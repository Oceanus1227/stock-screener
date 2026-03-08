"""
A股数据获取模块
使用akshare获取免费A股数据，带重试机制
"""
import akshare as ak
import pandas as pd
import time
from typing import List, Optional
from datetime import datetime, timedelta

class DataFetcher:
    """数据获取器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300
    
    def _retry_request(self, func, max_retries=3, delay=2):
        """带重试的请求"""
        for i in range(max_retries):
            try:
                return func()
            except Exception as e:
                if i < max_retries - 1:
                    print(f"请求失败，{delay}秒后重试 ({i+1}/{max_retries}): {e}")
                    time.sleep(delay)
                    delay *= 2  # 指数退避
                else:
                    raise e
        return None
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        cache_key = 'stock_list'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            def fetch():
                df = ak.stock_zh_a_spot_em()
                return df
            
            df = self._retry_request(fetch)
            if df is None or len(df) == 0:
                print("获取股票列表失败，返回空数据")
                return pd.DataFrame()
            
            # 标准化列名
            column_mapping = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'change_pct',
                '市盈率-动态': 'pe',
                '总市值': 'market_cap',
                '成交额': 'volume',
                '换手率': 'turnover'
            }
            
            # 只保留存在的列
            available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df[list(available_cols.keys())].copy()
            df.columns = list(available_cols.values())
            
            # 数据处理
            if 'market_cap' in df.columns:
                df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce') / 1e8
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
            if 'pe' in df.columns:
                df['pe'] = pd.to_numeric(df['pe'], errors='coerce')
            
            # 过滤无效数据
            df = df[df['price'] > 0].copy()
            
            self._set_cache(cache_key, df)
            return df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_kline(self, code: str, days: int = 60) -> pd.DataFrame:
        """获取个股K线数据"""
        cache_key = f'kline_{code}_{days}'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            def fetch():
                # 根据代码判断市场
                if code.startswith('6'):
                    symbol = f"sh{code}"
                else:
                    symbol = f"sz{code}"
                
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                        start_date=None, end_date=None, adjust="qfq")
                return df
            
            df = self._retry_request(fetch)
            if df is None or len(df) < days // 2:  # 允许部分数据缺失
                return pd.DataFrame()
            
            df = df.tail(days).copy()
            df.columns = ['date', 'open', 'close', 'high', 'low', 'volume',
                         'amount', 'amplitude', 'pct_change', 'change', 'turnover']
            
            # 转换数值类型
            for col in ['open', 'close', 'high', 'low', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            self._set_cache(cache_key, df)
            return df
        except Exception as e:
            print(f"获取{code}K线失败: {e}")
            return pd.DataFrame()
    
    def get_stock_news(self, code: str, num: int = 5) -> List[dict]:
        """获取个股新闻"""
        try:
            def fetch():
                if code.startswith('6'):
                    symbol = f"sh{code}"
                else:
                    symbol = f"sz{code}"
                
                df = ak.stock_news_em(symbol=symbol)
                return df
            
            df = self._retry_request(fetch, max_retries=2)
            if df is None or len(df) == 0:
                return []
            
            df = df.head(num)
            news_list = []
            for _, row in df.iterrows():
                news_list.append({
                    'title': row.get('title', ''),
                    'content': str(row.get('content', ''))[:200],
                    'time': row.get('time', '')
                })
            return news_list
        except Exception as e:
            print(f"获取{code}新闻失败: {e}")
            return []
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self.cache:
            return False
        if time.time() - self.cache_time.get(key, 0) > self.cache_duration:
            return False
        return True
    
    def _set_cache(self, key: str, value):
        """设置缓存"""
        self.cache[key] = value
        self.cache_time[key] = time.time()
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
        self.cache_time.clear()

# 全局实例
fetcher = DataFetcher()
