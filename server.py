"""Loom Web 服务器：提供 API + SSE 流式进度 + 静态前端页面。"""

import io
import json
import os
import sys
import traceback
from contextlib import redirect_stdout

from flask import Flask, Response, jsonify, request, send_from_directory

# 确保包可导入，动态推导包名
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PKG = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

from importlib import import_module
_core = import_module(f"{_PKG}.core")
run = _core.run
run_graph = _core.run_graph
clear_cache = _core.clear_cache
list_models = _core.list_models
list_datasets = _core.list_datasets
list_runs = _core.store.list_runs
get_run = _core.store.get_run
_datasets_mod = import_module(f"{_PKG}.datasets.csv_loader")
register_csv_dataset = _datasets_mod.register_csv_dataset

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "web"), static_url_path="")

# 全局存储最近一次运行结果，供 chat 引用
last_result_store = {}

# 存储上传的 CSV 文件路径
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/models")
def api_models():
    task_type = request.args.get("task_type")
    return jsonify({"models": list_models(task_type=task_type)})


@app.route("/api/datasets")
def api_datasets():
    task_type = request.args.get("task_type")
    return jsonify({"datasets": list_datasets(task_type=task_type)})


@app.route("/api/dataset/<name>/preview")
def api_dataset_preview(name):
    """返回数据集预览和统计分析。"""
    try:
        ds_cls = _core.get_dataset_class(name)
        ds = ds_cls()
        X, y = ds.load()
        feat_names = ds.feature_names()

        import numpy as np
        # 前 10 行预览
        preview = []
        for i in range(min(10, X.shape[0])):
            row = {fn: float(X[i][j]) for j, fn in enumerate(feat_names)}
            row["_target"] = float(y[i])
            preview.append(row)

        # 特征统计
        feature_stats = []
        for j, fn in enumerate(feat_names):
            col = X[:, j]
            feature_stats.append({
                "name": fn,
                "mean": float(np.mean(col)),
                "std": float(np.std(col)),
                "min": float(np.min(col)),
                "max": float(np.max(col)),
                "median": float(np.median(col)),
                "missing": int(np.isnan(col).sum()),
            })

        # 目标统计
        target_stats = {
            "mean": float(np.mean(y)),
            "std": float(np.std(y)),
            "min": float(np.min(y)),
            "max": float(np.max(y)),
            "median": float(np.median(y)),
        }

        # 相关性（目标与各特征）
        correlations = []
        for j, fn in enumerate(feat_names):
            if np.std(X[:, j]) > 0 and np.std(y) > 0:
                corr = float(np.corrcoef(X[:, j], y)[0, 1])
            else:
                corr = 0.0
            correlations.append({"feature": fn, "correlation": corr})

        # 按相关性绝对值排序
        correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return jsonify({
            "status": "success",
            "n_samples": X.shape[0],
            "n_features": X.shape[1],
            "feature_names": feat_names,
            "task_type": ds.task_type,
            "preview": preview,
            "feature_stats": feature_stats,
            "target_stats": target_stats,
            "correlations": correlations,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"{type(e).__name__}: {e}"}), 404


@app.route("/api/upload_csv", methods=["POST"])
def api_upload_csv():
    """上传 CSV 文件，返回列名供用户选择目标列。"""
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "没有文件"}), 400
    f = request.files["file"]
    if not f.filename.endswith(".csv"):
        return jsonify({"status": "error", "message": "仅支持 .csv 文件"}), 400

    filepath = os.path.join(UPLOAD_DIR, f.filename)
    f.save(filepath)

    import pandas as pd
    df = pd.read_csv(filepath)
    return jsonify({
        "status": "success",
        "filepath": filepath,
        "columns": list(df.columns),
        "n_rows": len(df),
        "preview": df.head(5).to_dict(orient="records"),
    })


