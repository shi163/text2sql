from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from database import DatabaseConnector
from llm_client import LLMClient
from config import config


@dataclass
class SQLGenerationResult:
    success: bool
    sql: str
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    attempts: int = 0
    attempt_history: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.attempt_history is None:
            self.attempt_history = []


class Text2SQL:
    def __init__(self):
        self.db = DatabaseConnector()
        self.llm = LLMClient()
        self.max_attempts = config.max_retry_attempts

    def get_available_schemas(self) -> List[str]:
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT schema_name FROM information_schema.schemata"
                )
                return [row[0] for row in cur.fetchall()]

    def get_tables_in_schema(self, schema: str) -> List[str]:
        return self.db.get_schema_tables(schema)

    def generate_sql(
        self,
        question: str,
        schema: str,
        tables: List[str],
        execute: bool = True,
    ) -> SQLGenerationResult:
        table_context = self.db.get_tables_context(schema, tables)

        attempt = 1
        sql = self.llm.generate_sql(table_context, question)
        attempt_history = [
            {"attempt": 1, "sql": sql, "error": None}
        ]

        if execute:
            success, results, error = self._execute_with_retry(
                sql, table_context, question, attempt_history
            )

            return SQLGenerationResult(
                success=success,
                sql=sql,
                results=results if success else None,
                error=error if not success else None,
                attempts=len(attempt_history),
                attempt_history=attempt_history,
            )
        else:
            return SQLGenerationResult(
                success=True,
                sql=sql,
                attempts=1,
                attempt_history=attempt_history,
            )

    def _execute_with_retry(
        self,
        initial_sql: str,
        table_context: str,
        question: str,
        attempt_history: List[Dict[str, str]],
    ) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        sql = initial_sql

        for attempt in range(1, self.max_attempts + 1):
            success, results, error = self.db.execute_sql(sql)

            if success:
                return True, results, None

            if attempt < self.max_attempts:
                print(f"尝试 {attempt} 失败: {error}")
                print(f"正在修正 SQL...")

                sql = self.llm.fix_sql(
                    table_context, question, sql, error
                )

                attempt_history.append(
                    {"attempt": attempt + 1, "sql": sql, "error": error}
                )

        return False, None, f"达到最大尝试次数 ({self.max_attempts})，最后的错误: {error}"

    def generate_sql_with_validation(
        self,
        question: str,
        schema: str,
        tables: List[str],
    ) -> SQLGenerationResult:
        table_context = self.db.get_tables_context(schema, tables)

        attempt = 1
        sql = self.llm.generate_sql(table_context, question)
        attempt_history = [
            {"attempt": 1, "sql": sql, "error": None}
        ]

        valid, error = self.db.validate_sql(sql)

        if valid:
            return SQLGenerationResult(
                success=True,
                sql=sql,
                attempts=1,
                attempt_history=attempt_history,
            )

        print(f"SQL 验证失败: {error}")
        print("正在修正 SQL...")

        for attempt in range(2, self.max_attempts + 1):
            sql = self.llm.fix_sql(table_context, question, sql, error)
            attempt_history.append(
                {"attempt": attempt, "sql": sql, "error": error}
            )

            valid, error = self.db.validate_sql(sql)

            if valid:
                return SQLGenerationResult(
                    success=True,
                    sql=sql,
                    attempts=attempt,
                    attempt_history=attempt_history,
                )

            print(f"尝试 {attempt} 失败: {error}")
            print("正在修正 SQL...")

        return SQLGenerationResult(
            success=False,
            sql=sql,
            error=f"达到最大尝试次数 ({self.max_attempts})，最后的错误: {error}",
            attempts=self.max_attempts,
            attempt_history=attempt_history,
        )
