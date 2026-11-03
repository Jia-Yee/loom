# Loom 测试文档

## 一、环境准备

### 1.1 安装依赖

```bash
cd loom
pip install -r requirements.txt
```

### 1.2 启动 Web 服务

```bash
./start.sh web
# 或 python server.py
```

确认输出：
```
Loom Web 控制台启动中...
访问 http://localhost:8899
```

### 1.3 访问

浏览器打开 http://localhost:8899

---

## 二、功能测试清单

### T1. 顶栏与标签切换

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T1.1 | 打开页面 | 顶栏显示「🌀 Loom」、三个标签（流程编辑器/AI对话/代码）、⚙ LLM 按钮、运行按钮 |
| T1.2 | 点击「AI 对话」 | 切换到对话面板，显示输入框和发送按钮 |
| T1.3 | 点击「代码」 | 切换到代码面板，左侧显示文件树 |
| T1.4 | 点击「流程编辑器」 | 切回画布，显示空画布和节点库 |

### T2. LLM 全局配置

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T2.1 | 点击「⚙ LLM」 | 弹出配置弹窗 |
| T2.2 | Provider 选 Ollama，模型填 qwen3.5:4b | 输入框正常 |
| T2.3 | 点击「测试连接」 | 显示测试结果（成功/失败+原因） |
| T2.4 | 点击「保存」 | 弹窗关闭，日志显示「LLM 配置已保存」，顶栏状态显示模型名 |
| T2.5 | 刷新页面 | 配置仍在（localStorage 持久化） |

### T3. 节点库

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T3.1 | 查看左栏 | 显示 6 个分类：数据、处理、模型、评估、LLM、输出 |
| T3.2 | 点击分类标题 | 展开/折叠子节点 |
| T3.3 | 在搜索框输入"模型" | 过滤显示匹配的节点 |

### T4. 拖拽节点到画布

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T4.1 | 从左栏拖「数据集」到画布 | 画布出现数据集节点，右栏显示参数表单 |
| T4.2 | 从左栏拖「数据切分」到画布 | 出现切分节点 |
| T4.3 | 从左栏拖「模型训练」到画布 | 出现模型节点 |
| T4.4 | 从左栏拖「评估指标」到画布 | 出现指标节点 |
| T4.5 | 拖拽时画布高亮 | drag-over 样式（背景变色） |

### T5. 节点拖动

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T5.1 | 鼠标按住画布上的节点 | 节点可拖动 |
| T5.2 | 拖动到新位置 | 节点跟随鼠标，连线实时更新 |
| T5.3 | 松开鼠标 | 节点停在新位置 |

### T6. 节点连线

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T6.1 | 点击数据集节点的右侧端口 | 端口高亮 |
| T6.2 | 拖到切分节点的左侧端口 | 出现连线 |
| T6.3 | 连接：数据集→切分→模型→指标 | 4 条连线正确显示 |
| T6.4 | 点击连线 | 连线可选中（高亮） |
| T6.5 | 右键节点 | 可删除节点 |

### T7. 右栏参数配置

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T7.1 | 点击数据集节点 | 右栏显示数据集选择下拉框 |
| T7.2 | 选择 diabetes | 配置保存到节点 |
| T7.3 | 点击模型节点 | 右栏显示模型选择下拉框 |
| T7.4 | 选择 linear_regression | 配置保存 |
| T7.5 | 点击切分节点 | 右栏显示 test_size 和 seed 输入框 |
| T7.6 | 修改 test_size 为 0.3 | 配置保存 |
| T7.7 | 右栏下方显示对应代码 | 代码内容正确 |

### T8. 运行流水线（无 LLM）

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T8.1 | 拖入：数据集→切分→模型→指标，连线 | 画布有 4 节点 3 连线 |
| T8.2 | 数据集选 diabetes，模型选 linear_regression | 参数已配置 |
| T8.3 | 点击「▶ 运行」 | 日志开始输出，节点状态变为 running |
| T8.4 | 观察日志 | 依次显示 init→dataset→llm_init(skipped)→llm_pre(skipped)→split→train→llm_post(skipped)→done |
| T8.5 | 运行完成 | 节点状态变为 success/skipped，指标节点显示 MSE 和 R² |
| T8.6 | 检查 output/nodes.json | 文件已生成，包含节点和边 |
| T8.7 | 检查 output/automl.db | 数据库已生成，三表有记录 |

