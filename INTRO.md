# Loom — 可扩展 AutoML 框架

> **一句话介绍**：注册即用的机器学习流水线框架——选模型、配参数、一键运行，LLM 智能分析，画布可视化全流程。

## 这是什么

Loom 是一个面向研究者和工程师的 AutoML 框架。它不追求全自动，而是把"配置 → 运行 → 分析 → 改进"的循环做到极简：

1. **选数据集和模型**（内置 4 个模型 + 3 个数据集，支持 CSV 上传）
2. **配参数**（测试集比例、随机种子、是否选优、是否搜索超参）
3. **运行**（实时进度推送，每一步状态可见）
4. **看结果**（画布流程图 + 指标 + LLM 解读）
5. **问 AI**（内置 Chat，可附带代码和结果，对话式分析改进）

## 核心特性

### 注册即用
新增模型/数据集只需 1 个文件 + 1 行注册，不改核心代码：
```python
@register_model("my_model")
class MyModel(BaseModel):
    task_type = "regression"
    def fit(self, X, y): ...
    def predict(self, X): ...
```

### 全流程可视化
每个步骤都是画布上的独立节点，可拖动、可查看详情：

```
config → dataset → llm_pre → split → model_A → search_A → metric_A → llm_post_A
                                     → model_B → search_B → metric_B → llm_post_B
                                                                        → comparison
```

| 节点类型 | 展示内容 |
|---------|---------|
| `config` | 运行参数（test_size、seed、select_best、search、LLM 配置） |
| `dataset` | 样本数、特征数、特征名 |
| `llm_analysis` | LLM 原始文本 + 结构化 JSON（容错） |
| `split` | 训练/测试集大小、分层采样 |
| `model` | 模型名、参数 |
| `search` | 超参搜索信息（n_iter、cv、best_score） |
| `metric` | 评估指标（回归: MSE/R²，分类: accuracy/f1/auc） |
| `comparison` | 多模型对比，标记最优 |

### LLM 智能分析
- 支持 DeepSeek / Ollama 双 provider
- 训练前：分析数据特征，建议模型类型
- 训练后：解读结果，给出改进方向
- 容错：LLM 失败不影响主流程，原始文本保留展示
- 内置测试连接功能

### AI 对话
- 与大模型流式对话（SSE）
- 可附带项目全部源码作为上下文
- 可附带最近运行结果
- 根据对话建议模型组合和参数

### 多模型选优
- `select_best=True` 自动比较所有模型
- 按 R²（回归）或 accuracy（分类）排序
- 生成 comparison 节点标记最优

### 超参搜索
- `search=True` 启用 RandomizedSearchCV
- 各模型通过 `param_space()` 声明搜索空间
- 搜索结果独立节点展示

### 分类任务
- 回归/分类双模式
- 类型校验（模型与数据集 task_type 必须一致）
- 分类指标：accuracy / f1 / auc

### 结果持久化
- SQLite 存储所有运行记录
- `--history` 查询历史
- 支持按数据集过滤

### CSV 数据上传
- Web 界面上传 CSV
- 自动解析列名
- 选择目标列和任务类型
- 注册后即可使用

## 快速开始

```bash
# 安装
pip install -r requirements.txt

# Web 控制台（推荐）
./start.sh web
# 打开 http://localhost:8899

# 命令行
./start.sh cli

# 查看历史
./start.sh history
```

## 内置模型

| 模型 | 类型 | 说明 |
|------|------|------|
| `linear_regression` | 回归 | sklearn LinearRegression |
| `random_forest` | 回归 | RandomForestRegressor |
| `ridge` | 回归 | Ridge，支持 alpha 超参搜索 |
| `logistic_regression` | 分类 | LogisticRegression，支持 C/solver 搜索 |

## 内置数据集

| 数据集 | 类型 | 样本 × 特征 |
|--------|------|------------|
| `diabetes` | 回归 | 442 × 10 |
| `breast_cancer` | 分类 | 569 × 30 |
| `california_housing` | 回归 | 20640 × 8 |

## 技术栈

- **后端**：Python 3.10+, Flask, scikit-learn, OpenAI SDK
- **前端**：原生 HTML/CSS/JS（无框架依赖）
- **存储**：SQLite
- **LLM**：DeepSeek / Ollama（OpenAI 兼容接口）

## License

- 代码：[GNU AGPL-3.0](LICENSE)
- 文档：[CC BY-SA 4.0](LICENSE-docs)

## GitHub

https://github.com/Jia-Yee/loom
