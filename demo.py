"""
演示如何使用 FastMCP 股票信息服务器
这个脚本展示了如何手动测试服务器功能
"""

from stock_mcp_server import mcp, stock_db
from stock_api import StockCreate
import asyncio
import json


def demo_basic_operations():
    """演示基本的数据库操作"""
    print("=== 基本数据库操作演示 ===")
    
    # 显示现有股票
    stocks = stock_db.get_all_stocks()
    print(f"当前股票数量: {len(stocks)}")
    
    for stock in stocks[:3]:  # 显示前3只股票
        print(f"- {stock.symbol}: {stock.name} (${stock.price})")
    
    print()


def demo_mcp_resources():
    """演示 MCP 资源功能"""
    print("=== MCP 资源演示 ===")
    
    try:
        # 直接调用资源函数进行演示
        from stock_mcp_server import get_all_stocks_resource, get_stats_resource
        
        # 获取所有股票资源
        data = get_all_stocks_resource()
        print(f"stock://all 资源返回数据长度: {len(data)} 字符")
        
        # 获取统计信息资源
        stats_data = get_stats_resource()
        print("stock://stats 资源返回:")
        stats_json = json.loads(stats_data)
        for key, value in stats_json.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"资源演示出错: {e}")
    
    print()


async def demo_mcp_tools():
    """演示 MCP 工具功能"""
    print("=== MCP 工具演示 ===")
    
    try:
        # 直接调用工具函数进行演示
        from stock_mcp_server import get_stock_stats_tool, list_stocks_tool
        
        print("可用工具:")
        print("- list_stocks: 获取所有股票信息列表")
        print("- get_stock: 根据ID或代码获取股票信息")
        print("- create_stock: 创建新股票记录")
        print("- update_stock: 更新股票信息")
        print("- delete_stock: 删除股票记录")
        print("- get_stock_stats: 获取统计信息")
        
        # 演示调用工具（由于 Context 现在是必需的，这里只展示工具列表）
        print("\n注意: 工具现在需要 FastMCP Context，不能直接调用")
        print("请使用 MCP 客户端来调用这些工具")
        
    except Exception as e:
        print(f"工具演示出错: {e}")
    
    print()


def demo_file_storage():
    """演示文件存储功能"""
    print("=== 文件存储演示 ===")
    
    import os
    from pathlib import Path
    
    data_file = Path("stocks.txt")
    if data_file.exists():
        file_size = data_file.stat().st_size
        print(f"数据文件 '{data_file}' 存在")
        print(f"文件大小: {file_size} 字节")
        
        # 显示文件内容的开头部分
        with open(data_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                data = json.loads(content)
                print(f"存储的股票记录数: {len(data)}")
            else:
                print("文件为空")
    else:
        print("数据文件不存在")
    
    print()


async def main():
    """主演示函数"""
    print("FastMCP 股票信息管理系统演示")
    print("=" * 50)
    print()
    
    demo_basic_operations()
    demo_mcp_resources()
    await demo_mcp_tools()
    demo_file_storage()
    
    print("演示完成!")
    print()
    print("要启动 MCP 服务器，请运行:")
    print("  python3 stock_mcp_server.py")
    print()
    print("服务器将在 http://localhost:8000/mcp/ 上提供 MCP 服务")


if __name__ == "__main__":
    asyncio.run(main())