### T9. 运行流水线（带 LLM）

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T9.1 | 配置 LLM（⚙ LLM → Ollama → 测试 → 保存） | 顶栏显示 LLM 模型名 |
| T9.2 | 拖入 LLM 分析节点（训练前 + 训练后） | 画布有 6 节点 |
| T9.3 | 点击运行 | 日志显示 LLM 调用详情（model/base_url/timeout） |
| T9.4 | LLM 分析中 | 日志显示 prompt 长度、耗时、token 用量 |
| T9.5 | LLM 完成 | llm_pre 和 llm_post 节点显示分析文本 |
| T9.6 | LLM 超时/失败 | 节点标记 skipped，日志显示具体错误，主流程继续 |

### T10. 多模型分支

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T10.1 | 拖入 2 个模型节点 | 画布有 2 个 model 节点 |
| T10.2 | 分别选 linear_regression 和 random_forest | 两个模型不同 |
| T10.3 | 从切分节点分别连线到两个模型 | 2 条连线 |
| T10.4 | 拖入对比节点，连线 | comparison 节点出现 |
| T10.5 | 运行 | 两个模型分别训练，comparison 显示最优 |
| T10.6 | 日志显示两个模型的指标 | MSE/R² 各一组 |

### T11. 超参搜索

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T11.1 | 拖入搜索节点 | 画布有 search 节点 |
| T11.2 | 配置 n_iter=5, cv=3 | 参数已设置 |
| T11.3 | 运行 | 日志显示"超参搜索中..." |
| T11.4 | 完成 | search 节点显示 best_score，model 节点显示最优参数 |

### T12. AI 对话

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T12.1 | 切到「AI 对话」标签 | 显示对话界面 |
| T12.2 | 输入"你好" | 用户消息显示在右侧 |
| T12.3 | 等待回复 | AI 回复流式输出在左侧 |
| T12.4 | 勾选「附带代码」 | 下次对话附带项目源码 |
| T12.5 | 点击「分析结果」快捷按钮 | 自动填入并发送 |
| T12.6 | 未配置 LLM 时对话 | 提示"请先配置 LLM" |

### T13. 代码查看与编辑

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T13.1 | 切到「代码」标签 | 左侧显示文件树（按目录分组） |
| T13.2 | 点击 models/linear.py | 右侧显示代码内容 |
| T13.3 | 点击「编辑」 | 进入编辑模式（textarea） |
| T13.4 | 修改代码 | 可编辑 |
| T13.5 | 点击「保存」 | 显示"保存成功"，热加载重启 |
| T13.6 | 点击「取消」 | 放弃修改回到查看模式 |

### T14. CSV 上传

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T14.1 | 拖入 CSV 上传节点 | 节点出现在画布 |
| T14.2 | 右栏选择 CSV 文件 | 上传成功，返回列名 |
| T14.3 | 选择目标列和任务类型 | 配置保存 |
| T14.4 | 连线到模型节点 | 连线正常 |
| T14.5 | 运行 | 使用 CSV 数据训练 |

### T15. 数据集分析

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T15.1 | 拖入数据分析节点 | 节点出现 |
| T15.2 | 连线数据集→数据分析 | 连线正常 |
| T15.3 | 运行 | 分析节点显示统计信息 |
| T15.4 | API: GET /api/dataset/diabetes/preview | 返回预览、统计、相关性 |

### T16. 历史记录

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T16.1 | 点击「历史」按钮 | 弹出历史列表 |
| T16.2 | 查看记录 | 显示 run_id、数据集、最优模型、时间 |
| T16.3 | 连续运行两次 | 历史有两条记录 |
| T16.4 | API: GET /api/run/<run_id>/nodes | 返回完整 nodes/edges |

### T17. 下载

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T17.1 | 运行完成后 | 画布工具栏显示下载按钮 |
| T17.2 | 点击「下载 nodes.json」 | 浏览器下载文件 |
| T17.3 | 点击「下载完整结果」 | 下载完整 result JSON |

### T18. 命令行模式

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T18.1 | `./start.sh cli` | 命令行输出模型列表、指标、节点统计 |
| T18.2 | `./start.sh history` | 输出历史记录列表 |
| T18.3 | 无 .env 时运行 | LLM 跳过，训练正常完成 |

