import argparse
import json
from text2sql import Text2SQL
from typing import List


def print_result(result):
    print("\n" + "=" * 60)
    print(f"生成状态: {'成功' if result.success else '失败'}")
    print(f"尝试次数: {result.attempts}")
    print(f"\n最终 SQL:\n{result.sql}")

    if result.results:
        print(f"\n查询结果 (共 {len(result.results)} 行):")
        print(json.dumps(result.results[:10], indent=2, ensure_ascii=False))
        if len(result.results) > 10:
            print(f"... 还有 {len(result.results) - 10} 行")

    if result.error:
        print(f"\n错误信息:\n{result.error}")

    if result.attempt_history and len(result.attempt_history) > 1:
        print("\n修正历史:")
        for attempt in result.attempt_history:
            print(f"\n--- 尝试 {attempt['attempt']} ---")
            print(f"SQL: {attempt['sql']}")
            if attempt.get("error"):
                print(f"错误: {attempt['error']}")

    print("=" * 60)


def interactive_mode():
    text2sql = Text2SQL()

    print("\n" + "=" * 60)
    print("Text2SQL 交互模式")
    print("=" * 60)

    schemas = text2sql.get_available_schemas()
    print(f"\n可用 schema: {', '.join(schemas)}")

    schema = input("\n请输入 schema 名称 (默认 public): ").strip()
    if not schema:
        schema = "public"

    tables = text2sql.get_tables_in_schema(schema)
    print(f"\n可用表: {', '.join(tables)}")

    selected_tables = input(
        "\n请输入要使用的表名 (多个表用逗号分隔，默认全部): "
    ).strip()
    if selected_tables:
        tables = [t.strip() for t in selected_tables.split(",")]
    else:
        selected_all = input("是否使用所有表? (y/n): ").strip().lower()
        if selected_all != "y":
            tables = input("请输入表名: ").strip().split(",")
            tables = [t.strip() for t in tables]

    print(f"\n已选择表: {', '.join(tables)}")

    while True:
        print("\n" + "-" * 60)
        question = input("\n请输入自然语言问题 (输入 'quit' 退出): ").strip()

        if question.lower() in ["quit", "exit", "q"]:
            break

        if not question:
            continue

        execute = (
            input("是否执行 SQL? (y/n, 默认 y): ").strip().lower() != "n"
        )

        result = text2sql.generate_sql(question, schema, tables, execute)
        print_result(result)


def single_query_mode(
    schema: str,
    tables: List[str],
    question: str,
    execute: bool = True,
):
    text2sql = Text2SQL()
    result = text2sql.generate_sql(question, schema, tables, execute)
    print_result(result)


def main():
    parser = argparse.ArgumentParser(description="Text2SQL - 自然语言转 SQL 工具")
    parser.add_argument("--schema", type=str, default="public", help="数据库 schema")
    parser.add_argument("--tables", type=str, help="表名列表 (逗号分隔)")
    parser.add_argument("--question", type=str, help="自然语言问题")
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="只生成 SQL，不执行",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="交互模式",
    )

    args = parser.parse_args()

    if args.interactive or not args.question:
        interactive_mode()
    else:
        tables = args.tables.split(",") if args.tables else []
        single_query_mode(
            args.schema, tables, args.question, execute=not args.no_execute
        )


if __name__ == "__main__":
    main()
