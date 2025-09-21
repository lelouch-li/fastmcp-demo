#!/usr/bin/env python3
"""
认证测试工具
测试 FastAPI Basic Auth 和 FastMCP Bearer Token 认证
"""

import asyncio
import base64
import json
import httpx
from fastmcp import Client


async def test_fastapi_auth():
    """测试 FastAPI Basic Authentication"""
    print("=== 测试 FastAPI Basic Authentication ===")
    
    # 正确的认证信息
    correct_auth = ("admin", "admin")
    
    # 错误的认证信息
    wrong_auth = ("wrong", "wrong")
    
    async with httpx.AsyncClient() as client:
        # 测试无认证访问
        print("1. 测试无认证访问...")
        try:
            response = await client.get("http://localhost:8000/stocks")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ 正确拒绝无认证访问")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        # 测试错误认证
        print("2. 测试错误认证...")
        try:
            response = await client.get(
                "http://localhost:8000/stocks",
                auth=wrong_auth
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ 正确拒绝错误认证")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        # 测试正确认证
        print("3. 测试正确认证...")
        try:
            response = await client.get(
                "http://localhost:8000/stocks",
                auth=correct_auth
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 认证成功，获取到 {len(data)} 条股票数据")
            else:
                print(f"   ❌ 认证失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        # 测试受保护的端点
        print("4. 测试受保护的端点...")
        try:
            response = await client.get(
                "http://localhost:8000/protected",
                auth=correct_auth
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功访问受保护端点: {data['message']}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    print()


async def test_fastmcp_auth():
    """测试 FastMCP Bearer Token Authentication"""
    print("=== 测试 FastMCP Bearer Token Authentication ===")
    
    # Bearer token (base64 编码的 admin:admin)
    token = base64.b64encode("admin:admin".encode()).decode()
    
    # 测试健康检查端点（无需认证）
    print("1. 测试健康检查端点（无需认证）...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {data}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试认证信息端点
    print("2. 测试认证信息端点...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/auth-info")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Bearer Token: {data['example_token']}")
                print("   ✅ 获取认证信息成功")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试 MCP 端点（需要认证）
    print("3. 测试 MCP 端点（无认证）...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/mcp/")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ 正确拒绝无认证访问")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试带认证的 MCP 客户端连接
    print("4. 测试带认证的 MCP 客户端连接...")
    try:
        # 使用 FastMCP 客户端连接
        async with Client(
            "http://localhost:8001/mcp/",
            auth=token  # 直接传递 token，FastMCP 会自动添加 Bearer 前缀
        ) as mcp_client:
            # 测试 ping
            await mcp_client.ping()
            print("   ✅ MCP 客户端连接成功")
            
            # 列出资源
            resources = await mcp_client.list_resources()
            print(f"   ✅ 获取到 {len(resources)} 个资源")
            for resource in resources[:3]:  # 显示前3个资源
                print(f"      - {resource.uri}: {resource.name}")
            
            # 列出工具
            tools = await mcp_client.list_tools()
            print(f"   ✅ 获取到 {len(tools)} 个工具")
            for tool in tools[:3]:  # 显示前3个工具
                print(f"      - {tool.name}: {tool.description}")
            
            # 调用一个工具
            result = await mcp_client.call_tool("get_stock_stats", {})
            print("   ✅ 成功调用 get_stock_stats 工具")
            print(f"      股票总数: {result.data['stats']['总数']}")
            
    except Exception as e:
        print(f"   ❌ MCP 客户端连接错误: {e}")
    
    print()


async def test_http_requests():
    """使用原始 HTTP 请求测试认证"""
    print("=== 测试原始 HTTP 请求 ===")
    
    token = base64.b64encode("admin:admin".encode()).decode()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # 测试直接 HTTP 请求到 MCP 端点
        try:
            response = await client.post(
                "http://localhost:8001/mcp/",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "ping",
                    "params": {}
                }
            )
            print(f"MCP Ping 请求状态码: {response.status_code}")
            if response.status_code == 200:
                print("✅ 直接 HTTP 请求成功")
                # print(f"响应: {response.json()}")
        except Exception as e:
            print(f"❌ 直接 HTTP 请求失败: {e}")


def print_auth_info():
    """打印认证信息"""
    print("=== 认证信息 ===")
    token = base64.b64encode("admin:admin".encode()).decode()
    print(f"用户名: admin")
    print(f"密码: admin")
    print(f"Bearer Token: {token}")
    print(f"Authorization Header: Bearer {token}")
    print()


async def main():
    """主测试函数"""
    print("FastMCP 股票管理系统认证测试")
    print("=" * 50)
    print()
    
    print_auth_info()
    
    print("请确保以下服务已启动:")
    print("1. FastAPI 服务器: python3 stock_api.py (端口 8000)")
    print("2. FastMCP 服务器: python3 stock_mcp_server.py (端口 8001)")
    print()
    
    input("按 Enter 键开始测试...")
    print()
    
    # 测试 FastAPI Basic Auth
    await test_fastapi_auth()
    
    # 测试 FastMCP Bearer Token Auth
    await test_fastmcp_auth()
    
    # 测试原始 HTTP 请求
    await test_http_requests()
    
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
