"""调度引擎：加载→LLM分析→训练→评估→LLM解读→节点组装。

支持：
- 单/多模型统一调度
- 模型自动选优与对比节点（select_best）
- 超参数随机搜索（search/n_iter/cv）
- 回归/分类任务切换（task_type 校验与指标适配）
- LLM 训练前分析（一次）+ 训练后解读（按模型，可配置 scope）
- 运行参数节点（test_size / seed 可视化）
- 进度回调（on_step 回调函数，实时推送步骤状态）
"""

import json
import os
import warnings
from datetime import datetime
from typing import Callable, Optional, Union

import numpy as np
from sklearn.exceptions import NotFittedError
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, train_test_split

from .llm_analyzer import LLMAnalyzer
from .registry import get_model_class, get_dataset_class


def _evaluate(task_type: str, y_test, y_pred, y_proba=None) -> dict:
    """按任务类型计算评估指标。"""
    if task_type == "regression":
        return {
            "mse": float(mean_squared_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
        }
    elif task_type == "classification":
        result = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1": float(f1_score(y_test, y_pred, average="weighted")),
        }
        if y_proba is not None:
            try:
                classes = sorted(set(y_test))
                if len(classes) == 2:
                    result["auc"] = float(roc_auc_score(y_test, y_proba[:, 1]))
            except (ValueError, IndexError):
                pass
        return result
    else:
        raise ValueError(f"未知任务类型: {task_type}")


def _best_metric_key(task_type: str) -> str:
    return "r2" if task_type == "regression" else "f1"


