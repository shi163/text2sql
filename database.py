import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from config import config


class DatabaseConnector:
    def __init__(self):
        self.conn_params = {
            "host": config.database.host,
            "port": config.database.port,
            "database": config.database.database,
            "user": config.database.user,
            "password": config.database.password,
        }

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**self.conn_params)
        try:
            yield conn
        finally:
            conn.close()

    def get_schema_tables(self, schema: str = "public") -> List[str]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    ORDER BY table_name
                """
                cur.execute(query, (schema,))
                return [row[0] for row in cur.fetchall()]

    def get_table_structure(self, schema: str, table: str) -> Dict[str, Any]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                columns_query = """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """
                cur.execute(columns_query, (schema, table))
                columns = cur.fetchall()

                pk_query = """
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    JOIN pg_class c ON c.oid = i.indrelid
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE i.indisprimary
                    AND n.nspname = %s
                    AND c.relname = %s
                """
                cur.execute(pk_query, (schema, table))
                primary_keys = [row[0] for row in cur.fetchall()]

                fk_query = """
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table,
                        ccu.column_name AS foreign_column
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = %s
                    AND tc.table_name = %s
                """
                cur.execute(fk_query, (schema, table))
                foreign_keys = cur.fetchall()

                return {
                    "table_name": table,
                    "schema": schema,
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2] == "YES",
                            "default": col[3],
                        }
                        for col in columns
                    ],
                    "primary_keys": primary_keys,
                    "foreign_keys": [
                        {"column": fk[0], "ref_table": fk[1], "ref_column": fk[2]}
                        for fk in foreign_keys
                    ],
                }

    def get_tables_context(self, schema: str, tables: List[str]) -> str:
        context_parts = []
        for table in tables:
            structure = self.get_table_structure(schema, table)
            context_parts.append(self._format_table_structure(structure))
        return "\n\n".join(context_parts)

    def _format_table_structure(self, structure: Dict[str, Any]) -> str:
        lines = [f"表名: {structure['schema']}.{structure['table_name']}"]
        lines.append("字段:")
        for col in structure["columns"]:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            default = f"DEFAULT {col['default']}" if col["default"] else ""
            lines.append(
                f"  - {col['name']} ({col['type']}) {nullable} {default}"
            )
        if structure["primary_keys"]:
            lines.append(f"主键: {', '.join(structure['primary_keys'])}")
        if structure["foreign_keys"]:
            lines.append("外键:")
            for fk in structure["foreign_keys"]:
                lines.append(
                    f"  - {fk['column']} -> {fk['ref_table']}.{fk['ref_column']}"
                )
        return "\n".join(lines)

    def execute_sql(
        self, sql_query: str
    ) -> tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_query)
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        results = [
                            dict(zip(columns, row)) for row in rows
                        ]
                        return True, results, None
                    conn.commit()
                    return True, None, None
        except Exception as e:
            return False, None, str(e)

    def validate_sql(self, sql_query: str) -> tuple[bool, Optional[str]]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"EXPLAIN {sql_query}")
                return True, None
        except Exception as e:
            return False, str(e)
