#!/usr/bin/env python3
"""
清爽版 FastMCP 服务器 - 过滤掉正常的 OAuth 发现 404 日志
"""

import logging
from stock_mcp_server import *

# 自定义日志过滤器
class MCPLogFilter(logging.Filter):
    def filter(self, record):
        # 过滤掉正常的 OAuth 发现请求
        oauth_paths = [
            '/.well-known/oauth-protected-resource',
            '/.well-known/oauth-authorization-server', 
            '/.well-known/openid-configuration',
            '/register'
        ]
        
        # 检查是否是这些路径的404错误
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            if '404 Not Found' in message:
                for path in oauth_paths:
                    if path in message:
                        return False  # 过滤掉这些日志
        
        return True  # 保留其他所有日志

if __name__ == "__main__":
    print("正在启动 FastMCP 股票信息服务器（清爽版）...")
    print("🔒 认证模式: Bearer Token")
    print(f"📋 用户名: {USERNAME}")
    print(f"🔑 密码: {PASSWORD}")  
    print(f"🎫 Bearer Token: {VALID_TOKEN}")
    print()
    print("📍 服务器地址:")
    print("  - MCP 端点: http://localhost:8001/mcp/")
    print("  - 健康检查: http://localhost:8001/health")
    print("  - 认证信息: http://localhost:8001/auth-info")
    print()
    print("💡 提示: OAuth 发现的 404 错误已被过滤，日志更清爽")
    print()
    
    # 添加日志过滤器
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(MCPLogFilter())
    
    # 获取 HTTP 应用并添加中间件
    app = mcp.http_app()
    app.add_middleware(AuthMiddleware)
    
    # 使用 HTTP transport (streamable 模式)
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
