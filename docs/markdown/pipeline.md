# 流程文档

## 流程图结构

每次运行 `run()` 会生成一组节点和边，构成完整的流程图。

### 节点类型

| 类型 | 说明 | 展示内容 |
|------|------|---------|
| `config` | 运行参数 | test_size, seed, select_best, search, LLM 配置 |
| `dataset` | 数据集 | 样本数、特征数、特征名 |
| `llm_analysis` | LLM 分析 | 原始文本 + 结构化 JSON（容错） |
| `split` | 数据切分 | 训练/测试集大小、分层采样 |
| `model` | 模型 | 模型名、参数 |
| `search` | 超参搜索 | n_iter, cv, best_score, 搜索空间 |
| `metric` | 评估指标 | 回归: MSE/R²，分类: accuracy/f1/auc |
| `comparison` | 模型对比 | 多模型对比，标记最优 |

### 流程图布局

**单模型：**

```
config → dataset → llm_pre → split → model → search → metric → llm_post
```

**多模型 + 选优：**

```
config → dataset → llm_pre → split → model_A → search_A → metric_A → llm_post_A
                                     → model_B → search_B → metric_B → llm_post_B
                                                                        → comparison
```

### 节点状态

| 状态 | 样式 | 说明 |
|------|------|------|
| `success` | 绿色边框 | 步骤成功完成 |
| `running` | 蓝色脉冲 | 正在执行 |
| `failed` | 红色边框 | 执行失败 |
| `skipped` | 灰色虚线 | 跳过（如 LLM 未配置） |

## 运行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_names | str/list | 必填 | 模型名或模型名列表 |
| dataset_name | str | 必填 | 数据集注册名 |
| test_size | float | 0.2 | 测试集比例 |
| seed | int | 42 | 随机种子 |
| select_best | bool | False | 是否自动选优 |
| llm_post_scope | str | "all" | LLM 解读范围：all/best |
| search | bool | False | 是否启用超参搜索 |
| n_iter | int | 10 | 搜索迭代次数 |
| cv | int | 5 | 交叉验证折数 |

## LLM 分析

### 训练前分析（仅一次）

将数据集摘要传给 LLM，返回：
- 适合的模型类型建议
- 潜在数据问题
- 对线性模型的适用性判断

### 训练后解读（按模型）

将评估指标传给 LLM，返回：
- 模型表现的自然语言解读
- 改进方向建议

### 容错机制

- LLM 返回合法 JSON → 结构化展示
- LLM 返回纯文本 → 保留原文展示
- 网络/超时/密钥缺失 → 节点标记 `skipped`，主流程继续

## 数据持久化

### SQLite 三表

| 表 | 内容 |
|---|---|
| `runs` | run_id、数据集、时间、最优模型、完整 nodes/edges |
| `metrics` | 每个模型的指标、参数、搜索信息 |
| `llm_analysis` | LLM 分析文本和结构化结果 |

### 历史回看

```bash
./start.sh history
# 或
python main.py --history
```

API 方式：

```
GET /api/run/<run_id>/nodes  # 返回完整 nodes/edges
```
