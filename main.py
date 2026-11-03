"""Loom AutoML 框架入口：一键运行，命令行输出指标与 LLM 分析。"""

import json
import os
import sys

# 确保包可导入（python main.py 直接运行时）
# 动态推导包名，重命名项目目录无需改代码
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PKG = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# 加载 .env（如果 python-dotenv 可用）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from importlib import import_module
_core = import_module(f"{_PKG}.core")
run = _core.run
list_models = _core.list_models
list_datasets = _core.list_datasets
list_runs = _core.store.list_runs


def main():
    # ── --history 模式 ─────────────────────────────────────
    if "--history" in sys.argv:
        print("=" * 60)
        print("历史运行记录")
        print("=" * 60)
        runs = list_runs(limit=20)
        if not runs:
            print("（暂无记录）")
        else:
            for r in runs:
                print(f"  {r['run_id']}  |  数据集: {r['dataset_name']}  |  "
                      f"最优: {r['best_model'] or 'N/A'}  |  时间: {r['timestamp']}")
        return

    print("=" * 60)
    print("Loom AutoML 框架 — 可扩展机器学习流水线")
    print("=" * 60)

    # ── 列出已注册模型与数据集 ────────────────────────────
    print(f"\n已注册模型: {list_models()}")
    print(f"已注册数据集: {list_datasets()}")

    # ── 运行 ──────────────────────────────────────────────
    print("\n▶ 运行: run(['linear_regression', 'random_forest'], 'diabetes', select_best=True)")
    result = run(
        ["linear_regression", "random_forest"],
        "diabetes",
        select_best=True,
    )

    # ── 打印指标 ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print("评估指标")
    print("=" * 60)
    for model_name, m in result["metrics"].items():
        metrics_str = "  ".join(f"{k}={v:.4f}" for k, v in m.items())
        print(f"  {model_name}: {metrics_str}")

    if result.get("best_model"):
        print(f"\n  ⭐ 最优模型: {result['best_model']}")

    # ── 节点统计 ──────────────────────────────────────────
    print(f"\n节点数: {len(result['nodes'])}  边数: {len(result['edges'])}")
    for node in result["nodes"]:
        status = node["status"]
        label = node["label"]
        print(f"  [{node['type']:14s}] {label:30s}  {status}")

    print("\n完成。nodes.json 已写入 output/ 目录。")
    print("运行 python main.py --history 查看历史记录。")


if __name__ == "__main__":
    main()