### T19. 扩展性

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T19.1 | 新建 models/svm.py，注册 @register_model("svm") | 文件创建 |
| T19.2 | models/__init__.py 加 import | 注册触发 |
| T19.3 | 热加载重启 | 服务器自动重启 |
| T19.4 | 刷新页面，左栏节点库 | 模型分类下出现 svm |
| T19.5 | 拖入 svm 节点，运行 | 正常训练 |

### T20. 项目重命名

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| T20.1 | 复制 loom 目录为 my_project | 目录复制 |
| T20.2 | `cd my_project && python main.py` | 正常运行，无导入错误 |
| T20.3 | `python server.py` | Web 服务正常启动 |

---

## 三、API 测试

### A1. GET /api/models

```bash
curl http://localhost:8899/api/models
# 预期: {"models":["linear_regression","random_forest","logistic_regression","ridge"]}
```

### A2. GET /api/datasets

```bash
curl http://localhost:8899/api/datasets
# 预期: {"datasets":["diabetes","breast_cancer","california_housing"]}
```

### A3. GET /api/dataset/diabetes/preview

```bash
curl http://localhost:8899/api/dataset/diabetes/preview | python -m json.tool
# 预期: 返回 preview, feature_stats, target_stats, correlations
```

### A4. POST /api/run_stream

```bash
curl -N -X POST http://localhost:8899/api/run_stream \
  -H "Content-Type: application/json" \
  -d '{"model_names":["linear_regression"],"dataset_name":"diabetes"}'
# 预期: SSE 流式输出 step 事件，最终 done
```

### A5. POST /api/llm_test

```bash
curl -X POST http://localhost:8899/api/llm_test \
  -H "Content-Type: application/json" \
  -d '{"provider":"ollama","model":"qwen3.5:4b"}'
# 预期: {"status":"success","message":"连接成功！..."} 或错误信息
```

### A6. POST /api/chat

```bash
curl -N -X POST http://localhost:8899/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}],"provider":"ollama","model":"qwen3.5:4b"}'
# 预期: SSE 流式输出 chunk 事件
```

### A7. GET /api/code

```bash
curl http://localhost:8899/api/code
# 预期: {"files":[{"path":"core/base.py","size":1844},...]}
```

### A8. GET /api/code/models/linear.py

```bash
curl http://localhost:8899/api/code/models/linear.py
# 预期: {"status":"success","content":"...","lines":35}
```

### A9. PUT /api/code/models/linear.py

```bash
curl -X PUT http://localhost:8899/api/code/models/linear.py \
  -H "Content-Type: application/json" \
  -d '{"content":"# modified"}'
# 预期: {"status":"success","message":"保存成功..."}
```

### A10. GET /api/history

```bash
curl http://localhost:8899/api/history
# 预期: {"runs":[{"run_id":"...","dataset_name":"diabetes",...}]}
```

### A11. GET /api/run/<run_id>/nodes

```bash
curl http://localhost:8899/api/run/<run_id>/nodes
# 预期: {"status":"success","nodes":[...],"edges":[...]}
```

---

## 四、测试结果记录

| 测试项 | 结果 | 备注 |
|--------|------|------|
| T1 顶栏与标签切换 | ⬜ | |
| T2 LLM 全局配置 | ⬜ | |
| T3 节点库 | ⬜ | |
| T4 拖拽节点 | ⬜ | |
| T5 节点拖动 | ⬜ | |
| T6 节点连线 | ⬜ | |
| T7 参数配置 | ⬜ | |
| T8 运行（无 LLM） | ⬜ | |
| T9 运行（带 LLM） | ⬜ | |
| T10 多模型分支 | ⬜ | |
| T11 超参搜索 | ⬜ | |
| T12 AI 对话 | ⬜ | |
| T13 代码编辑 | ⬜ | |
| T14 CSV 上传 | ⬜ | |
| T15 数据集分析 | ⬜ | |
| T16 历史记录 | ⬜ | |
| T17 下载 | ⬜ | |
| T18 命令行 | ⬜ | |
| T19 扩展性 | ⬜ | |
| T20 项目重命名 | ⬜ | |
| A1-A11 API | ⬜ | |
