import json
import uuid
import secrets
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import datetime

# 数据模型
class Stock(BaseModel):
    id: str
    symbol: str
    name: str
    price: float
    change: float
    volume: int
    market_cap: float
    created_at: str
    updated_at: str

class StockCreate(BaseModel):
    symbol: str
    name: str
    price: float
    change: float = 0.0
    volume: int = 0
    market_cap: float = 0.0

class StockUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None

# 数据存储类
class StockDatabase:
    def __init__(self, file_path: str = "stocks.txt"):
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not self.file_path.exists():
            self._save_data({})
    
    def _load_data(self) -> Dict[str, Dict]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data: Dict[str, Dict]):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_stock(self, stock_data: StockCreate) -> Stock:
        data = self._load_data()
        
        # 检查股票代码是否已存在
        for stock in data.values():
            if stock['symbol'] == stock_data.symbol:
                raise ValueError(f"股票代码 {stock_data.symbol} 已存在")
        
        stock_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        stock = Stock(
            id=stock_id,
            symbol=stock_data.symbol.upper(),
            name=stock_data.name,
            price=stock_data.price,
            change=stock_data.change,
            volume=stock_data.volume,
            market_cap=stock_data.market_cap,
            created_at=now,
            updated_at=now
        )
        
        data[stock_id] = stock.dict()
        self._save_data(data)
        return stock
    
    def get_all_stocks(self) -> List[Stock]:
        data = self._load_data()
        return [Stock(**stock) for stock in data.values()]
    
    def get_stock(self, stock_id: str) -> Optional[Stock]:
        data = self._load_data()
        if stock_id not in data:
            return None
        return Stock(**data[stock_id])
    
    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        data = self._load_data()
        for stock in data.values():
            if stock['symbol'].upper() == symbol.upper():
                return Stock(**stock)
        return None
    
    def update_stock(self, stock_id: str, update_data: StockUpdate) -> Optional[Stock]:
        data = self._load_data()
        if stock_id not in data:
            return None
        
        # 检查股票代码重复（如果更新了symbol）
        if update_data.symbol:
            for sid, stock in data.items():
                if sid != stock_id and stock['symbol'].upper() == update_data.symbol.upper():
                    raise ValueError(f"股票代码 {update_data.symbol} 已存在")
        
        stock = data[stock_id]
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if field == 'symbol' and value:
                stock[field] = value.upper()
            else:
                stock[field] = value
        
        stock['updated_at'] = datetime.now().isoformat()
        data[stock_id] = stock
        self._save_data(data)
        return Stock(**stock)
    
    def delete_stock(self, stock_id: str) -> bool:
        data = self._load_data()
        if stock_id not in data:
            return False
        del data[stock_id]
        self._save_data(data)
        return True

# 初始化数据库和 FastAPI
db = StockDatabase()
app = FastAPI(title="股票信息管理系统", description="简单的股票信息增删查改API", version="1.0.0")

# 初始化 Basic Auth
security = HTTPBasic()

# 认证配置
USERNAME = "admin"
PASSWORD = "admin"

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """验证用户凭据"""
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# 初始化一些示例数据
def init_sample_data():
    try:
        # 只有当没有数据时才添加示例数据
        if not db.get_all_stocks():
            sample_stocks = [
                StockCreate(symbol="AAPL", name="Apple Inc.", price=175.43, change=2.14, volume=52000000, market_cap=2800000000000),
                StockCreate(symbol="GOOGL", name="Alphabet Inc.", price=138.21, change=-1.23, volume=28000000, market_cap=1700000000000),
                StockCreate(symbol="MSFT", name="Microsoft Corp.", price=378.85, change=5.67, volume=31000000, market_cap=2900000000000),
                StockCreate(symbol="TSLA", name="Tesla Inc.", price=248.42, change=-8.91, volume=89000000, market_cap=790000000000),
                StockCreate(symbol="NVDA", name="NVIDIA Corp.", price=875.28, change=15.73, volume=45000000, market_cap=2100000000000)
            ]
            
            for stock_data in sample_stocks:
                try:
                    db.create_stock(stock_data)
                except ValueError:
                    pass  # 忽略重复错误
    except Exception as e:
        print(f"初始化示例数据时出错: {e}")

# 启动时初始化示例数据
init_sample_data()

# API 端点
@app.get("/", summary="根路径")
async def root():
    return {"message": "股票信息管理系统 API", "version": "1.0.0"}

@app.get("/protected", summary="受保护的测试端点")
async def protected_endpoint(username: str = Depends(authenticate_user)):
    return {"message": f"欢迎, {username}! 这是一个受保护的端点。"}

@app.get("/stocks", response_model=List[Stock], summary="获取所有股票")
async def get_all_stocks(username: str = Depends(authenticate_user)):
    """获取所有股票信息"""
    return db.get_all_stocks()

@app.post("/stocks", response_model=Stock, summary="创建新股票")
async def create_stock(stock: StockCreate, username: str = Depends(authenticate_user)):
    """创建新的股票记录"""
    try:
        return db.create_stock(stock)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stocks/{stock_id}", response_model=Stock, summary="根据ID获取股票")
async def get_stock(stock_id: str, username: str = Depends(authenticate_user)):
    """根据ID获取特定股票信息"""
    stock = db.get_stock(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    return stock

@app.get("/stocks/symbol/{symbol}", response_model=Stock, summary="根据代码获取股票")
async def get_stock_by_symbol(symbol: str, username: str = Depends(authenticate_user)):
    """根据股票代码获取股票信息"""
    stock = db.get_stock_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail=f"股票代码 {symbol} 不存在")
    return stock

@app.put("/stocks/{stock_id}", response_model=Stock, summary="更新股票信息")
async def update_stock(stock_id: str, stock_update: StockUpdate, username: str = Depends(authenticate_user)):
    """更新股票信息"""
    try:
        stock = db.update_stock(stock_id, stock_update)
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        return stock
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/stocks/{stock_id}", summary="删除股票")
async def delete_stock(stock_id: str, username: str = Depends(authenticate_user)):
    """删除股票记录"""
    success = db.delete_stock(stock_id)
    if not success:
        raise HTTPException(status_code=404, detail="股票不存在")
    return {"message": "股票删除成功"}

@app.get("/stats", summary="获取统计信息")
async def get_stats(username: str = Depends(authenticate_user)):
    """获取股票统计信息"""
    stocks = db.get_all_stocks()
    if not stocks:
        return {"总数": 0, "平均价格": 0, "总市值": 0}
    
    total_count = len(stocks)
    avg_price = sum(stock.price for stock in stocks) / total_count
    total_market_cap = sum(stock.market_cap for stock in stocks)
    
    return {
        "总数": total_count,
        "平均价格": round(avg_price, 2),
        "总市值": total_market_cap,
        "价格最高": max(stocks, key=lambda x: x.price).symbol,
        "价格最低": min(stocks, key=lambda x: x.price).symbol
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
