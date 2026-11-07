"""图执行引擎：基于节点+边的拓扑排序执行。

支持：
- 全图执行：按拓扑序执行所有节点
- 单节点执行：只执行目标节点及其上游依赖
- 数据缓存：每个节点的输出缓存在内存中，单节点执行时复用
- SSE 进度推送：每个节点的状态变化实时推送
"""

import json
import os
import traceback
from datetime import datetime
from typing import Callable, Optional
from collections import defaultdict, deque

import numpy as np
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, mean_squared_error, r2_score, roc_auc_score
)

from .registry import get_model_class, get_dataset_class
from .llm_analyzer import LLMAnalyzer


# ── 全局数据缓存 ────────────────────────────────────────
# key: node_id, value: {output: dict, display: dict, config: dict}
_data_cache: dict[str, dict] = {}


def get_cached_output(node_id: str) -> dict | None:
    return _data_cache.get(node_id)


def clear_cache():
    _data_cache.clear()


# ── 评估函数 ────────────────────────────────────────────
def _evaluate(task_type, y_test, y_pred, y_proba=None):
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
    raise ValueError(f"未知任务类型: {task_type}")


def _best_metric_key(task_type):
    return "r2" if task_type == "regression" else "f1"


# ── 拓扑排序 ────────────────────────────────────────────
def _topo_sort(nodes, edges):
    """Kahn's algorithm."""
    adj = defaultdict(list)
    in_deg = {n["id"]: 0 for n in nodes}
    node_map = {n["id"]: n for n in nodes}

    for e in edges:
        if e["source"] in in_deg and e["target"] in in_deg:
            adj[e["source"]].append(e["target"])
            in_deg[e["target"]] += 1

    queue = deque([nid for nid, d in in_deg.items() if d == 0])
    result = []
    while queue:
        nid = queue.popleft()
        result.append(node_map[nid])
        for tgt in adj[nid]:
            in_deg[tgt] -= 1
            if in_deg[tgt] == 0:
                queue.append(tgt)

    if len(result) < len(nodes):
        remaining = set(n["id"] for n in nodes) - set(r["id"] for r in result)
        raise ValueError(f"检测到环，涉及节点: {remaining}")
    return result


def _get_upstream_ids(node_id, edges):
    """获取节点的所有上游节点 ID（传递闭包）。"""
    all_upstream = set()
    queue = deque([node_id])
    while queue:
        nid = queue.popleft()
        for e in edges:
            if e["target"] == nid and e["source"] not in all_upstream:
                all_upstream.add(e["source"])
                queue.append(e["source"])
    return all_upstream


def _collect_inputs(node_id, edges, cache):
    """从上游节点的缓存输出中收集输入数据（支持端口级路由）。
    
    如果边携带 sourcePort/targetPort，则按端口映射：
        inputs[targetPort] = upstream_output[sourcePort]
    否则向后兼容（合并所有输出 key）。
    
    特殊情况：同一 targetPort 有多条连线时（如 comparison），
    收集为列表。
    """
    inputs = {}
    for e in edges:
        if e["target"] != node_id:
            continue
        cached = cache.get(e["source"])
        if not cached or "output" not in cached:
            continue
        source_port = e.get("sourcePort")
        target_port = e.get("targetPort")
        if source_port and target_port and source_port in cached["output"]:
            port_data = cached["output"][source_port]
            if target_port in inputs:
                if isinstance(inputs[target_port], list):
                    inputs[target_port].append(port_data)
                else:
                    inputs[target_port] = [inputs[target_port], port_data]
            else:
                inputs[target_port] = port_data
        else:
            inputs.update(cached["output"])
    return inputs


# ── 节点执行器 ──────────────────────────────────────────
def _exec_dataset(node, inputs, llm=None):
    cfg = node.get("config", {})
    ds_name = cfg.get("dataset_name", "diabetes")
    ds_class = get_dataset_class(ds_name)
    ds = ds_class()
    X, y = ds.load()
    summary = ds.summary()
    output = {"data": {"X": X, "y": y, "task_type": ds.task_type, "feature_names": ds.feature_names(), "data_summary": summary}}
    display = {"n_samples": summary["n_samples"], "n_features": summary["n_features"], "task_type": ds.task_type}
    return output, display


def _exec_csv_upload(node, inputs, llm=None):
    cfg = node.get("config", {})
    ds_name = cfg.get("dataset_name", "csv_data")
    ds_class = get_dataset_class(ds_name)
    ds = ds_class()
    X, y = ds.load()
    summary = ds.summary()
    output = {"data": {"X": X, "y": y, "task_type": ds.task_type, "feature_names": ds.feature_names(), "data_summary": summary}}
    display = {"n_samples": summary["n_samples"], "n_features": summary["n_features"], "task_type": ds.task_type}
    return output, display


def _exec_data_analysis(node, inputs, llm=None):
    data = inputs.get("data", {})
    summary = data.get("data_summary", {})
    output = {"summary": summary}
    display = summary
    return output, display