@app.route("/api/run_stream", methods=["POST"])
def api_run_stream():
    """SSE 流式运行流水线，实时推送步骤进度。"""
    data = request.json or {}

    model_names = data.get("model_names", "linear_regression")
    dataset_name = data.get("dataset_name", "diabetes")
    test_size = float(data.get("test_size", 0.2))
    seed = int(data.get("seed", 42))
    select_best = bool(data.get("select_best", False))
    llm_post_scope = data.get("llm_post_scope", "all")
    search = bool(data.get("search", False))
    n_iter = int(data.get("n_iter", 10))
    cv = int(data.get("cv", 5))
    steps = data.get("steps", {})

    # LLM 配置
    llm_provider = data.get("llm_provider", "").strip()
    llm_api_key = data.get("llm_api_key", "").strip()
    llm_base_url = data.get("llm_base_url", "").strip()
    llm_model = data.get("llm_model", "").strip()
    llm_timeout = data.get("llm_timeout", "")

    if llm_provider:
        os.environ["AUTOML_LLM_PROVIDER"] = llm_provider
    if llm_api_key:
        os.environ["AUTOML_LLM_API_KEY"] = llm_api_key
    if llm_base_url:
        os.environ["AUTOML_LLM_BASE_URL"] = llm_base_url
    if llm_model:
        os.environ["AUTOML_LLM_MODEL"] = llm_model
    if llm_timeout:
        os.environ["AUTOML_LLM_TIMEOUT"] = str(llm_timeout)

    # CSV 数据集
    csv_config = data.get("csv_config")
    if csv_config:
        register_csv_dataset(
            name=csv_config["name"],
            csv_path=csv_config["filepath"],
            target_column=csv_config["target_column"],
            task_type=csv_config.get("task_type", "regression"),
        )
        dataset_name = csv_config["name"]

    def generate():
        import queue
        import threading

        q = queue.Queue()
        log_lines = []

        def on_step(step_data):
            log_lines.append(f"[{step_data['step']}] {step_data['status']}: {step_data['message']}")
            q.put(("step", step_data))

        def run_in_thread():
            try:
                result = run(
                    model_names=model_names,
                    dataset_name=dataset_name,
                    test_size=test_size,
                    seed=seed,
                    select_best=select_best,
                    llm_post_scope=llm_post_scope,
                    search=search,
                    n_iter=n_iter,
                    cv=cv,
                    steps=steps,
                    on_step=on_step,
                )
                q.put(("done", result))
            except Exception as e:
                q.put(("error", f"{type(e).__name__}: {e}"))

        t = threading.Thread(target=run_in_thread, daemon=True)
        t.start()

        while True:
            try:
                kind, data = q.get(timeout=600)
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'error', 'message': '超时（10分钟无响应）'})}\n\n"
                break

            if kind == "step":
                yield f"data: {json.dumps({'type': 'step', **data})}\n\n"
            elif kind == "done":
                last_result_store["result"] = data
                yield f"data: {json.dumps({'type': 'done', 'run_id': data['run_id'], 'metrics': data['metrics'], 'best_model': data.get('best_model'), 'nodes': data['nodes'], 'edges': data['edges'], 'log': '\\n'.join(log_lines)})}\n\n"
                break
            elif kind == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data, 'log': '\\n'.join(log_lines)})}\n\n"
                break

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/run_graph", methods=["POST"])
def api_run_graph():
    """图执行 SSE：接受画布节点+边，按拓扑序执行，实时推送进度。

    请求体:
        nodes: [{id, type, config, ...}]     画布节点列表
        edges: [{source, target}]             画布边列表
        target_node_id: str | None           单节点执行时指定
        clear_cache: bool                    是否清空缓存
        llm_provider / llm_api_key / ...     LLM 配置
        csv_config: dict | None              CSV 数据集配置
    """
    data = request.json or {}
    nodes_data = data.get("nodes", [])
    edges_data = data.get("edges", [])
    target_node_id = data.get("target_node_id")
    do_clear_cache = data.get("clear_cache", False)

    # LLM 配置
    llm_provider = data.get("llm_provider", "").strip()
    llm_api_key = data.get("llm_api_key", "").strip()
    llm_base_url = data.get("llm_base_url", "").strip()
    llm_model = data.get("llm_model", "").strip()
    llm_timeout = data.get("llm_timeout", "")

    if llm_provider:
        os.environ["AUTOML_LLM_PROVIDER"] = llm_provider
    if llm_api_key:
        os.environ["AUTOML_LLM_API_KEY"] = llm_api_key
    if llm_base_url:
        os.environ["AUTOML_LLM_BASE_URL"] = llm_base_url
    if llm_model:
        os.environ["AUTOML_LLM_MODEL"] = llm_model
    if llm_timeout:
        os.environ["AUTOML_LLM_TIMEOUT"] = str(llm_timeout)

    # CSV 数据集注册
    csv_config = data.get("csv_config")
    if csv_config:
        register_csv_dataset(
            name=csv_config["name"],
            csv_path=csv_config["filepath"],
            target_column=csv_config["target_column"],
            task_type=csv_config.get("task_type", "regression"),
        )

    if do_clear_cache:
        clear_cache()

    def generate():
        import queue
        import threading

        q = queue.Queue()
        log_lines = []

        def on_step(step_data):
            log_lines.append(f"[{step_data['step']}] {step_data['status']}: {step_data['message']}")
            q.put(("step", step_data))

        def run_in_thread():
            try:
                llm = LLMAnalyzer()
                result = run_graph(
                    nodes_data=nodes_data,
                    edges_data=edges_data,
                    target_node_id=target_node_id,
                    on_step=on_step,
                    llm=llm,
                )
                q.put(("done", result))
            except Exception as e:
                import traceback as tb
                tb.print_exc()
                q.put(("error", f"{type(e).__name__}: {e}"))

        t = threading.Thread(target=run_in_thread, daemon=True)
        t.start()

        while True:
            try:
                kind, data = q.get(timeout=600)
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'error', 'message': '超时（10分钟无响应）'})}\n\n"
                break

            if kind == "step":
                yield f"data: {json.dumps({'type': 'step', **data})}\n\n"
            elif kind == "done":
                last_result_store["result"] = data
                yield f"data: {json.dumps({'type': 'done', 'run_id': data['run_id'], 'metrics': data.get('metrics', {}), 'best_model': data.get('best_model'), 'node_displays': data.get('node_displays', {}), 'log': '\\n'.join(log_lines)})}\n\n"
                break
            elif kind == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data, 'log': '\\n'.join(log_lines)})}\n\n"
                break

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/clear_cache", methods=["POST"])
def api_clear_cache():
    """清空节点缓存。"""
    clear_cache()
    return jsonify({"status": "success", "message": "缓存已清空"})


