SYSTEM_PROMPT = """你是一个专业的 SQL 查询生成助手。你的任务是根据用户的自然语言问题和数据库表结构，生成准确的 SQL 查询语句。

重要规则：
1. 只返回 SQL 查询语句，不要包含任何解释或注释
2. SQL 语句必须符合 PostgreSQL 语法
3. 正确使用表名和字段名（注意大小写敏感性）
4. 合理使用 JOIN、WHERE、GROUP BY、ORDER BY 等子句
5. 对于模糊查询，使用 ILIKE 进行大小写不敏感匹配
6. 对于日期查询，使用正确的 PostgreSQL 日期函数
7. 注意处理 NULL 值
8. 对于聚合查询，正确使用 HAVING 子句
"""

GENERATE_SQL_PROMPT = """数据库表结构：
{table_context}

用户问题：{question}

请生成对应的 SQL 查询语句：
"""

FIX_SQL_PROMPT = """数据库表结构：
{table_context}

用户问题：{question}

之前生成的 SQL：
```sql
{previous_sql}
```

执行错误信息：
{error_message}

请根据错误信息修正 SQL 查询语句。注意：
1. 仔细分析错误原因
2. 检查表名和字段名是否正确
3. 检查 SQL 语法是否正确
4. 返回修正后的 SQL 语句，不要包含任何解释：
"""

EXAMPLES_PROMPT = """
示例问题与 SQL：

示例1：
问题: 查询所有用户
SQL: SELECT * FROM users;

示例2：
问题: 查询年龄大于18岁的用户姓名
SQL: SELECT name FROM users WHERE age > 18;

示例3：
问题: 统计每个部门的员工数量
SQL: SELECT department_id, COUNT(*) as employee_count FROM employees GROUP BY department_id;

示例4：
问题: 查询订单金额最高的前10个订单
SQL: SELECT * FROM orders ORDER BY amount DESC LIMIT 10;

示例5：
问题: 查询用户名为"张三"的订单信息
SQL: SELECT o.* FROM orders o JOIN users u ON o.user_id = u.id WHERE u.name = '张三';
"""
