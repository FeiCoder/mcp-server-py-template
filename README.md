# mcp-server-py-template

一个 Python MCP (Model Context Protocol) 服务器，通过 HTTP 提供当前时间功能。

## 功能

- 通过 HTTP 实现 MCP 协议
- 提供获取当前日期和时间的工具

## 安装

确保安装了 `uv`。如果没有，请从 [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv) 安装。

克隆仓库并安装依赖：

```bash
git clone https://github.com/FeiCoder/mcp-server-py-template.git
cd mcp-server-py-template
uv sync
```

## 使用

运行服务器：

```bash
uv run mcp-server
```

服务器将在 `http://0.0.0.0:8000` 上启动。

## MCP 协议

此服务器实现 MCP 协议用于工具调用。它支持：

- `initialize`：初始化连接
- `tools/list`：列出可用工具
- `tools/call`：调用工具

可用工具：

- `get_current_time`：返回当前日期和时间（ISO 格式）

## 开发

在开发模式下运行：

```bash
uv run uvicorn mcp_server.main:app --reload
```

## 测试

运行测试脚本以验证服务器功能：

```bash
# 首先启动服务器（在新终端中）
uv run mcp-server

# 然后运行测试
uv run python test_mcp_server.py
```

测试脚本将验证：
- 初始化连接
- 列出可用工具
- 调用 `get_current_time` 工具
