import json
import sys
import asyncio
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from pydantic import BaseModel


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: Dict[str, Any] = {}


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Any = None
    error: Dict[str, Any] = None


app = FastAPI(title="MCP Server", description="A simple MCP server for getting current time")


@app.post("/")
async def handle_request(request: Request):
    data = await request.json()
    rpc_request = JSONRPCRequest(**data)

    if rpc_request.method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True}
            },
            "serverInfo": {
                "name": "mcp-server-py",
                "version": "0.1.0"
            }
        }
    elif rpc_request.method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "get_current_time",
                    "description": "Get the current date and time",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    elif rpc_request.method == "tools/call":
        tool_name = rpc_request.params.get("name")
        if tool_name == "get_current_time":
            current_time = datetime.now().isoformat()
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": f"Current time: {current_time}"
                    }
                ]
            }
        else:
            return JSONRPCResponse(
                id=rpc_request.id,
                error={"code": -32601, "message": "Method not found"}
            )
    else:
        return JSONRPCResponse(
            id=rpc_request.id,
            error={"code": -32601, "message": "Method not found"}
        )

    return JSONRPCResponse(id=rpc_request.id, result=result)


def handle_stdio_request(rpc_request: JSONRPCRequest) -> JSONRPCResponse:
    """处理 Stdio 请求（同步版本，用于 Stdio 模式）"""
    if rpc_request.method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True}
            },
            "serverInfo": {
                "name": "mcp-server-py",
                "version": "0.1.0"
            }
        }
    elif rpc_request.method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "get_current_time",
                    "description": "Get the current date and time",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    elif rpc_request.method == "tools/call":
        tool_name = rpc_request.params.get("name")
        if tool_name == "get_current_time":
            current_time = datetime.now().isoformat()
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": f"Current time: {current_time}"
                    }
                ]
            }
        else:
            return JSONRPCResponse(
                id=rpc_request.id,
                error={"code": -32601, "message": "Method not found"}
            )
    else:
        return JSONRPCResponse(
            id=rpc_request.id,
            error={"code": -32601, "message": "Method not found"}
        )

    return JSONRPCResponse(id=rpc_request.id, result=result)


async def run_stdio_server():
    """运行 Stdio MCP 服务器"""
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            rpc_request = JSONRPCRequest(**data)
            response = handle_stdio_request(rpc_request)
            response_json = response.model_dump_json()
            print(response_json, flush=True)
        except json.JSONDecodeError:
            error_response = JSONRPCResponse(
                id=None,
                error={"code": -32700, "message": "Parse error"}
            )
            print(error_response.model_dump_json(), flush=True)
        except Exception as e:
            error_response = JSONRPCResponse(
                id=None,
                error={"code": -32603, "message": f"Internal error: {str(e)}"}
            )
            print(error_response.model_dump_json(), flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument("--transport", choices=["http", "stdio"], default="http",
                       help="Transport type: http or stdio")
    args = parser.parse_args()

    if args.transport == "stdio":
        asyncio.run(run_stdio_server())
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8044)


if __name__ == "__main__":
    main()