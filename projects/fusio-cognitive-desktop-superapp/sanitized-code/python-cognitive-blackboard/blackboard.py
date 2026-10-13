"""
Sanitized Reference Implementation: Session Blackboard Architecture
High-performance SQLite WAL working memory and agent trajectory session tree.
"""

import json
import logging
import os
import sqlite3
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SessionBlackboard")


class SessionBlackboard:
    """
    Provides an SQLite WAL-backed scoped key-value store and branching trajectory tree.
    Enables disparate agent loops across isolated context windows to share structured state
    with sub-millisecond memory latency.
    """

    def __init__(self, db_path: str = "blackboard_demo.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                PRAGMA journal_mode = WAL;
                PRAGMA synchronous = NORMAL;

                CREATE TABLE IF NOT EXISTS scoped_kv (
                    session_id TEXT NOT NULL,
                    branch_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, branch_id, key)
                );

                CREATE TABLE IF NOT EXISTS agent_session_tree (
                    node_id TEXT PRIMARY KEY,
                    parent_id TEXT,
                    session_id TEXT NOT NULL,
                    branch_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def set(self, session_id: str, branch_id: str, key: str, value: Any) -> None:
        """Stores a serialized value in scoped working memory"""
        val_json = json.dumps(value)
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO scoped_kv (session_id, branch_id, key, value_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id, branch_id, key) 
                DO UPDATE SET value_json = excluded.value_json, updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, branch_id, key, val_json),
            )

    def get(self, session_id: str, branch_id: str, key: str, fallback_to_main: bool = True) -> Optional[Any]:
        """Retrieves a scoped value with optional fallback to main branch"""
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT value_json FROM scoped_kv WHERE session_id = ? AND branch_id = ? AND key = ?",
                (session_id, branch_id, key),
            )
            row = cur.fetchone()
            if row:
                return json.loads(row["value_json"])

            if fallback_to_main and branch_id != "main":
                cur = conn.execute(
                    "SELECT value_json FROM scoped_kv WHERE session_id = ? AND branch_id = 'main' AND key = ?",
                    (session_id, key),
                )
                row = cur.fetchone()
                if row:
                    return json.loads(row["value_json"])

        return None

    def record_step(
        self,
        node_id: str,
        parent_id: Optional[str],
        session_id: str,
        branch_id: str,
        step_index: int,
        role: str,
        content: str,
    ) -> None:
        """Appends a thought/action step into the branching trajectory tree"""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO agent_session_tree (node_id, parent_id, session_id, branch_id, step_index, role, content)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (node_id, parent_id, session_id, branch_id, step_index, role, content),
            )

    def get_trajectory(self, session_id: str, branch_id: str) -> List[Dict[str, Any]]:
        """Fetches chronological execution steps for a specific branch"""
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT node_id, step_index, role, content, created_at
                FROM agent_session_tree
                WHERE session_id = ? AND branch_id = ?
                ORDER BY step_index ASC
                """,
                (session_id, branch_id),
            )
            return [dict(r) for r in cur.fetchall()]