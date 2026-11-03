"""BaseModel / BaseDataset 接口定义。"""

from abc import ABC, abstractmethod
import numpy as np


class BaseModel(ABC):
    """所有模型的统一接口。新增模型继承此类并用 @register_model 注册。"""

    task_type: str = "regression"

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        ...

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        ...

    @abstractmethod
    def get_params(self) -> dict:
        """返回模型当前参数，用于节点展示。"""
        ...

    def param_space(self) -> dict:
        """超参数搜索空间，供演进三使用。本期可返回空。"""
        return {}


class BaseDataset(ABC):
    """所有数据集的统一接口。新增数据集继承此类并用 @register_dataset 注册。"""

    task_type: str = "regression"

    @abstractmethod
    def load(self) -> tuple[np.ndarray, np.ndarray]:
        """返回 (X, y)。"""
        ...

    @abstractmethod
    def feature_names(self) -> list[str]:
        """返回特征名列表。"""
        ...

    def summary(self) -> dict:
        """数据集摘要，供 LLM 分析使用。子类可覆盖以补充信息。"""
        X, y = self.load()
        return {
            "n_samples": X.shape[0],
            "n_features": X.shape[1],
            "feature_names": self.feature_names(),
            "task_type": self.task_type,
            "target_mean": float(np.mean(y)),
            "target_std": float(np.std(y)),
            "feature_scale_ratio": float(
                np.max(np.std(X, axis=0)) / max(np.min(np.std(X, axis=0)), 1e-12)
            ),
            "features_with_missing": [
                name
                for name, col in zip(self.feature_names(), X.T)
                if np.isnan(col).any()
            ],
        }
