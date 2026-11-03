# 模型文档

## linear_regression（线性回归）

- **类型**：回归
- **注册名**：`linear_regression`
- **实现**：包装 sklearn `LinearRegression`

### 接口

| 方法 | 说明 |
|------|------|
| `fit(X, y)` | 训练模型 |
| `predict(X)` | 预测 |
| `get_params()` | 返回 fit_intercept, copy_X, coef, intercept |
| `param_space()` | `{"fit_intercept": [True, False]}` |

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| fit_intercept | bool | True | 是否拟合截距 |
| copy_X | bool | True | 是否复制 X |

### 使用示例

```python
from loom.core import run
result = run("linear_regression", "diabetes")
# metrics: {"mse": 2900.19, "r2": 0.4526}
```

---

## random_forest（随机森林）

- **类型**：回归
- **注册名**：`random_forest`
- **实现**：包装 sklearn `RandomForestRegressor`

### 接口

| 方法 | 说明 |
|------|------|
| `fit(X, y)` | 训练模型 |
| `predict(X)` | 预测 |
| `get_params()` | 返回 n_estimators, max_depth, n_features_in_ |
| `param_space()` | `{"n_estimators": [50, 100, 200], "max_depth": [None, 5, 10, 20]}` |

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| n_estimators | int | 100 | 树的数量 |
| max_depth | int/None | None | 树的最大深度 |

### 超参搜索

```python
run("random_forest", "diabetes", search=True, n_iter=10, cv=5)
```

---

## ridge（Ridge 回归）

- **类型**：回归
- **注册名**：`ridge`
- **实现**：包装 sklearn `Ridge`

### 接口

| 方法 | 说明 |
|------|------|
| `fit(X, y)` | 训练模型 |
| `predict(X)` | 预测 |
| `get_params()` | 返回 alpha, solver |
| `param_space()` | `{"alpha": [0.01, 0.1, 1.0, 10.0, 100.0]}` |

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| alpha | float | 1.0 | 正则化强度 |
| solver | str | auto | 求解算法 |

---

## logistic_regression（逻辑回归）

- **类型**：分类
- **注册名**：`logistic_regression`
- **实现**：包装 sklearn `LogisticRegression`

### 接口

| 方法 | 说明 |
|------|------|
| `fit(X, y)` | 训练模型 |
| `predict(X)` | 预测类别 |
| `get_params()` | 返回 C, max_iter, solver, n_features_in_ |
| `param_space()` | `{"C": [0.01, 0.1, 1.0, 10.0, 100.0], "solver": ["lbfgs", "liblinear"]}` |

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| C | float | 1.0 | 正则化强度的倒数 |
| max_iter | int | 5000 | 最大迭代次数 |
| solver | str | lbfgs | 优化算法 |

### 使用示例

```python
from loom.core import run
result = run("logistic_regression", "breast_cancer")
# metrics: {"accuracy": 0.9649, "f1": 0.9647, "auc": 0.9954}
```
