# API 文档

## 模型与数据集

### GET /api/models
列出已注册模型。

**参数**：`task_type`（可选，过滤回归/分类）

**响应**：
```json
{"models": ["linear_regression", "random_forest", "ridge", "logistic_regression"]}
```

### GET /api/datasets
列出已注册数据集。

### GET /api/dataset/\<name\>/preview
返回数据集预览和统计分析。

**响应**：
```json
{
  "status": "success",
  "n_samples": 442,
  "n_features": 10,
  "feature_names": ["age", "sex", ...],
  "task_type": "regression",
  "preview": [{"age": 0.038, ..., "_target": 151.0}, ...],
  "feature_stats": [{"name": "age", "mean": 0.0, "std": 0.048, ...}, ...],
  "target_stats": {"mean": 152.13, "std": 77.01, ...},
  "correlations": [{"feature": "bmi", "correlation": 0.586}, ...]
}
```

## 运行流水线

### POST /api/run_stream
SSE 流式运行，实时推送步骤进度。

**请求体**：
```json
{
  "model_names": ["linear_regression", "random_forest"],
  "dataset_name": "diabetes",
  "test_size": 0.2,
  "seed": 42,
  "select_best": true,
  "llm_post_scope": "all",
  "search": false,
  "n_iter": 10,
  "cv": 5,
  "llm_provider": "ollama",
  "llm_api_key": "placeholder",
  "llm_base_url": "",
  "llm_model": "qwen3.5:4b",
  "llm_timeout": "120"
}
```

**SSE 事件**：
```
data: {"type": "step", "step": "train", "status": "running", "message": "训练模型..."}
data: {"type": "step", "step": "train", "status": "success", "message": "完成: r2=0.4526"}
data: {"type": "done", "run_id": "...", "nodes": [...], "edges": [...], "metrics": {...}}
```

## LLM

### POST /api/llm_test
测试 LLM 连通性。

### POST /api/chat
流式对话（SSE），支持附带代码和结果上下文。

## 代码

### GET /api/code
列出所有源码文件。

### GET /api/code/\<path\>
获取文件内容。

### PUT /api/code/\<path\>
保存修改后的内容。

## 历史

### GET /api/history
列出历史运行记录。

### GET /api/run/\<run_id\>
查询单次运行详情。

### GET /api/run/\<run_id\>/nodes
返回完整 nodes/edges，用于历史回看。

## CSV 上传

### POST /api/upload_csv
上传 CSV 文件，返回列名和预览。

### POST /api/register_csv
注册 CSV 数据集。
