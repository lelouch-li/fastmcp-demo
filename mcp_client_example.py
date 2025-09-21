#!/usr/bin/env python3
"""
FastMCP 客户端示例
展示如何使用 Bearer Token 认证连接到股票信息 MCP 服务器
"""

import asyncio
import base64
from fastmcp import Client


async def demonstrate_mcp_client():
    """演示 MCP 客户端功能"""
    print("FastMCP 股票信息客户端演示")
    print("=" * 40)
    
    # 创建 Bearer token (admin:admin 的 base64 编码)
    token = base64.b64encode("admin:admin".encode()).decode()
    server_url = "http://localhost:8001/mcp/"
    
    print(f"连接到服务器: {server_url}")
    print(f"使用 Bearer Token: {token}")
    print()
    
    try:
        # 创建认证的 MCP 客户端
        # 根据 FastMCP 文档，可以直接传递 token 字符串，FastMCP 会自动格式化
        async with Client(server_url, auth=token) as client:
            print("✅ 成功连接到 MCP 服务器")
            
            # 1. 测试 ping
            print("\n1. 测试连接...")
            await client.ping()
            print("   ✅ Ping 成功")
            
            # 2. 列出所有资源
            print("\n2. 列出可用资源...")
            resources = await client.list_resources()
            print(f"   发现 {len(resources)} 个资源:")
            for resource in resources:
                print(f"   - {resource.uri}: {resource.name}")
                if hasattr(resource, 'description') and resource.description:
                    print(f"     {resource.description}")
            
            # 3. 读取股票统计资源
            print("\n3. 读取股票统计资源...")
            try:
                stats_content = await client.read_resource("stock://stats")
                if stats_content:
                    print(f"   ✅ 统计信息:")
                    print(f"   {stats_content[0].text}")
            except Exception as e:
                print(f"   ❌ 读取统计资源失败: {e}")
            
            # 4. 读取所有股票资源
            print("\n4. 读取所有股票资源...")
            try:
                stocks_content = await client.read_resource("stock://all")
                if stocks_content:
                    import json
                    stocks_data = json.loads(stocks_content[0].text)
                    print(f"   ✅ 获取到 {len(stocks_data)} 只股票信息")
                    # 显示前3只股票
                    for i, stock in enumerate(stocks_data[:3]):
                        print(f"   {i+1}. {stock['symbol']}: {stock['name']} (${stock['price']})")
            except Exception as e:
                print(f"   ❌ 读取股票资源失败: {e}")
            
            # 5. 读取特定股票信息（动态资源模板）
            print("\n5. 读取特定股票信息 (AAPL)...")
            try:
                apple_content = await client.read_resource("stock://AAPL/info")
                if apple_content:
                    print(f"   ✅ AAPL 信息:")
                    print(f"   {apple_content[0].text}")
            except Exception as e:
                print(f"   ❌ 读取 AAPL 信息失败: {e}")
            
            # 6. 列出所有工具
            print("\n6. 列出可用工具...")
            tools = await client.list_tools()
            print(f"   发现 {len(tools)} 个工具:")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            
            # 7. 调用获取统计信息工具
            print("\n7. 调用获取统计信息工具...")
            try:
                result = await client.call_tool("get_stock_stats", {})
                print("   ✅ 统计信息:")
                stats = result.data.get("stats", {})
                for key, value in stats.items():
                    print(f"      {key}: {value}")
            except Exception as e:
                print(f"   ❌ 调用统计工具失败: {e}")
            
            # 8. 调用列出股票工具
            print("\n8. 调用列出股票工具...")
            try:
                result = await client.call_tool("list_stocks", {})
                print(f"   ✅ 获取到 {result.data.get('count', 0)} 只股票")
                # 显示前3只股票的详细信息
                stocks = result.data.get("stocks", [])[:3]
                for stock in stocks:
                    print(f"      {stock['symbol']}: {stock['name']} - ${stock['price']}")
            except Exception as e:
                print(f"   ❌ 调用列表工具失败: {e}")
            
            # 9. 调用获取特定股票工具
            print("\n9. 获取特定股票信息（按代码）...")
            try:
                result = await client.call_tool("get_stock", {
                    "identifier": "AAPL",
                    "by_symbol": True
                })
                if result.data.get("success"):
                    stock = result.data["stock"]
                    print("   ✅ 股票信息:")
                    print(f"      代码: {stock['symbol']}")
                    print(f"      名称: {stock['name']}")
                    print(f"      价格: ${stock['price']}")
                    print(f"      变动: {stock['change']}")
                    print(f"      交易量: {stock['volume']:,}")
                else:
                    print(f"   ❌ {result.data.get('error', '未知错误')}")
            except Exception as e:
                print(f"   ❌ 获取股票信息失败: {e}")
            
            # 10. 创建新股票（演示）
            print("\n10. 创建新股票（演示）...")
            try:
                new_stock_data = {
                    "symbol": "DEMO",
                    "name": "Demo Company Inc.",
                    "price": 100.50,
                    "change": 2.5,
                    "volume": 1000000,
                    "market_cap": 5000000000
                }
                
                result = await client.call_tool("create_stock", new_stock_data)
                if result.data.get("success"):
                    stock = result.data["stock"]
                    print("   ✅ 成功创建股票:")
                    print(f"      ID: {stock['id']}")
                    print(f"      代码: {stock['symbol']}")
                    print(f"      名称: {stock['name']}")
                    
                    # 立即删除演示股票
                    delete_result = await client.call_tool("delete_stock", {"stock_id": stock['id']})
                    if delete_result.data.get("success"):
                        print("   ✅ 演示股票已删除")
                else:
                    print(f"   ❌ {result.data.get('error', '创建失败')}")
            except Exception as e:
                print(f"   ❌ 创建股票失败: {e}")
            
    except Exception as e:
        print(f"❌ 连接 MCP 服务器失败: {e}")
        print("\n请确保 FastMCP 服务器正在运行:")
        print("  python3 stock_mcp_server.py")


def print_connection_info():
    """打印连接信息"""
    token = base64.b64encode("admin:admin".encode()).decode()
    
    print("MCP 客户端连接信息")
    print("=" * 30)
    print(f"服务器地址: http://localhost:8001/mcp/")
    print(f"认证方式: Bearer Token")
    print(f"用户名: admin")
    print(f"密码: admin")
    print(f"Bearer Token: {token}")
    print()
    print("使用方法（Python 代码）:")
    print("```python")
    print("from fastmcp import Client")
    print("import base64")
    print()
    print(f"token = '{token}'")
    print("async with Client('http://localhost:8001/mcp/', auth=token) as client:")
    print("    # 使用 MCP 客户端...")
    print("    resources = await client.list_resources()")
    print("    tools = await client.list_tools()")
    print("```")
    print()


async def main():
    """主函数"""
    print_connection_info()
    
    print("开始演示...")
    print()
    
    await demonstrate_mcp_client()
    
    print("\n演示完成！")
    print("\n您可以使用以上代码作为模板来开发自己的 MCP 客户端应用。")


if __name__ == "__main__":
    asyncio.run(main())