def run(
    model_names: Union[str, list[str]],
    dataset_name: str,
    test_size: float = 0.2,
    seed: int = 42,
    select_best: bool = False,
    llm_post_scope: str = "all",
    search: bool = False,
    n_iter: int = 10,
    cv: int = 5,
    on_step: Callable[[dict], None] | None = None,
) -> dict:
    """统一调度入口。

    参数：
        model_names: 模型名（str）或模型名列表
        dataset_name: 数据集注册名
        test_size: 测试集比例
        seed: 随机种子
        select_best: 是否自动选优并生成对比节点
        llm_post_scope: 训练后 LLM 解读范围 "all" | "best"
        search: 是否启用超参搜索
        n_iter: RandomizedSearchCV 迭代次数
        cv: 交叉验证折数
        on_step: 进度回调，每步调用 on_step({"step": str, "status": str, "message": str, "data": ...})

    返回：
        {run_id, metrics, best_model, nodes, edges}
    """
    def _emit(step: str, status: str = "running", message: str = "", **extra):
        if on_step:
            on_step({"step": step, "status": status, "message": message, **extra})

    # ── 统一为列表 ────────────────────────────────────────
    if isinstance(model_names, str):
        model_names = [model_names]

    _emit("init", "running", f"启动流水线：模型={model_names}，数据集={dataset_name}")

    # ── 加载数据集 ────────────────────────────────────────
    _emit("dataset", "running", f"加载数据集 {dataset_name}...")
    dataset_cls = get_dataset_class(dataset_name)
    dataset = dataset_cls()
    X, y = dataset.load()
    data_summary = dataset.summary()
    task_type = dataset.task_type
    _emit("dataset", "success", f"数据集加载完成：{data_summary['n_samples']} 样本 × {data_summary['n_features']} 特征")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{dataset_name}"

    # ── E4-FR-3 任务类型校验 ──────────────────────────────
    for model_name in model_names:
        model_cls = get_model_class(model_name)
        if model_cls.task_type != task_type:
            _emit("init", "failed", f"任务类型不匹配：模型 '{model_name}' 是 {model_cls.task_type}，数据集是 {task_type}")
            raise ValueError(
                f"任务类型不匹配：模型 '{model_name}' 的 task_type="
                f"'{model_cls.task_type}' 与数据集 '{dataset_name}' 的 "
                f"task_type='{task_type}' 不一致"
            )
    model_task_types = {get_model_class(m).task_type for m in model_names}
    if len(model_task_types) > 1:
        _emit("init", "failed", f"混合任务类型: {model_task_types}")
        raise ValueError(f"模型列表包含混合任务类型: {model_task_types}")

    # ── LLM 初始化 ────────────────────────────────────────
    llm = LLMAnalyzer()
    if llm.available:
        _emit("llm_init", "success", f"LLM 就绪：provider={llm.provider}, model={llm.model}")
    else:
        _emit("llm_init", "skipped", "LLM 未配置，跳过所有 LLM 分析")

    # ── 节点 & 边 ─────────────────────────────────────────
    nodes: list[dict] = []
    edges: list[dict] = []

    # config 节点（运行参数）
    config_node_id = "config"
    nodes.append({
        "id": config_node_id,
        "type": "config",
        "label": "运行参数",
        "status": "success",
        "position": {"x": 0, "y": -120},
        "display": {
            "test_size": test_size,
            "seed": seed,
            "select_best": select_best,
            "search": search,
            "n_iter": n_iter if search else None,
            "cv": cv if search else None,
            "llm_provider": llm.provider or None,
            "llm_model": llm.model or None,
        },
    })

    # dataset 节点
    dataset_node_id = f"dataset-{dataset_name}"
    nodes.append({
        "id": dataset_node_id,
        "type": "dataset",
        "label": f"数据集: {dataset_name}",
        "status": "success",
        "position": {"x": 0, "y": 0},
        "display": {
            "n_samples": data_summary["n_samples"],
            "n_features": data_summary["n_features"],
            "feature_names": data_summary["feature_names"],
            "task_type": task_type,
        },
    })
    edges.append({"source": config_node_id, "target": dataset_node_id})

    # ── 训练前 LLM 分析（仅一次）──────────────────────────
    llm_pre_id = "llm_pre"
    if llm.available:
        _emit("llm_pre", "running", "训练前 LLM 分析中...", model_name=None)
        llm_pre_result = llm.analyze_data(data_summary)
    else:
        llm_pre_result = None

    if llm_pre_result is not None:
        nodes.append({
            "id": llm_pre_id,
            "type": "llm_analysis",
            "label": "训练前 LLM 分析",
            "status": "success",
            "position": {"x": 250, "y": 0},
            "display": {
                "stage": "pre_train",
                "model_name": None,
                "content": llm_pre_result["content"],
                "structured": llm_pre_result["structured"],
                "parse_failed": llm_pre_result["parse_failed"],
            },
        })
        edges.append({"source": dataset_node_id, "target": llm_pre_id})
        _emit("llm_pre", "success", "训练前 LLM 分析完成")
        _print_llm("训练前分析", llm_pre_result)
    else:
        reason = "未配置 LLM" if not llm.available else "调用失败"
        nodes.append({
            "id": llm_pre_id,
            "type": "llm_analysis",
            "label": "训练前 LLM 分析",
            "status": "skipped",
            "position": {"x": 250, "y": 0},
            "display": {
                "stage": "pre_train",
                "model_name": None,
                "content": "",
                "structured": None,
                "parse_failed": True,
            },
        })
        edges.append({"source": dataset_node_id, "target": llm_pre_id})
        _emit("llm_pre", "skipped", f"训练前 LLM 分析跳过（{reason}）")
        print(f"\n[LLM 训练前分析] 跳过（{reason}）")

    # ── 划分数据 ──────────────────────────────────────────
    _emit("split", "running", f"划分训练/测试集 (test_size={test_size}, seed={seed})...")
    stratify = y if task_type == "classification" else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=stratify
    )
    _emit("split", "success", f"训练集 {X_train.shape[0]} 样本，测试集 {X_test.shape[0]} 样本")

    # ── 逐模型训练评估 ────────────────────────────────────
    metrics: dict[str, dict[str, float]] = {}
    model_results: list[dict] = []
    n_models = len(model_names)
    model_y_spacing = 160

    for idx, model_name in enumerate(model_names):
        _emit("train", "running", f"训练模型 {model_name}...", model_name=model_name)
        model_cls = get_model_class(model_name)
        model = model_cls()

        model_node_id = f"model-{model_name}"
        metric_node_id = f"metric-{model_name}"
        llm_post_id = f"llm_post-{model_name}"

        y_offset = idx * model_y_spacing - (n_models - 1) * model_y_spacing // 2

        # ── E3: 超参搜索 ────────────────────────────────
        search_info = {"enabled": False, "n_iter": n_iter, "cv": cv, "best_score": None}
        try:
            param_space = model.param_space()
            if search and param_space:
                _emit("search", "running", f"超参搜索 {model_name} (n_iter={n_iter}, cv={cv})...", model_name=model_name)
                sk_estimator = getattr(model, "_model", model)
                scorer = "r2" if task_type == "regression" else "f1_weighted"
                search_cv = RandomizedSearchCV(
                    sk_estimator, param_space, n_iter=n_iter, cv=cv,
                    scoring=scorer, random_state=seed, n_jobs=-1,
                )
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    search_cv.fit(X_train, y_train)
                if hasattr(model, "_model"):
                    model._model = search_cv.best_estimator_
                else:
                    model = search_cv.best_estimator_
                search_info = {
                    "enabled": True, "n_iter": n_iter, "cv": cv,
                    "best_score": float(search_cv.best_score_),
                }
                _emit("search", "success", f"超参搜索完成: best_score={search_cv.best_score_:.4f}", model_name=model_name)
                print(f"\n[{model_name}] 超参搜索完成: best_score={search_cv.best_score_:.4f}")
            elif search and not param_space:
                search_info["enabled"] = False
                search_info["note"] = "param_space() 为空，跳过搜索"
        except Exception as e:
            search_info = {"enabled": False, "n_iter": n_iter, "cv": cv, "best_score": None, "error": str(e)}
            _emit("search", "failed", f"超参搜索异常: {e}", model_name=model_name)
            print(f"[{model_name}] 超参搜索异常，回退默认参数: {e}")
            model = model_cls()

        # 训练
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        y_proba = None
        if task_type == "classification":
            try:
                sk_est = getattr(model, "_model", model)
                if hasattr(sk_est, "predict_proba"):
                    y_proba = sk_est.predict_proba(X_test)
            except Exception:
                pass

        model_metrics = _evaluate(task_type, y_test, y_pred, y_proba)
        metrics[model_name] = model_metrics
        params = model.get_params()

        metric_str = "  ".join(f"{k}={v:.4f}" for k, v in model_metrics.items())
        _emit("train", "success", f"模型 {model_name} 完成: {metric_str}", model_name=model_name)
        print(f"\n[{model_name}] {metric_str}")

        model_display = {"model_name": model_name, "params": params}
        if search:
            model_display["search_info"] = search_info

        nodes.append({
            "id": model_node_id, "type": "model",
            "label": f"模型: {model_name}", "status": "success",
            "position": {"x": 500, "y": y_offset},
            "display": model_display,
        })
        edges.append({"source": llm_pre_id, "target": model_node_id})

        metric_display = {"model_name": model_name}
        metric_display.update(model_metrics)
        nodes.append({
            "id": metric_node_id, "type": "metric",
            "label": f"指标: {model_name}", "status": "success",
            "position": {"x": 750, "y": y_offset},
            "display": metric_display,
        })
        edges.append({"source": model_node_id, "target": metric_node_id})

        model_results.append({
            "model_name": model_name, "metrics": model_metrics,
            "llm_post_id": llm_post_id, "metric_node_id": metric_node_id,
            "y_offset": y_offset,
        })

    # ── E2: 自动选优 ──────────────────────────────────────
    best_model_name: Optional[str] = None
    if select_best and len(model_results) > 1:
        best_key = _best_metric_key(task_type)
        best_result = max(model_results, key=lambda r: r["metrics"][best_key])
        best_model_name = best_result["model_name"]

        comp_models = []
        for r in model_results:
            comp_models.append({
                "model_name": r["model_name"],
                **r["metrics"],
                "is_best": r["model_name"] == best_model_name,
            })

        comp_y = sum(r["y_offset"] for r in model_results) / len(model_results)
        comp_node_id = "comparison"
        nodes.append({
            "id": comp_node_id, "type": "comparison",
            "label": "模型对比", "status": "success",
            "position": {"x": 1000, "y": comp_y},
            "display": {"models": comp_models, "best_model": best_model_name},
        })
        for r in model_results:
            edges.append({"source": r["metric_node_id"], "target": comp_node_id})

        _emit("select_best", "success", f"最优模型: {best_model_name} ({best_key}={best_result['metrics'][best_key]:.4f})")
        print(f"\n▶ 最优模型: {best_model_name} ({best_key}={best_result['metrics'][best_key]:.4f})")

    # ── 训练后 LLM 解读 ────────────────────────────────────
    for r in model_results:
        model_name = r["model_name"]
        llm_post_id = r["llm_post_id"]
        metric_node_id = r["metric_node_id"]
        y_offset = r["y_offset"]

        if llm_post_scope == "best" and best_model_name and model_name != best_model_name:
            _emit("llm_post", "skipped", f"结果解读 {model_name} 跳过（scope=best）", model_name=model_name)
            print(f"[LLM 结果解读 {model_name}] 跳过（scope=best，非最优模型）")
            continue

        if llm.available:
            _emit("llm_post", "running", f"结果解读 {model_name} 中...", model_name=model_name)
            llm_post_result = llm.analyze_results(model_name, metrics[model_name], data_summary)
        else:
            llm_post_result = None

        post_x = 1250 if select_best and len(model_results) > 1 else 1000

        if llm_post_result is not None:
            nodes.append({
                "id": llm_post_id, "type": "llm_analysis",
                "label": f"结果解读: {model_name}", "status": "success",
                "position": {"x": post_x, "y": y_offset},
                "display": {
                    "stage": "post_train", "model_name": model_name,
                    "content": llm_post_result["content"],
                    "structured": llm_post_result["structured"],
                    "parse_failed": llm_post_result["parse_failed"],
                },
            })
            edges.append({"source": metric_node_id, "target": llm_post_id})
            _emit("llm_post", "success", f"结果解读 {model_name} 完成", model_name=model_name)
            _print_llm(f"结果解读 [{model_name}]", llm_post_result)
        else:
            reason = "未配置 LLM" if not llm.available else "调用失败"
            nodes.append({
                "id": llm_post_id, "type": "llm_analysis",
                "label": f"结果解读: {model_name}", "status": "skipped",
                "position": {"x": post_x, "y": y_offset},
                "display": {
                    "stage": "post_train", "model_name": model_name,
                    "content": "", "structured": None, "parse_failed": True,
                },
            })
            edges.append({"source": metric_node_id, "target": llm_post_id})
            _emit("llm_post", "skipped", f"结果解读 {model_name} 跳过（{reason}）", model_name=model_name)
            print(f"[LLM 结果解读 {model_name}] 跳过（{reason}）")

    # ── 组装结果 ──────────────────────────────────────────
    result = {
        "run_id": run_id, "metrics": metrics,
        "best_model": best_model_name, "nodes": nodes, "edges": edges,
    }

    # ── 写 nodes.json ─────────────────────────────────────
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    nodes_path = os.path.join(output_dir, "nodes.json")
    with open(nodes_path, "w", encoding="utf-8") as f:
        json.dump({"run_id": run_id, "nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)
    print(f"\n节点数据已写入: {nodes_path}")

    # ── E5: 持久化 ────────────────────────────────────────
    try:
        from .store import save_run
        save_run(result, dataset_name)
    except Exception as e:
        print(f"⚠ 数据库写入失败（不影响主流程）: {e}")

    _emit("done", "success", f"流水线完成 (run_id={run_id})")
    return result


def _print_llm(title: str, result: dict) -> None:
    print(f"\n{'='*60}")
    print(f"[LLM {title}]")
    print(f"{'='*60}")
    print(result["content"])
    if result["parse_failed"]:
        print("(JSON 解析失败，以上为原始文本)")
    print(f"{'='*60}")
