 
# text2sql
NL2SQL project generated using Codex, with test accuracy metrics

# Text2SQL 项目

自然语言转 SQL 查询系统，支持 PostgreSQL 数据库，包含智能 SQL 生成与自动修正功能。

## 功能特性

- 自然语言转 SQL 查询
- 支持 PostgreSQL 数据库
- 自动获取表结构和关系
- SQL 执行错误自动修正
- 支持交互式和命令行模式

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

配置项：
- `DATABASE_*`: PostgreSQL 数据库连接信息
- `LLM_*`: LLM API 配置（支持 OpenAI 兼容接口）

## 使用方式

### 交互模式

```bash
python main.py -i
```

### 命令行模式

```bash
python main.py --schema public --tables users,orders --question "查询所有用户"
```

### 仅生成 SQL（不执行）

```bash
python main.py --schema public --tables users --question "查询所有用户" --no-execute
```

## 项目结构

```
text2sql/
├── config.py          # 配置管理
├── database.py        # 数据库连接和操作
├── llm_client.py      # LLM API 客户端
├── prompts.py         # Prompt 模板
├── text2sql.py        # 核心逻辑
├── main.py            # 入口程序
├── requirements.txt   # 依赖
├── .env.example       # 配置示例
└── README.md          # 文档
```

## 核心流程

1. 用户输入自然语言问题和目标表
2. 系统获取表结构信息（字段、类型、主键、外键）
3. 将表结构和问题发送给 LLM 生成 SQL
4. 尝试执行 SQL
5. 如果失败，将错误信息反馈给 LLM 进行修正
6. 循环直到成功或达到最大尝试次数

## Prompt 设计

系统使用分层的 Prompt 策略：

1. **System Prompt**: 定义角色和基本规则
2. **生成 Prompt**: 包含表结构和用户问题
3. **修正 Prompt**: 包含错误信息和历史 SQL

关键原则：
- 明确返回格式要求
- 提供具体的 SQL 语法规则
- 包含常见模式和示例
- 清晰的错误上下文

## 扩展建议

1. **添加缓存**: 缓存相似问题的 SQL
2. **Few-shot 学习**: 添加领域相关的示例
3. **SQL 验证**: 语法检查和安全检查
4. **多轮对话**: 支持上下文相关的查询
5. **可视化**: 添加查询结果可视化功能

 
