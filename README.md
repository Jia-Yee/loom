# Loom — 可扩展 Loom AutoML 框架

一个可扩展的自动化机器学习框架，支持模型/数据集增量注册、多模型调度、LLM 智能分析、超参搜索、分类任务、结果持久化，以及 Web 控制台可视化。

---

## 目录

- [功能概览](#功能概览)
- [项目结构](#项目结构)
- [环境要求](#环境要求)
- [安装](#安装)
- [启动](#启动)
- [Web 控制台使用指南](#web-控制台使用指南)
- [命令行使用指南](#命令行使用指南)
- [LLM 配置](#llm-配置)
- [扩展：添加新模型](#扩展添加新模型)
- [扩展：添加新数据集](#扩展添加新数据集)
- [API 接口文档](#api-接口文档)
- [运行示例](#运行示例)

---

## 功能概览

| 模块 | 说明 |
|------|------|
| 注册机制 | `@register_model` / `@register_dataset` 装饰器，新增项无需改 core/ |
| 多模型调度 | `run()` 接受 str 或 list，统一返回结构 |
| LLM 分析 | DeepSeek / Ollama 双 provider，训练前数据分析 + 训练后结果解读 |
| 原始文本容错 | LLM 返回纯文本时保留原文展示，JSON 解析失败不丢数据 |
| 自动选优 | `select_best=True` 生成对比节点，标记最优模型 |
| 超参搜索 | `search=True` 启用 RandomizedSearchCV，按 `param_space()` 自动搜索 |
| 分类任务 | 回归/分类双模式，分类指标含 accuracy/f1/auc，类型校验 |
| 结果持久化 | SQLite 存储运行记录，`--history` 查询历史 |
| Web 控制台 | 浏览器中选模型、配参数、运行流水线、查看画布、读日志 |

---

## 项目结构

```
loom/
├── core/
│   ├── __init__.py        # 包初始化 + 导出公共接口
│   ├── base.py            # BaseModel / BaseDataset 抽象接口
│   ├── registry.py        # 注册表与查询（@register_model / @register_dataset）
│   ├── runner.py          # 调度引擎（选优 + 搜索 + 分类 + 节点组装）
│   ├── llm_analyzer.py    # LLM 封装（DeepSeek / Ollama，OpenAI 兼容 SDK）
│   └── store.py           # SQLite 持久化（save_run / list_runs / get_run）
├── models/
│   ├── __init__.py        # 导入所有模型模块以触发注册
│   ├── linear.py          # 线性回归（LinearRegression）
│   ├── forest.py          # 随机森林（RandomForestRegressor）
│   ├── logistic.py        # 逻辑回归（LogisticRegression，分类）
│   └── ridge.py           # Ridge 回归（示例扩展）
├── datasets/
│   ├── __init__.py        # 导入所有数据集模块以触发注册
│   ├── toy.py             # diabetes（回归，442×10）
│   ├── classification.py  # breast_cancer（分类，569×30）
│   └── california.py      # california_housing（回归，20640×8，示例扩展）
├── web/
│   └── index.html         # Web 控制台前端（单页应用）
├── output/                # 运行时生成 nodes.json / automl.db
│   ├── flowml_canvas.html # 独立画布页面（静态）
│   └── .gitkeep
├── server.py              # Flask Web 服务器
├── main.py                # 命令行入口
├── start.sh               # 一键启动脚本（web / cli / history）
├── requirements.txt       # Python 依赖
├── .env.example           # LLM 配置模板
└── README.md              # 本文档
```

---

## 环境要求

- Python 3.10+
- 依赖包：scikit-learn, numpy, openai, python-dotenv（可选）, flask

---

## 安装

```bash
# 1. 解压
unzip loom.zip
cd loom

# 2. 安装依赖
pip install -r requirements.txt
```

---

## 启动

提供三种启动模式：

### Web 控制台模式（推荐）

```bash
./start.sh web
# 或
python server.py
```

启动后浏览器访问 `http://localhost:5000`

### 命令行模式

```bash
./start.sh cli
# 或
python main.py
```

### 历史查询

```bash
./start.sh history
# 或
python main.py --history
```

### 自定义端口

```bash
FLOWML_PORT=8080 python server.py
```

---

## Web 控制台使用指南

### 界面布局

```
┌─────────────────────────────────────────────────────┐
│  Loom AutoML 控制台          [运行] [重置] [历史]  │  ← 顶栏
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│  配置面板 │            流水线画布                     │  ← 主区域
│          │     (节点拖动、状态样式、连线)             │
│  数据集   │                                          │
│  模型选择 │                                          │
│  参数配置 │                                          │
│  LLM配置  │                                          │
│          ├──────────────────────────────────────────┤
│          │            运行日志                       │  ← 底部日志
│          │     (实时输出训练过程与LLM分析)            │
└──────────┴──────────────────────────────────────────┘
```

### 操作步骤

1. **选择数据集**：左侧下拉框选择（diabetes / breast_cancer / california_housing）
2. **选择模型**：多选框勾选一个或多个模型
3. **配置参数**（可选）：
   - `test_size`：测试集比例（默认 0.2）
   - `seed`：随机种子（默认 42）
   - `select_best`：勾选后自动选优并生成对比节点
   - `llm_post_scope`：`all`（全部解读）或 `best`（仅最优）
   - `search`：勾选后启用超参搜索，可设 `n_iter` 和 `cv`
4. **点击「运行」**：画布实时渲染节点，底部日志输出过程
5. **查看结果**：
   - 画布中节点按类型展示不同内容
   - 拖动节点调整布局
   - 点击「重置」恢复初始布局
   - 点击「历史」查看历史运行记录

### 节点类型说明

| 节点类型 | 颜色 | 展示内容 |
|---------|------|---------|
| dataset | 绿色边框 | 样本数、特征数、特征名列表（可折叠） |
| model | 绿色边框 | 模型名、参数 |
| metric | 绿色边框 | MSE/R²（回归）或 accuracy/f1/auc（分类） |
| llm_analysis | 灰色虚线（skipped） | LLM 原文或结构化卡片 |
| comparison | 绿色边框 | 多模型对比表，标记最优 |

### 节点状态样式

| 状态 | 样式 |
|------|------|
| success | 绿色边框 |
| running | 蓝色脉冲动画 |
| failed | 红色边框 |
| skipped | 灰色虚线边框 + "已跳过" |

---

## 命令行使用指南

### 基本用法

```python
from loom.core import run, list_models, list_datasets

# 查看已注册的模型和数据集
print(list_models())      # ['linear_regression', 'random_forest', 'ridge', ...]
print(list_datasets())    # ['diabetes', 'breast_cancer', 'california_housing']

# 单模型运行
result = run("linear_regression", "diabetes")

# 多模型运行
result = run(["linear_regression", "random_forest"], "diabetes")

# 自动选优
result = run(["linear_regression", "random_forest"], "diabetes", select_best=True)
print(result["best_model"])  # 'linear_regression'

# 超参搜索
result = run("random_forest", "diabetes", search=True, n_iter=10, cv=5)

# 分类任务
result = run("logistic_regression", "breast_cancer")
print(result["metrics"]["logistic_regression"])
# {'accuracy': 0.9649, 'f1': 0.9647, 'auc': 0.9954}

# 只对最优模型做 LLM 解读
result = run(["linear_regression", "ridge"], "diabetes",
             select_best=True, llm_post_scope="best")
```

### 返回结构

```python
{
    "run_id": "20261103-142530-diabetes",
    "metrics": {
        "linear_regression": {"mse": 2900.19, "r2": 0.4526},
        "random_forest": {"mse": 2946.84, "r2": 0.4438}
    },
    "best_model": "linear_regression",   # select_best=True 时有值
    "nodes": [...],                        # 节点数据（供前端渲染）
    "edges": [...]                         # 连线数据
}
```

### 历史查询

```python
from loom.core.store import list_runs, get_run

# 列出最近 20 条
runs = list_runs(limit=20)

# 按数据集过滤
runs = list_runs(dataset_name="diabetes", limit=10)

# 查看某次运行详情
detail = get_run("20261103-142530-diabetes")
# {"run": {...}, "metrics": {...}, "llm_analysis": [...]}
```

---

## LLM 配置

LLM 分析为可选功能，不配置时训练评估正常执行，LLM 节点标记为 `skipped`。

### 配置方法

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# LLM 提供方: deepseek | ollama
AUTOML_LLM_PROVIDER=deepseek

# API Key（DeepSeek 必填，Ollama 填任意占位符）
AUTOML_LLM_API_KEY=sk-your-deepseek-key

# 端点（可选，按 provider 取默认）
# DeepSeek 默认: https://api.deepseek.com
# Ollama 默认: http://localhost:11434/v1
AUTOML_LLM_BASE_URL=

# 模型名（可选，按 provider 取默认）
# DeepSeek 默认: deepseek-chat
# Ollama 默认: qwen2.5:7b
AUTOML_LLM_MODEL=

# 超时秒数（可选，默认 30）
AUTOML_LLM_TIMEOUT=30
```

### Provider 对照

| Provider | base_url | api_key | 说明 |
|----------|----------|---------|------|
| deepseek | https://api.deepseek.com | 必填 | 通过 OpenAI 兼容 SDK 调用 |
| ollama | http://localhost:11434/v1 | 任意占位符 | 本地部署，无需真实 key |

### LLM 输出容错

| 场景 | 行为 |
|------|------|
| LLM 返回合法 JSON | `structured` 有值，`parse_failed=False`，`content` 保留原文 |
| LLM 返回自然语言 | `structured=null`，`parse_failed=True`，`content` 保留原文供展示 |
| 网络/超时/密钥缺失 | 返回 `None`，节点标记 `status: "skipped"`，主流程继续 |

---

## 扩展：添加新模型

### 步骤

1. 在 `models/` 目录下新建 `.py` 文件
2. 继承 `BaseModel`，实现 4 个抽象方法
3. 用 `@register_model("名称")` 注册
4. 在 `models/__init__.py` 中加一行导入

### 模板

```python
# models/my_model.py
import numpy as np
from some_library import SomeModel

from loom.core.base import BaseModel
from loom.core.registry import register_model


@register_model("my_model")
class MyModel(BaseModel):
    task_type = "regression"  # 或 "classification"

    def __init__(self, param1=1.0, **kwargs):
        self._model = SomeModel(param1=param1, **kwargs)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def get_params(self) -> dict:
        return {"param1": self._model.param1}

    def param_space(self) -> dict:
        # 超参搜索空间，返回空字典表示不参与搜索
        return {"param1": [0.1, 1.0, 10.0]}
```

```python
# models/__init__.py 中添加
from . import my_model  # noqa: F401
```

### 完整示例：Ridge 回归

```python
# models/ridge.py
import numpy as np
from sklearn.linear_model import Ridge
from loom.core.base import BaseModel
from loom.core.registry import register_model

@register_model("ridge")
class RidgeModel(BaseModel):
    task_type = "regression"

    def __init__(self, alpha: float = 1.0, **kwargs):
        self._model = Ridge(alpha=alpha, **kwargs)

    def fit(self, X, y):
        self._model.fit(X, y)

    def predict(self, X):
        return self._model.predict(X)

    def get_params(self):
        return {"alpha": self._model.alpha, "solver": self._model.solver}

    def param_space(self):
        return {"alpha": [0.01, 0.1, 1.0, 10.0, 100.0]}
```

### 要点

- `task_type` 必须与数据集一致，否则 `run()` 会报错
- `param_space()` 返回空字典 `{}` 时，`search=True` 也会跳过该模型
- `core/` 目录下的任何文件都不需要修改
- Web 控制台自动识别新注册的模型

---

## 扩展：添加新数据集

### 步骤

1. 在 `datasets/` 目录下新建 `.py` 文件
2. 继承 `BaseDataset`，实现 `load()` 和 `feature_names()` 两个抽象方法
3. 用 `@register_dataset("名称")` 注册
4. 在 `datasets/__init__.py` 中加一行导入

### 模板

```python
# datasets/my_dataset.py
import numpy as np
from loom.core.base import BaseDataset
from loom.core.registry import register_dataset

@register_dataset("my_dataset")
class MyDataset(BaseDataset):
    task_type = "regression"  # 或 "classification"

    def load(self) -> tuple[np.ndarray, np.ndarray]:
        # 返回 (特征矩阵 X, 目标向量 y)
        ...
        return X, y

    def feature_names(self) -> list[str]:
        return ["feature1", "feature2", ...]
```

```python
# datasets/__init__.py 中添加
from . import my_dataset  # noqa: F401
```

### 完整示例：California Housing

```python
# datasets/california.py
import numpy as np
from sklearn.datasets import fetch_california_housing
from loom.core.base import BaseDataset
from loom.core.registry import register_dataset

@register_dataset("california_housing")
class CaliforniaHousingDataset(BaseDataset):
    task_type = "regression"

    def load(self):
        data = fetch_california_housing()
        return data.data, data.target

    def feature_names(self):
        return list(fetch_california_housing().feature_names)
```

### 要点

- `load()` 返回 `(X, y)`，X 是 numpy 数组，y 是一维目标向量
- `feature_names()` 返回字符串列表
- `task_type` 必须与模型一致，`run()` 启动时会校验
- `core/` 目录下的任何文件都不需要修改
- Web 控制台自动识别新注册的数据集

---

## API 接口文档

Web 服务器（`python server.py`）提供以下 API：

### GET /api/models

列出已注册模型。

| 参数 | 类型 | 说明 |
|------|------|------|
| task_type | string, 可选 | 按任务类型过滤（regression / classification） |

**响应**：`{"models": ["linear_regression", "random_forest", ...]}`

### GET /api/datasets

列出已注册数据集。

| 参数 | 类型 | 说明 |
|------|------|------|
| task_type | string, 可选 | 按任务类型过滤 |

**响应**：`{"datasets": ["diabetes", "breast_cancer", ...]}`

### POST /api/run

运行流水线。

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
    "cv": 5
}
```

**响应**：

```json
{
    "status": "success",
    "run_id": "20261103-142530-diabetes",
    "metrics": {...},
    "best_model": "linear_regression",
    "nodes": [...],
    "edges": [...],
    "log": "训练过程日志文本..."
}
```

### GET /api/history

查询历史运行记录。

| 参数 | 类型 | 说明 |
|------|------|------|
| limit | int, 默认 20 | 返回条数 |
| dataset_name | string, 可选 | 按数据集过滤 |

**响应**：`{"runs": [{"run_id": "...", "dataset_name": "...", "best_model": "...", "timestamp": "..."}]}`

### GET /api/run/:run_id

查询单次运行详情。

**响应**：

```json
{
    "status": "success",
    "data": {
        "run": {...},
        "metrics": {...},
        "llm_analysis": [...]
    }
}
```

### GET /api/config

返回当前 LLM 配置状态（隐藏完整 api_key）。

**响应**：

```json
{
    "provider": "deepseek",
    "has_api_key": true,
    "api_key_preview": "sk-abcde...",
    "base_url": "",
    "model": "",
    "timeout": "30"
}
```

---

## 运行示例

### 命令行输出

```
============================================================
Loom AutoML 框架 — 可扩展机器学习流水线
============================================================

已注册模型: ['linear_regression', 'random_forest', 'logistic_regression', 'ridge']
已注册数据集: ['diabetes', 'breast_cancer', 'california_housing']

▶ 运行: run(['linear_regression', 'random_forest'], 'diabetes', select_best=True)

[LLM 训练前分析] 跳过（未配置 LLM）

[linear_regression] mse=2900.1936  r2=0.4526
[random_forest] mse=2946.8415  r2=0.4438
▶ 最优模型: linear_regression (r2=0.4526)
[LLM 结果解读 linear_regression] 跳过（未配置 LLM）
[LLM 结果解读 random_forest] 跳过（未配置 LLM）

节点数据已写入: output/nodes.json
✓ 结果已持久化: output/automl.db

============================================================
评估指标
============================================================
  linear_regression: mse=2900.1936  r2=0.4526
  random_forest: mse=2946.8415  r2=0.4438

  ⭐ 最优模型: linear_regression

节点数: 9  边数: 9
完成。nodes.json 已写入 output/ 目录。
运行 python main.py --history 查看历史记录。
```

### 历史查询

```
============================================================
历史运行记录
============================================================
  20261103-142530-diabetes  |  数据集: diabetes  |  最优: linear_regression  |  时间: 2026-11-03T14:25:30
  20261103-142410-breast_cancer  |  数据集: breast_cancer  |  最优: N/A  |  时间: 2026-11-03T14:24:10
```

### nodes.json 结构

```json
{
  "run_id": "20261103-142530-diabetes",
  "nodes": [
    {
      "id": "dataset-diabetes",
      "type": "dataset",
      "label": "数据集: diabetes",
      "status": "success",
      "position": {"x": 0, "y": 0},
      "display": {
        "n_samples": 442,
        "n_features": 10,
        "feature_names": ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"],
        "task_type": "regression"
      }
    },
    {
      "id": "llm_pre",
      "type": "llm_analysis",
      "label": "训练前 LLM 分析",
      "status": "skipped",
      "position": {"x": 250, "y": 0},
      "display": {
        "stage": "pre_train",
        "model_name": null,
        "content": "",
        "structured": null,
        "parse_failed": true
      }
    },
    ...
  ],
  "edges": [
    {"source": "dataset-diabetes", "target": "llm_pre"},
    {"source": "llm_pre", "target": "model-linear_regression"},
    ...
  ]
}
```

---

## License

本仓库中的源代码（`core/`、`models/`、`datasets/`、`server.py`、`main.py` 等）采用 **GNU AGPL-3.0** 许可证，全文见 `LICENSE` 文件。

`docs/` 目录下的所有文档采用 **CC BY-SA 4.0** 许可证，全文见 `LICENSE-docs` 文件。
