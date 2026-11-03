"""sklearn 自带 toy 数据集：diabetes。"""

import numpy as np
from sklearn.datasets import load_diabetes

from ..core.base import BaseDataset
from ..core.registry import register_dataset


@register_dataset("diabetes")
class DiabetesDataset(BaseDataset):
    """sklearn diabetes 数据集（442 样本 × 10 特征，回归任务）。"""

    task_type = "regression"

    def load(self) -> tuple[np.ndarray, np.ndarray]:
        data = load_diabetes()
        return data.data, data.target

    def feature_names(self) -> list[str]:
        return list(load_diabetes().feature_names)
