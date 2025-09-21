#!/bin/bash

# FastMCP 股票信息服务器启动脚本

echo "FastMCP 股票信息管理系统"
echo "========================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "安装依赖..."
    pip install -r requirements.txt
else
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

echo ""
echo "可用的服务器选项:"
echo "1. FastAPI 服务器 (http://localhost:8000)"
echo "2. FastMCP 服务器 (http://localhost:8000/mcp/)"
echo "3. 演示脚本"
echo ""

read -p "选择要运行的服务器 (1-3): " choice

case $choice in
    1)
        echo "启动 FastAPI 服务器..."
        echo "访问 http://localhost:8000/docs 查看 API 文档"
        python3 stock_api.py
        ;;
    2)
        echo "启动 FastMCP 服务器..."
        echo "MCP 端点: http://localhost:8000/mcp/"
        python3 stock_mcp_server.py
        ;;
    3)
        echo "运行演示脚本..."
        python3 demo.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
