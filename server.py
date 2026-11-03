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
list_models = _core.list_models
list_datasets = _core.list_datasets
list_runs = _core.store.list_runs
get_run = _core.store.get_run
_datasets_mod = import_module(f"{_PKG}.datasets.csv_loader")
register_csv_dataset = _datasets_mod.register_csv_dataset

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "web"), static_url_path="")

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
                    on_step=on_step,
                )
                q.put(("done", result))
            except Exception as e:
                q.put(("error", f"{type(e).__name__}: {e}"))

        t = threading.Thread(target=run_in_thread, daemon=True)
        t.start()

        while True:
            try:
                kind, data = q.get(timeout=300)
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'error', 'message': '超时（5分钟无响应）'})}\n\n"
                break

            if kind == "step":
                yield f"data: {json.dumps({'type': 'step', **data})}\n\n"
            elif kind == "done":
                yield f"data: {json.dumps({'type': 'done', 'run_id': data['run_id'], 'metrics': data['metrics'], 'best_model': data.get('best_model'), 'nodes': data['nodes'], 'edges': data['edges'], 'log': '\\n'.join(log_lines)})}\n\n"
                break
            elif kind == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data, 'log': '\\n'.join(log_lines)})}\n\n"
                break

    return Response(generate(), mimetype="text/event-stream")


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


def main():
    port = int(os.environ.get("LOOM_PORT", 5000))
    print(f"Loom Web 控制台启动中...")
    print(f"访问 http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