@app.route("/api/history")
def api_history():
    limit = int(request.args.get("limit", 20))
    dataset_name = request.args.get("dataset_name")
    runs = list_runs(dataset_name=dataset_name, limit=limit)
    return jsonify({"runs": runs})


@app.route("/api/run/<run_id>")
def api_get_run(run_id):
    try:
        detail = get_run(run_id)
        return jsonify({"status": "success", "data": detail})
    except KeyError as e:
        return jsonify({"status": "error", "message": str(e)}), 404


@app.route("/api/run/<run_id>/nodes")
def api_get_run_nodes(run_id):
    """返回某次运行的完整 nodes/edges，用于历史回看。"""
    import sqlite3, json as _json
    _store = import_module(f"{_PKG}.core.store")
    db_path = _store._db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not row:
            return jsonify({"status": "error", "message": "run_id 不存在"}), 404
        nodes = _json.loads(row["nodes"]) if row["nodes"] else []
        edges = _json.loads(row["edges"]) if row["edges"] else []
        return jsonify({
            "status": "success",
            "run_id": run_id,
            "dataset_name": row["dataset_name"],
            "best_model": row["best_model"],
            "timestamp": row["timestamp"],
            "nodes": nodes,
            "edges": edges,
        })
    finally:
        conn.close()


