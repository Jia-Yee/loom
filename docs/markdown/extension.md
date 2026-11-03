# 扩展指南

## 添加新模型

### 步骤

1. 在 `models/` 下新建文件
2. 继承 `BaseModel`，用 `@register_model` 注册
3. 在 `models/__init__.py` 加一行导入

### 模板

```python
# models/my_model.py
import numpy as np
from sklearn.some_model import SomeModel

from ..core.base import BaseModel
from ..core.registry import register_model


@register_model("my_model")
class MyModel(BaseModel):
    task_type = "regression"  # 或 "classification"

    def __init__(self, alpha=1.0, **kwargs):
        self._model = SomeModel(alpha=alpha, **kwargs)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def get_params(self) -> dict:
        return {
            "alpha": self._model.alpha,
        }

    def param_space(self) -> dict:
        return {
            "alpha": [0.01, 0.1, 1.0, 10.0],
        }
```

```python
# models/__init__.py 加一行
from . import my_model  # noqa: F401
```

### 使用

```python
from loom.core import run
run("my_model", "diabetes")
# 或在 Web 控制台选择 my_model
```

## 添加新数据集

### 步骤

1. 在 `datasets/` 下新建文件
2. 继承 `BaseDataset`，用 `@register_dataset` 注册
3. 在 `datasets/__init__.py` 加一行导入

### 模板

```python
# datasets/my_dataset.py
import numpy as np
from sklearn.datasets import load_some_data

from ..core.base import BaseDataset
from ..core.registry import register_dataset


@register_dataset("my_dataset")
class MyDataset(BaseDataset):
    task_type = "regression"  # 或 "classification"

    def load(self) -> tuple[np.ndarray, np.ndarray]:
        data = load_some_data()
        return data.data, data.target

    def feature_names(self) -> list[str]:
        return list(load_some_data().feature_names)
```

```python
# datasets/__init__.py 加一行
from . import my_dataset  # noqa: F401
```

## 添加新 LLM Provider

在 `core/llm_analyzer.py` 的 `_PROVIDER_DEFAULTS` 中添加：

```python
_PROVIDER_DEFAULTS = {
    "deepseek": {"base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
    "ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen2.5:7b"},
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o"},  # 新增
}
```

只要 provider 支持 OpenAI 兼容接口，加一行即可。

## CSV 动态注册

无需写代码，通过 Web 控制台上传：

1. 左侧面板点击「上传 CSV」
2. 选择文件 → 自动解析列名
3. 选择目标列和任务类型
4. 注册后即可使用

代码方式：

```python
from loom.datasets.csv_loader import register_csv_dataset

register_csv_dataset(
    name="my_csv",
    csv_path="data.csv",
    target_column="price",
    task_type="regression",
)
```
