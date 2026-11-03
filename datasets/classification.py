"""分类数据集：sklearn breast_cancer。"""

import numpy as np
from sklearn.datasets import load_breast_cancer

from ..core.base import BaseDataset
from ..core.registry import register_dataset


@register_dataset("breast_cancer")
class BreastCancerDataset(BaseDataset):
    """sklearn breast_cancer 数据集（569 样本 × 30 特征，二分类）。"""

    task_type = "classification"

    def load(self) -> tuple[np.ndarray, np.ndarray]:
        data = load_breast_cancer()
        return data.data, data.target

    def feature_names(self) -> list[str]:
        return list(load_breast_cancer().feature_names)