@app.route("/api/config")
def api_config():
    provider = os.environ.get("AUTOML_LLM_PROVIDER", "")
    api_key = os.environ.get("AUTOML_LLM_API_KEY", "")
    return jsonify({
        "provider": provider,
        "has_api_key": bool(api_key),
        "api_key_preview": api_key[:8] + "..." if len(api_key) > 8 else "",
        "base_url": os.environ.get("AUTOML_LLM_BASE_URL", ""),
        "model": os.environ.get("AUTOML_LLM_MODEL", ""),
        "timeout": os.environ.get("AUTOML_LLM_TIMEOUT", "30"),
    })


# ── 代码查看与编辑 ─────────────────────────────────────
@app.route("/api/code")
def api_list_code():
    """列出所有可查看的源码文件。"""
    import glob
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = []
    for pattern in ["core/*.py", "models/*.py", "datasets/*.py", "*.py"]:
        for f in sorted(glob.glob(os.path.join(base_dir, pattern))):
            rel = os.path.relpath(f, base_dir)
            size = os.path.getsize(f)
            files.append({"path": rel, "size": size})
    return jsonify({"files": files})


@app.route("/api/code/<path:filepath>")
def api_get_code(filepath):
    """获取源码文件内容。"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    # 安全检查：不允许路径穿越
    if not os.path.realpath(full_path).startswith(os.path.realpath(base_dir)):
        return jsonify({"status": "error", "message": "路径不合法"}), 403
    if not os.path.isfile(full_path):
        return jsonify({"status": "error", "message": "文件不存在"}), 404
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({
            "status": "success",
            "path": filepath,
            "content": content,
            "size": len(content),
            "lines": content.count("\n") + 1,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/code/<path:filepath>", methods=["PUT"])
def api_save_code(filepath):
    """保存修改后的源码。"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    if not os.path.realpath(full_path).startswith(os.path.realpath(base_dir)):
        return jsonify({"status": "error", "message": "路径不合法"}), 403
    if not os.path.isfile(full_path):
        return jsonify({"status": "error", "message": "文件不存在"}), 404
    data = request.json or {}
    content = data.get("content", "")
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return jsonify({
            "status": "success",
            "path": filepath,
            "message": "保存成功（热加载会自动重启）",
            "size": len(content),
            "lines": content.count("\n") + 1,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/llm_test", methods=["POST"])
def api_llm_test():
    """测试 LLM 连通性。"""
    data = request.json or {}
    provider = data.get("provider", "").strip().lower()
    api_key = data.get("api_key", "").strip()
    base_url = data.get("base_url", "").strip()
    model = data.get("model", "").strip()
    timeout = int(data.get("timeout", 30))

    if not provider:
        return jsonify({"status": "error", "message": "未指定 provider"})

    # provider 默认值
    defaults = {
        "deepseek": {"base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
        "ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen2.5:7b"},
    }
    if not base_url:
        base_url = defaults.get(provider, {}).get("base_url", "")
    if not model:
        model = defaults.get(provider, {}).get("model", "")
    if not api_key and provider == "ollama":
        api_key = "ollama-placeholder"
    if not api_key and provider == "deepseek":
        return jsonify({"status": "error", "message": "DeepSeek 需要 API Key"})

    try:
        from openai import OpenAI
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "请回复'连接成功'四个字。"}],
            max_tokens=20,
        )
        reply = resp.choices[0].message.content.strip()
        return jsonify({
            "status": "success",
            "message": f"连接成功！模型回复: {reply}",
            "provider": provider,
            "model": model,
            "base_url": base_url,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"连接失败: {type(e).__name__}: {e}"})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """与大模型对话，可附带项目上下文（代码/模型/结果）。"""
    data = request.json or {}
    messages = data.get("messages", [])
    provider = data.get("provider", "").strip().lower()
    api_key = data.get("api_key", "").strip()
    base_url = data.get("base_url", "").strip()
    model = data.get("model", "").strip()
    timeout = int(data.get("timeout", 60))

    # 注入环境变量（复用 runner 的 LLM 配置）
    if provider:
        os.environ["AUTOML_LLM_PROVIDER"] = provider
    if api_key:
        os.environ["AUTOML_LLM_API_KEY"] = api_key
    if base_url:
        os.environ["AUTOML_LLM_BASE_URL"] = base_url
    if model:
        os.environ["AUTOML_LLM_MODEL"] = model
    if timeout:
        os.environ["AUTOML_LLM_TIMEOUT"] = str(timeout)

    # 构建系统上下文
    context_parts = []

    # 是否附带代码上下文
    include_code = data.get("include_code", False)
    if include_code:
        import glob
        code_files = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for pattern in ["core/*.py", "models/*.py", "datasets/*.py"]:
            for f in sorted(glob.glob(os.path.join(base_dir, pattern))):
                rel = os.path.relpath(f, base_dir)
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        content = fh.read()
                    code_files.append(f"### {rel}\n```python\n{content}\n```")
                except Exception:
                    pass
        if code_files:
            context_parts.append("以下是项目代码：\n\n" + "\n\n".join(code_files))

    # 是否附带运行结果
    include_results = data.get("include_results", False)
    if include_results and last_result_store.get("result"):
        r = last_result_store["result"]
        context_parts.append(
            f"最近一次运行结果：\nrun_id: {r['run_id']}\n"
            f"metrics: {json.dumps(r['metrics'], ensure_ascii=False)}\n"
            f"best_model: {r.get('best_model')}\n"
            f"nodes: {json.dumps(r['nodes'], ensure_ascii=False)[:3000]}"
        )

    # 模型与数据集列表
    context_parts.append(
        f"可用模型: {list_models()}\n"
        f"可用数据集: {list_datasets()}"
    )

    system_prompt = (
        "你是 Loom AutoML 框架的 AI 助手。你可以：\n"
        "1. 回答关于项目代码、模型、数据集、运行结果的问题\n"
        "2. 根据用户需求建议合适的模型和数据集组合\n"
        "3. 生成 Python 代码片段供用户执行\n"
        "4. 分析训练结果并给出改进建议\n\n"
        + "\n\n".join(context_parts)
    )

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        from openai import OpenAI
        defaults = {
            "deepseek": {"base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
            "ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen2.5:7b"},
        }
        prov = provider or os.environ.get("AUTOML_LLM_PROVIDER", "").strip().lower()
        if not base_url:
            base_url = os.environ.get("AUTOML_LLM_BASE_URL", "") or defaults.get(prov, {}).get("base_url", "")
        if not model:
            model = os.environ.get("AUTOML_LLM_MODEL", "") or defaults.get(prov, {}).get("model", "")
        if not api_key:
            api_key = os.environ.get("AUTOML_LLM_API_KEY", "")
        if not api_key and prov == "ollama":
            api_key = "ollama-placeholder"

        if not prov or not base_url or not model:
            return jsonify({"status": "error", "message": "LLM 未配置，请先填写 provider / model"})

        client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
        resp = client.chat.completions.create(
            model=model,
            messages=full_messages,
            max_tokens=4096,
            stream=True,
        )

        def generate():
            for chunk in resp:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': text})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({"status": "error", "message": f"LLM 调用失败: {type(e).__name__}: {e}"}), 500


def main():
    port = int(os.environ.get("LOOM_PORT", 8899))
    print(f"Loom Web 控制台启动中...")
    print(f"访问 http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