def _exec_split(node, inputs, llm=None):
    cfg = node.get("config", {})
    data = inputs.get("data", {})
    X, y = data["X"], data["y"]
    test_size = float(cfg.get("test_size", 0.2))
    seed = int(cfg.get("seed", 42))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)
    task_type = data.get("task_type", "regression")
    output = {
        "train": {"X": X_train, "y": y_train, "task_type": task_type},
        "test": {"X": X_test, "y": y_test, "task_type": task_type},
    }
    display = {"train_size": len(X_train), "test_size": len(X_test), "test_ratio": test_size, "seed": seed}
    return output, display


def _exec_model(node, inputs, llm=None):
    cfg = node.get("config", {})
    train = inputs.get("train", {})
    test = inputs.get("test", {})
    model_name = cfg.get("model_name", "linear_regression")
    model_class = get_model_class(model_name)
    model = model_class()
    model.fit(train["X"], train["y"])
    y_pred = model.predict(test["X"])
    task_type = train.get("task_type", "regression")
    output = {"model": {"model": model, "y_pred": y_pred, "y_test": test["y"], "model_name": model_name, "task_type": task_type, "params": model.get_params()}}
    display = {"model_name": model_name, "params": model.get_params()}
    return output, display


def _exec_search(node, inputs, llm=None):
    cfg = node.get("config", {})
    train = inputs.get("train", {})
    test = inputs.get("test", {})
    model_name = cfg.get("model_name", "linear_regression")
    model_class = get_model_class(model_name)
    base_model = model_class()
    param_space = base_model.param_space()
    n_iter = int(cfg.get("n_iter", 10))
    cv = int(cfg.get("cv", 5))
    task_type = train.get("task_type", "regression")

    if not param_space:
        base_model.fit(train["X"], train["y"])
        y_pred = base_model.predict(test["X"])
        output = {"model": {"model": base_model, "y_pred": y_pred, "y_test": test["y"], "model_name": model_name, "task_type": task_type, "params": base_model.get_params(), "search_info": {"note": "无搜索空间，使用默认参数"}}}
        display = {"model_name": model_name, "params": base_model.get_params(), "search": "无搜索空间"}
        return output, display

    search = RandomizedSearchCV(base_model._model if hasattr(base_model, "_model") else base_model, param_space, n_iter=n_iter, cv=cv, random_state=42)
    search.fit(train["X"], train["y"])
    y_pred = search.predict(test["X"])
    output = {"model": {"model": search.best_estimator_, "y_pred": y_pred, "y_test": test["y"], "model_name": model_name, "task_type": task_type, "params": search.best_params_, "search_info": {"best_params": search.best_params_, "best_score": float(search.best_score_)}}}
    display = {"model_name": model_name, "params": search.best_params_, "search": f"best_score={search.best_score_:.4f}"}
    return output, display


def _exec_metric(node, inputs, llm=None):
    model_data = inputs.get("model", {})
    task_type = model_data.get("task_type", "regression")
    y_test = model_data["y_test"]
    y_pred = model_data["y_pred"]
    metrics = _evaluate(task_type, y_test, y_pred)
    model_name = model_data.get("model_name", "")
    output = {"metrics": {"metrics": metrics, "model_name": model_name, "task_type": task_type}}
    display = metrics
    return output, display


def _exec_llm_pre(node, inputs, llm=None):
    if not llm or not llm.available:
        output = {"analysis": {"content": "", "structured": None, "parse_failed": True, "stage": "pre_train"}}
        display = {"content": "", "stage": "pre_train"}
        return output, display
    data = inputs.get("data", {})
    result = llm.analyze_data(data.get("data_summary", {}))
    output = {"analysis": {"content": result["content"], "structured": result["structured"], "parse_failed": result["parse_failed"], "stage": "pre_train"}}
    display = {"content": result["content"][:200], "stage": "pre_train"}
    return output, display


def _exec_llm_post(node, inputs, llm=None):
    metrics_data = inputs.get("metrics", {})
    data_data = inputs.get("data", {})
    model_name = metrics_data.get("model_name", "")
    metrics = metrics_data.get("metrics", {})
    data_summary = data_data.get("data_summary", {})
    if not llm or not llm.available:
        output = {"interpretation": {"content": "", "structured": None, "parse_failed": True, "stage": "post_train", "model_name": model_name}}
        display = {"content": "", "stage": "post_train"}
        return output, display
    result = llm.analyze_results(model_name, metrics, data_summary)
    output = {"interpretation": {"content": result["content"], "structured": result["structured"], "parse_failed": result["parse_failed"], "stage": "post_train", "model_name": model_name}}
    display = {"content": result["content"][:200], "stage": "post_train", "model_name": model_name}
    return output, display


def _exec_output(node, inputs, llm=None):
    output = {"saved": True}
    display = {"saved": True}
    return output, display


# 执行器注册表
EXECUTORS = {
    "dataset": _exec_dataset,
    "csv_upload": _exec_csv_upload,
    "data_analysis": _exec_data_analysis,
    "split": _exec_split,
    "model": _exec_model,
    "search": _exec_search,
    "metric": _exec_metric,
    "llm_pre": _exec_llm_pre,
    "llm_post": _exec_llm_post,
    "output": _exec_output,
}


