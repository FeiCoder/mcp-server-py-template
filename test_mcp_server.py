#!/usr/bin/env python3
"""
测试脚本，用于测试 MCP 服务器的功能。
确保服务器已在后台运行（uv run mcp-server）或使用 stdio 模式。
"""

import json
import subprocess
import sys
import requests
import time


def send_http_request(method, params=None, request_id=1):
    """发送 HTTP 请求到 MCP 服务器"""
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
        print(f"HTTP 请求失败: {e}")
        return None


def send_stdio_request(method, params=None, request_id=1):
    """通过 stdio 发送请求到 MCP 服务器"""
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params:
        payload["params"] = params

    try:
        process = subprocess.Popen(
            ["uv", "run", "mcp-server", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/data/zf/codes/mcp-server-py-template"
        )
        input_data = json.dumps(payload) + "\n"
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        if stderr:
            print(f"Stdio 错误: {stderr}")
        if stdout:
            return json.loads(stdout.strip())
        return None
    except subprocess.TimeoutExpired:
        process.kill()
        print("Stdio 请求超时")
        return None
    except Exception as e:
        print(f"Stdio 请求失败: {e}")
        return None


def test_transport(transport_func, transport_name):
    """测试指定传输方式"""
    print(f"\n=== 测试 {transport_name} 传输 ===")

    # 测试 initialize
    print("测试 initialize...")
    result = transport_func("initialize")
    if result:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        assert "result" in result
        assert result["result"]["serverInfo"]["name"] == "mcp-server-py"
        print("✓ initialize 测试通过")
    else:
        print("✗ initialize 测试失败")
        return False

    # 测试 tools/list
    print("测试 tools/list...")
    result = transport_func("tools/list")
    if result:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        assert "result" in result
        tools = result["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "get_current_time"
        print("✓ tools/list 测试通过")
    else:
        print("✗ tools/list 测试失败")
        return False

    # 测试 tools/call
    print("测试 tools/call (get_current_time)...")
    result = transport_func("tools/call", {"name": "get_current_time"})
    if result:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        assert "result" in result
        content = result["result"]["content"]
        assert len(content) == 1
        assert "Current time:" in content[0]["text"]
        print("✓ tools/call 测试通过")
    else:
        print("✗ tools/call 测试失败")
        return False

    return True


def main():
    """运行所有测试"""
    print("开始测试 MCP 服务器...")

    # 测试 HTTP 传输
    http_success = test_transport(send_http_request, "HTTP")

    # 测试 Stdio 传输
    stdio_success = test_transport(send_stdio_request, "Stdio")

    if http_success and stdio_success:
        print("\n🎉 所有测试通过！服务器支持 HTTP 和 Stdio 传输。")
    else:
        print("\n❌ 部分测试失败。")


if __name__ == "__main__":
    main()