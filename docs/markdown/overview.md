# Loom — 可扩展 AutoML 框架

> 注册即用的机器学习流水线框架——选模型、配参数、一键运行，LLM 智能分析，画布可视化全流程。

## 功能概览

- **注册即用**：新增模型/数据集只需 1 个文件 + 1 行注册，不改核心代码
- **全流程可视化**：每个步骤都是画布上的独立节点，可拖动、可查看详情
- **LLM 智能分析**：DeepSeek/Ollama 双 provider，训练前分析 + 训练后解读
- **AI 对话**：与大模型流式对话，可附带项目代码和运行结果
- **多模型选优**：自动比较所有模型，标记最优
- **超参搜索**：RandomizedSearchCV，各模型声明搜索空间
- **分类任务**：回归/分类双模式，类型校验
- **结果持久化**：SQLite 存储，历史回看
- **CSV 上传**：自定义数据集
- **代码编辑**：在线查看与编辑所有源码，热加载重启

## 快速开始

```bash
pip install -r requirements.txt
./start.sh web
# 打开 http://localhost:8899
```

## 流程图

```
config → dataset → llm_pre → split → model_A → search_A → metric_A → llm_post_A
                                     → model_B → search_B → metric_B → llm_post_B
                                                                        → comparison
```

## 内置模型

| 模型 | 类型 | 说明 |
|------|------|------|
| linear_regression | 回归 | sklearn LinearRegression |
| random_forest | 回归 | RandomForestRegressor |
| ridge | 回归 | Ridge，支持 alpha 超参搜索 |
| logistic_regression | 分类 | LogisticRegression，支持 C/solver 搜索 |

## 内置数据集

| 数据集 | 类型 | 样本 × 特征 |
|--------|------|------------|
| diabetes | 回归 | 442 × 10 |
| breast_cancer | 分类 | 569 × 30 |
| california_housing | 回归 | 20640 × 8 |

## 技术栈

- **后端**：Python 3.10+, Flask, scikit-learn, OpenAI SDK
- **前端**：原生 HTML/CSS/JS（无框架依赖）
- **存储**：SQLite
- **LLM**：DeepSeek / Ollama（OpenAI 兼容接口）

## License

- 代码：[AGPL-3.0](https://github.com/Jia-Yee/loom/blob/main/LICENSE)
- 文档：[CC BY-SA 4.0](https://github.com/Jia-Yee/loom/blob/main/LICENSE-docs)