# ── 图执行主函数 ────────────────────────────────────────
def run_graph(nodes_data, edges_data, target_node_id=None, on_step=None, llm=None, use_cache=True):
    """
    执行流程图。

    参数:
        nodes_data: [{id, type, config, ...}]  画布上的节点列表
        edges_data: [{source, target}]          画布上的边列表
        target_node_id: 如果指定，只执行该节点及其上游
        on_step: 回调函数，推送步骤状态
        llm: LLMAnalyzer 实例
        use_cache: 是否使用缓存（单节点执行时复用上游结果）

    返回:
        {run_id, node_displays, metrics, best_model}
    """
    def _emit(step, status, message, **kwargs):
        if on_step:
            on_step({"step": step, "status": status, "message": message, **kwargs})

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 确定要执行的节点
    if target_node_id:
        upstream_ids = _get_upstream_ids(target_node_id, edges_data)
        exec_node_ids = upstream_ids | {target_node_id}
        exec_nodes = [n for n in nodes_data if n["id"] in exec_node_ids]
    else:
        exec_nodes = list(nodes_data)

    # 拓扑排序
    try:
        sorted_nodes = _topo_sort(exec_nodes, edges_data)
    except ValueError as e:
        _emit("error", "failed", str(e))
        return {"run_id": run_id, "error": str(e), "node_displays": {}, "metrics": {}, "best_model": None}

    # 执行
    metrics = {}
    model_results = []
    node_displays = {}

    for node in sorted_nodes:
        node_id = node["id"]
        node_type = node["type"]
        node_label = node.get("label", node_type)

        # 如果已有缓存且不是目标节点，跳过
        if use_cache and target_node_id and node_id != target_node_id and node_id in _data_cache:
            cached = _data_cache[node_id]
            node_displays[node_id] = cached.get("display", {})
            _emit(node_type, "skipped", f"{node_label} (已缓存)", node_id=node_id)
            continue

        executor = EXECUTORS.get(node_type)
        if not executor:
            _emit(node_type, "skipped", f"未知节点类型: {node_type}", node_id=node_id)
            continue

        # 收集上游输入
        inputs = _collect_inputs(node_id, edges_data, _data_cache)

        _emit(node_type, "running", f"执行 {node_label}...", node_id=node_id)

        try:
            # 特殊处理 comparison 节点：从所有上游 metric 节点收集结果
            if node_type == "comparison":
                upstream_edges = [e for e in edges_data if e["target"] == node_id]
                all_metrics = []
                for e in upstream_edges:
                    cached = _data_cache.get(e["source"])
                    if cached and "output" in cached:
                        source_port = e.get("sourcePort", "metrics")
                        if source_port in cached["output"]:
                            port_data = cached["output"][source_port]
                            all_metrics.append(port_data)
                        else:
                            all_metrics.append(cached["output"])

                if all_metrics:
                    task_type = all_metrics[0].get("task_type", "regression")
                    best_key = _best_metric_key(task_type)
                    best = max(all_metrics, key=lambda r: r["metrics"][best_key])
                    comp_models = []
                    for r in all_metrics:
                        comp_models.append({
                            "model_name": r["model_name"],
                            **r["metrics"],
                            "is_best": r["model_name"] == best["model_name"],
                        })
                    output = {"comparison": {"models": comp_models, "best_model": best["model_name"]}}
                    display = {"models": comp_models, "best_model": best["model_name"]}
                    metrics = {r["model_name"]: r["metrics"] for r in all_metrics}
                else:
                    output = {"comparison": {"models": [], "best_model": None}}
                    display = {"models": [], "best_model": None}
            else:
                output, display = executor(node, inputs, llm=llm)

            # 缓存输出
            _data_cache[node_id] = {"output": output, "display": display, "config": node.get("config", {})}
            node_displays[node_id] = display

            # 收集 metrics
            if node_type == "metric":
                metrics_data = output.get("metrics", {})
                model_name = metrics_data.get("model_name", "")
                metrics[model_name] = metrics_data.get("metrics", {})
                model_results.append({"node_id": node_id, "model_name": model_name, "metrics": metrics_data.get("metrics", {}), "task_type": metrics_data.get("task_type", "regression")})

            _emit(node_type, "success", f"{node_label} 完成", node_id=node_id, display=display)

        except Exception as e:
            _emit(node_type, "failed", f"{node_label} 失败: {e}", node_id=node_id)
            traceback.print_exc()
            return {
                "run_id": run_id, "error": str(e),
                "node_displays": node_displays, "metrics": metrics, "best_model": None,
            }

    # 确定最优模型
    best_model = None
    if model_results:
        task_type = model_results[0].get("task_type", "regression")
        best_key = _best_metric_key(task_type)
        best = max(model_results, key=lambda r: r["metrics"][best_key])
        best_model = best["model_name"]

    _emit("done", "success", f"流水线完成 (run_id={run_id})")

    return {
        "run_id": run_id,
        "node_displays": node_displays,
        "metrics": metrics,
        "best_model": best_model,
        "nodes": [],
        "edges": [],
    }
