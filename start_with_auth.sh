#!/bin/bash

# FastMCP 股票信息服务器 - 带认证启动脚本

echo "🚀 FastMCP 股票信息管理系统"
echo "================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 安装依赖..."
    pip install -r requirements.txt
else
    echo "✅ 激活虚拟环境..."
    source venv/bin/activate
fi

echo ""
echo "🔐 认证信息"
echo "----------"
echo "FastAPI Basic Auth (端口 8000):"
echo "  用户名: admin"
echo "  密码: admin"
echo "  访问: http://localhost:8000/docs"
echo ""
echo "FastMCP Bearer Token Auth (端口 8001):"
echo "  用户名: admin"
echo "  密码: admin" 
echo "  Bearer Token: YWRtaW46YWRtaW4="
echo "  MCP 端点: http://localhost:8001/mcp/"
echo "  健康检查: http://localhost:8001/health"
echo "  认证信息: http://localhost:8001/auth-info"
echo ""

echo "🛠️  可用操作:"
echo "1. 启动 FastAPI 服务器 (Basic Auth)"
echo "2. 启动 FastMCP 服务器 (Bearer Token Auth)"
echo "3. 启动 FastMCP 服务器 (清爽版，过滤404日志)"
echo "4. 运行认证测试"
echo "5. 运行 MCP 客户端演示"
echo "6. 显示详细使用说明"
echo ""

read -p "选择操作 (1-6): " choice

case $choice in
    1)
        echo "🌐 启动 FastAPI 服务器..."
        echo "访问 http://localhost:8000/docs 查看 API 文档"
        echo "使用 admin/admin 进行认证"
        python3 stock_api.py
        ;;
    2)
        echo "🔗 启动 FastMCP 服务器..."
        echo "MCP 端点: http://localhost:8001/mcp/"
        echo "使用 Bearer Token: YWRtaW46YWRtaW4= 进行认证"
        python3 stock_mcp_server.py
        ;;
    3)
        echo "✨ 启动 FastMCP 服务器 (清爽版)..."
        echo "MCP 端点: http://localhost:8001/mcp/"
        echo "使用 Bearer Token: YWRtaW46YWRtaW4= 进行认证"
        echo "💡 OAuth 发现的 404 错误已被过滤"
        python3 clean_mcp_server.py
        ;;
    4)
        echo "🧪 运行认证测试..."
        echo "请先在其他终端启动两个服务器："
        echo "  终端1: python3 stock_api.py"
        echo "  终端2: python3 stock_mcp_server.py"
        read -p "服务器已启动？按 Enter 继续..."
        python3 test_auth.py
        ;;
    5)
        echo "📱 运行 MCP 客户端演示..."
        echo "请先在其他终端启动 FastMCP 服务器："
        echo "  python3 stock_mcp_server.py 或 python3 clean_mcp_server.py"
        read -p "服务器已启动？按 Enter 继续..."
        python3 mcp_client_example.py
        ;;
    6)
        echo "📖 详细使用说明"
        echo "=============="
        echo ""
        echo "🔧 MCP 客户端连接示例 (Python):"
        echo "```python"
        echo "import base64"
        echo "from fastmcp import Client"
        echo ""
        echo "# 创建 Bearer Token"
        echo "token = base64.b64encode('admin:admin'.encode()).decode()"
        echo ""
        echo "# 连接到认证的 MCP 服务器"
        echo "async with Client('http://localhost:8001/mcp/', auth=token) as client:"
        echo "    resources = await client.list_resources()"
        echo "    tools = await client.list_tools()"
        echo "    result = await client.call_tool('get_stock_stats', {})"
        echo "```"
        echo ""
        echo "🌐 HTTP 请求示例 (curl):"
        echo "```bash"
        echo "# FastAPI (Basic Auth)"
        echo "curl -u admin:admin http://localhost:8000/stocks"
        echo ""
        echo "# FastMCP (Bearer Token)"
        echo "curl -H 'Authorization: Bearer YWRtaW46YWRtaW4=' http://localhost:8001/health"
        echo "```"
        echo ""
        echo "📚 更多信息请查看 README.md 文件"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
