"""
A股数据获取模块
使用akshare获取免费A股数据
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
        self.cache_duration = 300  # 缓存5分钟
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        cache_key = 'stock_list'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            df = ak.stock_zh_a_spot_em()
            df = df[['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', 
                     '总市值', '成交额', '换手率']]
            df.columns = ['code', 'name', 'price', 'change_pct', 'pe', 
                         'market_cap', 'volume', 'turnover']
            df['market_cap'] = df['market_cap'] / 1e8  # 转为亿
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
            # 根据代码判断市场
            if code.startswith('6'):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"
            
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                    start_date=None, end_date=None, adjust="qfq")
            if df is not None and len(df) > 0:
                df = df.tail(days).copy()
                df.columns = ['date', 'open', 'close', 'high', 'low', 'volume',
                             'amount', 'amplitude', 'pct_change', 'change', 'turnover']
                self._set_cache(cache_key, df)
            return df
        except Exception as e:
            print(f"获取{code}K线失败: {e}")
            return pd.DataFrame()
    
    def get_stock_news(self, code: str, num: int = 5) -> List[dict]:
        """获取个股新闻"""
        try:
            if code.startswith('6'):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"
            
            df = ak.stock_news_em(symbol=symbol)
            if df is not None and len(df) > 0:
                df = df.head(num)
                news_list = []
                for _, row in df.iterrows():
                    news_list.append({
                        'title': row.get('title', ''),
                        'content': row.get('content', '')[:200],
                        'time': row.get('time', '')
                    })
                return news_list
            return []
        except Exception as e:
            print(f"获取{code}新闻失败: {e}")
            return []
    
    def get_sector_flow(self) -> pd.DataFrame:
        """获取行业资金流向"""
        try:
            df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
            return df.head(10) if df is not None else pd.DataFrame()
        except Exception as e:
            print(f"获取行业资金流向失败: {e}")
            return pd.DataFrame()
    
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
