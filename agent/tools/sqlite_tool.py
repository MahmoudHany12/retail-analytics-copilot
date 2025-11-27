# agent/tools/sqlite_tool.py
import sqlite3
from typing import Tuple, List, Dict, Any, Optional

class SQLiteTool:
    """
    Lightweight wrapper around sqlite3 for deterministic execution + schema introspection.
    Compatible with DSPy + LangGraph HybridAgent for NL2SQL queries.
    """

    def __init__(self, path: str):
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        """Establish connection if not already connected."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = sqlite3.Row  # fetch results as dict-like

    def close(self):
        """Close DB connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def list_tables(self) -> List[str]:
        """Return list of tables in the database."""
        self.connect()
        cur = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        return [r[0] for r in cur.fetchall()]

    def pragma_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Return PRAGMA table_info for schema introspection."""
        self.connect()
        cur = self.conn.execute(f"PRAGMA table_info('{table_name}')")
        rows = cur.fetchall()
        return [
            {
                "cid": r["cid"],
                "name": r["name"],
                "type": r["type"],
                "notnull": r["notnull"],
                "dflt_value": r["dflt_value"],
                "pk": r["pk"]
            } for r in rows
        ]

    def execute(self, sql: str, params: Tuple = ()) -> Dict[str, Any]:
        """
        Execute SQL query or statement.
        Returns a dict with keys: ok, error, columns, rows, rowcount
        """
        self.connect()
        try:
            cur = self.conn.execute(sql, params)
            # If SELECT statement
            if cur.description is not None:
                columns = [c[0] for c in cur.description]
                rows = [dict(r) for r in cur.fetchall()]
                return {"ok": True, "error": None, "columns": columns, "rows": rows, "rowcount": len(rows)}
            else:
                self.conn.commit()
                return {"ok": True, "error": None, "columns": [], "rows": [], "rowcount": cur.rowcount}
        except Exception as e:
            return {"ok": False, "error": str(e), "columns": [], "rows": [], "rowcount": 0}

    # Optional convenience method for raw SELECT returning only rows
    def query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        result = self.execute(sql, params)
        if result["ok"]:
            return result["rows"]
        else:
            raise RuntimeError(f"SQLiteTool query error: {result['error']}")
