import json
import time
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


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8044)


if __name__ == "__main__":
    main()