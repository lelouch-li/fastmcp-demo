# FastMCP 股票信息管理演示

这是一个使用 FastMCP 框架构建的股票信息管理系统演示，支持 HTTP streamable 模式的 MCP 服务器，包含完整的认证功能。

## 功能特性

### 1. 基础 FastAPI 股票管理系统
- 📊 完整的股票信息 CRUD 操作
- 💾 本地 txt 文件存储（JSON 格式）
- 🔍 支持按 ID 和股票代码查询
- 📈 统计信息功能

### 2. FastMCP 集成
- 🌐 HTTP streamable transport 模式
- 📚 MCP 资源（Text Resources）支持
- 🛠️ MCP 工具（Tools）支持
- 💬 上下文感知的日志记录

### 3. 完整认证系统
- 🔐 FastAPI Basic Authentication（用户名/密码: admin/admin）
- 🎫 FastMCP Bearer Token 认证（base64 编码的凭证）
- 🛡️ 自定义认证中间件
- 🔍 认证状态检测和测试工具

## 安装运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行 FastAPI 服务器（可选）
```bash
python stock_api.py
```
访问：http://localhost:8000/docs

### 3. 运行 FastMCP 服务器
```bash
python stock_mcp_server.py
```
MCP 端点：http://localhost:8001/mcp/ （需要 Bearer Token 认证）

## MCP 资源 (Resources)

支持以下资源访问：

### 静态资源
- `stock://all` - 获取所有股票信息
- `stock://stats` - 获取统计信息 
- `stock://config` - 获取服务器配置

### 动态资源模板
- `stock://{symbol}/info` - 获取特定股票信息
  - 示例：`stock://AAPL/info`

## MCP 工具 (Tools)

提供以下工具操作：

### 查询工具
- `list_stocks` - 获取所有股票信息列表
- `get_stock` - 根据ID或代码获取股票信息
- `get_stock_stats` - 获取统计信息

### 管理工具
- `create_stock` - 创建新股票记录
- `update_stock` - 更新股票信息
- `delete_stock` - 删除股票记录

## 数据模型

### Stock（股票信息）
```json
{
  "id": "uuid",
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "price": 175.43,
  "change": 2.14,
  "volume": 52000000,
  "market_cap": 2800000000000,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## 示例数据

系统会自动初始化以下示例股票：
- AAPL (Apple Inc.)
- GOOGL (Alphabet Inc.)
- MSFT (Microsoft Corp.)
- TSLA (Tesla Inc.)
- NVDA (NVIDIA Corp.)

## 技术栈

- **FastAPI** - Web 框架
- **FastMCP** - MCP 服务器框架
- **Pydantic** - 数据验证
- **JSON** - 数据存储格式

## 项目结构

```
fastmcp-demo/
├── stock_api.py            # FastAPI 股票管理 API (带 Basic Auth)
├── stock_mcp_server.py     # FastMCP 服务器 (带 Bearer Token Auth)
├── test_auth.py           # 认证功能测试工具
├── mcp_client_example.py  # MCP 客户端使用演示
├── demo.py               # 功能演示脚本
├── run_servers.sh        # 服务器启动脚本
├── requirements.txt      # Python 依赖
├── stocks.txt           # 数据存储文件（自动生成）
└── README.md           # 项目说明
```

## 认证信息

### FastAPI Basic Authentication
- **用户名**: `admin`
- **密码**: `admin`
- **访问**: 所有 `/stocks/*`, `/stats`, `/protected` 端点

### FastMCP Bearer Token Authentication
- **用户名**: `admin`
- **密码**: `admin`
- **Bearer Token**: `YWRtaW46YWRtaW4=` (base64 编码的 admin:admin)
- **Authorization Header**: `Bearer YWRtaW46YWRtaW4=`

## 使用说明

### MCP 客户端连接
服务器启动后，MCP 客户端可以连接到：
- **URL**: `http://localhost:8001/mcp/`
- **Transport**: HTTP Streamable
- **认证**: 需要 Bearer Token

### MCP 客户端认证示例
```python
import base64
from fastmcp import Client

# 创建 Bearer Token
token = base64.b64encode("admin:admin".encode()).decode()

# 连接到认证的 MCP 服务器
async with Client(
    "http://localhost:8001/mcp/",
    auth=token  # FastMCP 自动添加 Bearer 前缀
) as client:
    # 使用客户端...
    tools = await client.list_tools()
    resources = await client.list_resources()
```

### 工具调用示例
```python
# 创建股票
await client.call_tool("create_stock", {
    "symbol": "AMZN",
    "name": "Amazon.com Inc.",
    "price": 3200.50,
    "change": 45.20,
    "volume": 25000000,
    "market_cap": 1600000000000
})

# 获取股票信息
await client.call_tool("get_stock", {
    "identifier": "AAPL",
    "by_symbol": True
})
```

### 资源访问示例
```python
# 读取所有股票信息
content = await client.read_resource("stock://all")

# 读取特定股票信息
content = await client.read_resource("stock://AAPL/info")
```

## 测试工具

项目包含以下测试和演示脚本：

### 1. 认证测试工具
```bash
python test_auth.py
```
- 测试 FastAPI Basic Auth
- 测试 FastMCP Bearer Token Auth
- 验证认证机制正确性

### 2. MCP 客户端演示
```bash
python mcp_client_example.py
```
- 完整的 MCP 客户端使用演示
- 展示资源和工具的调用方法
- 包含认证连接示例

## 注意事项

### 数据存储
- 数据存储在本地 `stocks.txt` 文件中
- 服务器重启后数据会保持
- 股票代码会自动转换为大写
- 支持并发访问，但文件操作是同步的

### 认证安全
- **生产环境请更改默认用户名和密码**
- Bearer Token 使用 base64 编码，仅适用于演示
- 生产环境建议使用 JWT 或更安全的认证机制
- 所有 MCP 端点都需要认证，健康检查端点除外

### 端口配置
- FastAPI 服务器: `http://localhost:8000` (Basic Auth)
- FastMCP 服务器: `http://localhost:8001/mcp/` (Bearer Token)
- 可在代码中修改端口配置

### 引用文档
本项目实现参考了以下 FastMCP 文档：
- [Bearer Token Authentication](https://gofastmcp.com/clients/auth/bearer) - Bearer Token 认证实现
