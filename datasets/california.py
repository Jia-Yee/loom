"""示例：新增 California Housing 数据集（回归）。"""

import numpy as np
from sklearn.datasets import fetch_california_housing

from ..core.base import BaseDataset
from ..core.registry import register_dataset


@register_dataset("california_housing")
class CaliforniaHousingDataset(BaseDataset):
    """加州房价数据集（20640 样本 × 8 特征，回归任务）。"""

    task_type = "regression"

    def load(self) -> tuple[np.ndarray, np.ndarray]:
        data = fetch_california_housing()
        return data.data, data.target

    def feature_names(self) -> list[str]:
        return list(fetch_california_housing().feature_names)
