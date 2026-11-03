"""CSV 数据集支持：上传后动态注册，无需改代码。"""

import os
import tempfile
from typing import Optional

import numpy as np
import pandas as pd

from ..core.base import BaseDataset
from ..core.registry import register_dataset, _DATASET_REGISTRY


def register_csv_dataset(
    name: str,
    csv_path: str,
    target_column: str,
    task_type: str = "regression",
    feature_names_override: Optional[list[str]] = None,
) -> str:
    """动态注册一个 CSV 数据集。

    参数：
        name: 注册名（如 "my_csv_data"）
        csv_path: CSV 文件路径
        target_column: 目标列名
        task_type: "regression" 或 "classification"
        feature_names_override: 自定义特征名（可选）

    返回：
        注册名
    """
    df = pd.read_csv(csv_path)
    feature_cols = [c for c in df.columns if c != target_column]
    feat_names = feature_names_override or feature_cols

    class CSVDataset(BaseDataset):
        task_type = task_type

        def load(self):
            X = df[feature_cols].values.astype(float)
            y = df[target_column].values
            if task_type == "classification":
                # 标签编码为整数
                unique = sorted(set(y))
                label_map = {v: i for i, v in enumerate(unique)}
                y = np.array([label_map[v] for v in y])
            else:
                y = y.astype(float)
            return X, y

        def feature_names(self):
            return list(feat_names)

        def summary(self):
            X, y = self.load()
            return {
                "n_samples": X.shape[0],
                "n_features": X.shape[1],
                "feature_names": self.feature_names(),
                "task_type": self.task_type,
                "target_mean": float(np.mean(y)) if task_type == "regression" else None,
                "target_std": float(np.std(y)) if task_type == "regression" else None,
                "feature_scale_ratio": float(
                    np.max(np.std(X, axis=0)) / max(np.min(np.std(X, axis=0)), 1e-12)
                ),
                "features_with_missing": [
                    name for name, col in zip(self.feature_names(), X.T)
                    if np.isnan(col).any()
                ],
            }

    CSVDataset.__name__ = f"CSVDataset_{name}"
    _DATASET_REGISTRY[name] = CSVDataset
    return name
