"""
FastMCP 股票信息管理 MCP 服务器
使用 HTTP streamable 模式，支持 resources 和 tools
带 Bearer Token 认证
"""

import json
import base64
import asyncio
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from stock_api import StockDatabase, StockCreate, StockUpdate, Stock
from datetime import datetime
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# 认证配置 - 创建Bearer Token（base64编码的admin:admin）
USERNAME = "admin"
PASSWORD = "admin"
VALID_TOKEN = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()

class AuthMiddleware(BaseHTTPMiddleware):
    """简单的认证中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 跳过根路径和健康检查
        if request.url.path in ["/", "/health", "/auth-info"]:
            return await call_next(request)
            
        # 检查是否是 MCP 路径
        if request.url.path.startswith("/mcp"):
            # 检查 Authorization header
            auth_header = request.headers.get("Authorization")
            
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing or invalid Authorization header"}
                )
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            
            # 验证 token
            if token != VALID_TOKEN:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid token"}
                )
        
        return await call_next(request)

# 创建 FastMCP 实例
mcp = FastMCP(name="StockMCPServer", version="1.0.0")

# 初始化股票数据库
stock_db = StockDatabase()

# ============== MCP 资源 (Resources) ==============

@mcp.resource("stock://all")
def get_all_stocks_resource() -> str:
    """获取所有股票信息的资源"""
    stocks = stock_db.get_all_stocks()
    stocks_data = [stock.dict() for stock in stocks]
    return json.dumps(stocks_data, ensure_ascii=False, indent=2)

@mcp.resource("stock://stats")
def get_stats_resource() -> str:
    """获取股票统计信息的资源"""
    stocks = stock_db.get_all_stocks()
    if not stocks:
        stats = {"总数": 0, "平均价格": 0, "总市值": 0}
    else:
        total_count = len(stocks)
        avg_price = sum(stock.price for stock in stocks) / total_count
        total_market_cap = sum(stock.market_cap for stock in stocks)
        
        stats = {
            "总数": total_count,
            "平均价格": round(avg_price, 2),
            "总市值": total_market_cap,
            "价格最高": max(stocks, key=lambda x: x.price).symbol,
            "价格最低": min(stocks, key=lambda x: x.price).symbol
        }
    
    return json.dumps(stats, ensure_ascii=False, indent=2)

@mcp.resource("stock://{symbol}/info")
def get_stock_by_symbol_resource(symbol: str) -> str:
    """根据股票代码获取单个股票信息的资源"""
    stock = stock_db.get_stock_by_symbol(symbol)
    if not stock:
        return json.dumps({"error": f"股票代码 {symbol} 不存在"}, ensure_ascii=False, indent=2)
    
    return json.dumps(stock.dict(), ensure_ascii=False, indent=2)

@mcp.resource("stock://config")
def get_server_config() -> str:
    """获取服务器配置信息"""
    config = {
        "server_name": "StockMCPServer",
        "version": "1.0.0",
        "supported_operations": ["create", "read", "update", "delete"],
        "data_file": "stocks.txt",
        "last_updated": datetime.now().isoformat()
    }
    return json.dumps(config, ensure_ascii=False, indent=2)

# ============== MCP 工具 (Tools) ==============

@mcp.tool(name="list_stocks", description="获取所有股票信息列表")
async def list_stocks_tool(ctx: Context) -> Dict[str, Any]:
    """获取所有股票信息列表"""
    await ctx.info("正在获取所有股票信息...")
    
    stocks = stock_db.get_all_stocks()
    stocks_data = [stock.dict() for stock in stocks]
    
    await ctx.info(f"成功获取 {len(stocks_data)} 只股票的信息")
    return {
        "count": len(stocks_data),
        "stocks": stocks_data
    }

@mcp.tool(name="get_stock", description="根据股票ID或代码获取股票信息")
async def get_stock_tool(identifier: str, ctx: Context, by_symbol: bool = False) -> Dict[str, Any]:
    """
    根据股票ID或代码获取股票信息
    
    Args:
        identifier: 股票ID或代码
        by_symbol: True表示按代码查询，False表示按ID查询
    """
    await ctx.info(f"正在查询股票: {identifier} ({'按代码' if by_symbol else '按ID'})")
    
    if by_symbol:
        stock = stock_db.get_stock_by_symbol(identifier)
    else:
        stock = stock_db.get_stock(identifier)
    
    if not stock:
        error_msg = f"股票{'代码' if by_symbol else 'ID'} {identifier} 不存在"
        await ctx.info(error_msg)
        return {"error": error_msg}
    
    await ctx.info(f"成功找到股票: {stock.name} ({stock.symbol})")
    
    return {
        "success": True,
        "stock": stock.dict()
    }

@mcp.tool(name="create_stock", description="创建新的股票记录")
async def create_stock_tool(
    symbol: str,
    name: str,
    price: float,
    ctx: Context,
    change: float = 0.0,
    volume: int = 0,
    market_cap: float = 0.0
) -> Dict[str, Any]:
    """
    创建新的股票记录
    
    Args:
        symbol: 股票代码
        name: 股票名称
        price: 股票价格
        change: 价格变动（可选）
        volume: 交易量（可选）
        market_cap: 市值（可选）
    """
    await ctx.info(f"正在创建股票: {symbol} ({name})")
    
    try:
        stock_data = StockCreate(
            symbol=symbol,
            name=name,
            price=price,
            change=change,
            volume=volume,
            market_cap=market_cap
        )
        
        new_stock = stock_db.create_stock(stock_data)
        
        await ctx.info(f"成功创建股票: {new_stock.name} ({new_stock.symbol})")
        
        return {
            "success": True,
            "message": "股票创建成功",
            "stock": new_stock.dict()
        }
    
    except ValueError as e:
        error_msg = str(e)
        await ctx.info(f"创建失败: {error_msg}")
        return {"error": error_msg}

@mcp.tool(name="update_stock", description="更新股票信息")
async def update_stock_tool(
    stock_id: str,
    ctx: Context,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
    price: Optional[float] = None,
    change: Optional[float] = None,
    volume: Optional[int] = None,
    market_cap: Optional[float] = None
) -> Dict[str, Any]:
    """
    更新股票信息
    
    Args:
        stock_id: 股票ID
        symbol: 新的股票代码（可选）
        name: 新的股票名称（可选）
        price: 新的股票价格（可选）
        change: 新的价格变动（可选）
        volume: 新的交易量（可选）
        market_cap: 新的市值（可选）
    """
    await ctx.info(f"正在更新股票: {stock_id}")
    
    try:
        update_data = StockUpdate(
            symbol=symbol,
            name=name,
            price=price,
            change=change,
            volume=volume,
            market_cap=market_cap
        )
        
        updated_stock = stock_db.update_stock(stock_id, update_data)
        
        if not updated_stock:
            error_msg = "股票不存在"
            await ctx.info(error_msg)
            return {"error": error_msg}
        
        await ctx.info(f"成功更新股票: {updated_stock.name} ({updated_stock.symbol})")
        
        return {
            "success": True,
            "message": "股票更新成功",
            "stock": updated_stock.dict()
        }
    
    except ValueError as e:
        error_msg = str(e)
        await ctx.info(f"更新失败: {error_msg}")
        return {"error": error_msg}

@mcp.tool(name="delete_stock", description="删除股票记录")
async def delete_stock_tool(stock_id: str, ctx: Context) -> Dict[str, Any]:
    """
    删除股票记录
    
    Args:
        stock_id: 要删除的股票ID
    """
    await ctx.info(f"正在删除股票: {stock_id}")
    
    # 先获取股票信息用于返回
    stock = stock_db.get_stock(stock_id)
    if not stock:
        error_msg = "股票不存在"
        await ctx.info(error_msg)
        return {"error": error_msg}
    
    success = stock_db.delete_stock(stock_id)
    
    if success:
        await ctx.info(f"成功删除股票: {stock.name} ({stock.symbol})")
        return {
            "success": True,
            "message": "股票删除成功",
            "deleted_stock": stock.dict()
        }
    else:
        error_msg = "删除失败"
        await ctx.info(error_msg)
        return {"error": error_msg}

@mcp.tool(name="get_stock_stats", description="获取股票统计信息")
async def get_stock_stats_tool(ctx: Context) -> Dict[str, Any]:
    """获取股票统计信息"""
    await ctx.info("正在计算股票统计信息...")
    
    stocks = stock_db.get_all_stocks()
    if not stocks:
        stats = {"总数": 0, "平均价格": 0, "总市值": 0}
    else:
        total_count = len(stocks)
        avg_price = sum(stock.price for stock in stocks) / total_count
        total_market_cap = sum(stock.market_cap for stock in stocks)
        
        stats = {
            "总数": total_count,
            "平均价格": round(avg_price, 2),
            "总市值": total_market_cap,
            "价格最高": max(stocks, key=lambda x: x.price).symbol,
            "价格最低": min(stocks, key=lambda x: x.price).symbol
        }
    
    await ctx.info(f"统计完成: 共 {stats.get('总数', 0)} 只股票")
    
    return {
        "success": True,
        "stats": stats
    }

# 添加健康检查端点
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse(content={"status": "healthy", "service": "FastMCP Stock Server"})

# 添加认证信息端点
@mcp.custom_route("/auth-info", methods=["GET"])
async def auth_info(request: Request):
    return JSONResponse(content={
        "message": "Bearer Token Authentication Required",
        "token_format": "Bearer <base64_encoded_credentials>",
        "example_credentials": "admin:admin",
        "example_token": f"Bearer {VALID_TOKEN}"
    })

# ============== 启动服务器 ==============

if __name__ == "__main__":
    print("正在启动 FastMCP 股票信息服务器...")
    print("🔒 认证模式: Bearer Token")
    print(f"📋 用户名: {USERNAME}")
    print(f"🔑 密码: {PASSWORD}")
    print(f"🎫 Bearer Token: {VALID_TOKEN}")
    print()
    print("支持的资源:")
    print("  - stock://all - 获取所有股票信息")
    print("  - stock://stats - 获取统计信息")
    print("  - stock://{symbol}/info - 获取特定股票信息")
    print("  - stock://config - 获取服务器配置")
    print()
    print("支持的工具:")
    print("  - list_stocks - 列出所有股票")
    print("  - get_stock - 获取股票信息")
    print("  - create_stock - 创建新股票")
    print("  - update_stock - 更新股票信息")
    print("  - delete_stock - 删除股票")
    print("  - get_stock_stats - 获取统计信息")
    print()
    print("📍 服务器地址:")
    print("  - MCP 端点: http://localhost:8001/mcp/")
    print("  - 健康检查: http://localhost:8001/health")
    print("  - 认证信息: http://localhost:8001/auth-info")
    print()
    print("🔐 使用 Bearer Token 认证访问:")
    print(f"   Authorization: Bearer {VALID_TOKEN}")
    
    # 获取 HTTP 应用并添加中间件
    app = mcp.http_app()
    app.add_middleware(AuthMiddleware)
    
    # 使用 HTTP transport (streamable 模式)
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
