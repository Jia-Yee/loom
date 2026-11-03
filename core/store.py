"""SQLite 持久化：save_run / list_runs / get_run。"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Optional


def _db_path() -> str:
    return os.environ.get("AUTOML_DB_PATH", "") or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "automl.db"
    )


def _connect() -> sqlite3.Connection:
    db_path = _db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    return conn


def _init_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id       TEXT PRIMARY KEY,
            dataset_name TEXT NOT NULL,
            timestamp    TEXT NOT NULL,
            best_model   TEXT,
            nodes        TEXT,           -- 完整 nodes JSON（新增）
            edges        TEXT            -- 完整 edges JSON（新增）
        );

        CREATE TABLE IF NOT EXISTS metrics (
            run_id      TEXT NOT NULL,
            model_name  TEXT NOT NULL,
            task_type   TEXT NOT NULL,
            metrics     TEXT NOT NULL,  -- JSON
            params      TEXT,           -- 模型参数 JSON（新增）
            search_info TEXT,           -- 搜索信息 JSON（新增）
            PRIMARY KEY (run_id, model_name),
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        );

        CREATE TABLE IF NOT EXISTS llm_analysis (
            run_id       TEXT NOT NULL,
            model_name   TEXT,          -- pre_train 时为 NULL
            stage        TEXT NOT NULL,
            content      TEXT NOT NULL,
            structured   TEXT,          -- JSON 或 NULL
            parse_failed INTEGER NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        );
    """)
    # 兼容旧库：如果表已存在但缺列，自动补列
    for col, ddl in [("nodes", "TEXT"), ("edges", "TEXT")]:
        try:
            conn.execute(f"ALTER TABLE runs ADD COLUMN {col} {ddl}")
        except sqlite3.OperationalError:
            pass  # 列已存在
    for col, ddl in [("params", "TEXT"), ("search_info", "TEXT")]:
        try:
            conn.execute(f"ALTER TABLE metrics ADD COLUMN {col} {ddl}")
        except sqlite3.OperationalError:
            pass
    conn.commit()


def save_run(result: dict, dataset_name: str) -> None:
    """将一次 run() 结果写入 SQLite。"""
    conn = _connect()
    try:
        run_id = result["run_id"]
        best_model = result.get("best_model")
        ts = datetime.now().isoformat()
        nodes_json = json.dumps(result.get("nodes", []), ensure_ascii=False)
        edges_json = json.dumps(result.get("edges", []), ensure_ascii=False)

        conn.execute(
            "INSERT OR REPLACE INTO runs (run_id, dataset_name, timestamp, best_model, nodes, edges) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, dataset_name, ts, best_model, nodes_json, edges_json),
        )

        # metrics 表（含参数和搜索信息）
        for model_name, m in result["metrics"].items():
            task_type = "regression"
            params = None
            search_info = None
            for node in result.get("nodes", []):
                if node["type"] == "dataset":
                    task_type = node["display"].get("task_type", "regression")
                if node["type"] == "model" and node["display"].get("model_name") == model_name:
                    params = json.dumps(node["display"].get("params"), ensure_ascii=False)
                    search_info = json.dumps(node["display"].get("search_info"), ensure_ascii=False)
            conn.execute(
                "INSERT OR REPLACE INTO metrics (run_id, model_name, task_type, metrics, params, search_info) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, model_name, task_type, json.dumps(m, ensure_ascii=False), params, search_info),
            )

        # llm_analysis 表
        for node in result.get("nodes", []):
            if node["type"] != "llm_analysis":
                continue
            d = node["display"]
            conn.execute(
                "INSERT INTO llm_analysis (run_id, model_name, stage, content, structured, parse_failed) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    run_id,
                    d.get("model_name"),
                    d["stage"],
                    d.get("content", ""),
                    json.dumps(d.get("structured"), ensure_ascii=False) if d.get("structured") else None,
                    1 if d.get("parse_failed") else 0,
                ),
            )

        conn.commit()
        print(f"✓ 结果已持久化: {_db_path()}")
    finally:
        conn.close()


def list_runs(dataset_name: Optional[str] = None, limit: int = 20) -> list[dict]:
    """查询历史运行摘要。"""
    conn = _connect()
    try:
        if dataset_name:
            rows = conn.execute(
                "SELECT * FROM runs WHERE dataset_name=? ORDER BY timestamp DESC LIMIT ?",
                (dataset_name, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM runs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_run(run_id: str) -> dict:
    """查询单次运行的完整结果。"""
    conn = _connect()
    try:
        run = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not run:
            raise KeyError(f"run_id '{run_id}' 不存在")

        metrics_rows = conn.execute(
            "SELECT * FROM metrics WHERE run_id=?", (run_id,)
        ).fetchall()
        llm_rows = conn.execute(
            "SELECT * FROM llm_analysis WHERE run_id=?", (run_id,)
        ).fetchall()

        return {
            "run": dict(run),
            "metrics": {
                r["model_name"]: json.loads(r["metrics"]) for r in metrics_rows
            },
            "llm_analysis": [
                {
                    "model_name": r["model_name"],
                    "stage": r["stage"],
                    "content": r["content"],
                    "structured": json.loads(r["structured"]) if r["structured"] else None,
                    "parse_failed": bool(r["parse_failed"]),
                }
                for r in llm_rows
            ],
        }
    finally:
        conn.close()
