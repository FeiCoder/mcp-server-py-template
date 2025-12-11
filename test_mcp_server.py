#!/usr/bin/env python3
"""
测试脚本，用于测试 MCP 服务器的功能。
确保服务器已在后台运行（uv run mcp-server）。
"""

import json
import requests
import time


def send_request(method, params=None, request_id=1):
    """发送 JSON-RPC 请求到 MCP 服务器"""
    url = "http://localhost:8044/"
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params:
        payload["params"] = params

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def test_initialize():
    """测试 initialize 方法"""
    print("测试 initialize...")
    result = send_request("initialize")
    if result:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        assert "result" in result
        assert result["result"]["serverInfo"]["name"] == "mcp-server-py"
        print("✓ initialize 测试通过")
    else:
        print("✗ initialize 测试失败")


def test_tools_list():
    """测试 tools/list 方法"""
    print("\n测试 tools/list...")
    result = send_request("tools/list")
    if result:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        assert "result" in result
        tools = result["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "get_current_time"
        print("✓ tools/list 测试通过")
    else:
        print("✗ tools/list 测试失败")


def test_tools_call():
    """测试 tools/call 方法"""
    print("\n测试 tools/call (get_current_time)...")
    result = send_request("tools/call", {"name": "get_current_time"})
    if result:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        assert "result" in result
        content = result["result"]["content"]
        assert len(content) == 1
        assert "Current time:" in content[0]["text"]
        print("✓ tools/call 测试通过")
    else:
        print("✗ tools/call 测试失败")


def main():
    """运行所有测试"""
    print("开始测试 MCP 服务器...")
    print("请确保服务器已在运行: uv run mcp-server")

    # 等待服务器启动
    time.sleep(2)

    try:
        test_initialize()
        test_tools_list()
        test_tools_call()
        print("\n🎉 所有测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()