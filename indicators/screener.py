"""
股票筛选逻辑
"""
import pandas as pd
from typing import List, Dict
from data.fetcher import fetcher
from indicators.technical import TechnicalIndicators
from config.settings import settings

class StockScreener:
    """股票筛选器"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.config = settings.SCREENING
    
    def filter_base(self, df: pd.DataFrame) -> pd.DataFrame:
        """基础筛选"""
        # 基础条件
        df = df[
            (df['price'] >= self.config['price_min']) &
            (df['market_cap'] >= self.config['min_market_cap'])
        ].copy()
        
        # P/E筛选（动态市盈率）
        df = df[
            (df['pe'] >= self.config['pe_min']) &
            (df['pe'] <= self.config['pe_max'])
        ].copy()
        
        return df
    
    def screen_stock(self, code: str) -> Dict:
        """单只股票技术筛选"""
        # 获取K线数据
        df = fetcher.get_kline(code, days=60)
        if len(df) < 30:
            return None
        
        # 计算技术指标
        df = self.indicators.calculate_all(df)
        latest = df.iloc[-1]
        
        # 检查成交量
        if latest['volume_ratio'] < self.config['volume_ratio']:
            return None
        
        # 检查RSI
        if not (self.config['rsi_min'] <= latest['rsi'] <= self.config['rsi_max']):
            return None
        
        # 检查MACD金叉
        macd_signal = latest['macd_golden_cross'] or (latest['macd_dif'] > latest['macd_dea'] & 
                                                       df.iloc[-2]['macd_dif'] <= df.iloc[-2]['macd_dea'])
        
        # 检查均线金叉
        ma_signal = latest['ma_golden_cross'] or (latest['ma5'] > latest['ma20'] & 
                                                   df.iloc[-2]['ma5'] <= df.iloc[-2]['ma20'])
        
        # 检查布林带位置（处于中轨上方，但未超买）
        bb_signal = 0.4 < latest['bb_position'] < 0.85
        
        # 综合得分
        score = 0
        signals = []
        
        if macd_signal:
            score += 25
            signals.append('MACD金叉')
        if ma_signal:
            score += 25
            signals.append('均线金叉')
        if bb_signal:
            score += 20
            signals.append('布林带突破')
        if latest['volume_ratio'] > 2:
            score += 20
            signals.append('倍量')
        if latest['atr_ratio'] > latest['atr_ratio'] * 0.8:  # 波动放大
            score += 10
            signals.append('波动放大')
        
        if score < 50:
            return None
        
        return {
            'code': code,
            'score': score,
            'signals': signals,
            'price': round(latest['close'], 2),
            'change_pct': round(latest['pct_change'], 2),
            'rsi': round(latest['rsi'], 2),
            'volume_ratio': round(latest['volume_ratio'], 2),
            'macd_dif': round(latest['macd_dif'], 3),
            'macd_dea': round(latest['macd_dea'], 3),
            'bb_position': round(latest['bb_position'], 2),
            'atr_ratio': round(latest['atr_ratio'], 2),
        }
    
    def run_screening(self, max_stocks: int = None) -> List[Dict]:
        """
        运行全市场筛选
        """
        max_stocks = max_stocks or self.config['max_stocks']
        
        print("正在获取股票列表...")
        stock_list = fetcher.get_stock_list()
        
        print(f"共 {len(stock_list)} 只股票，开始基础筛选...")
        base_df = self.filter_base(stock_list)
        print(f"基础筛选后: {len(base_df)} 只")
        
        # 按成交额排序，优先分析活跃股票
        base_df = base_df.sort_values('volume', ascending=False).head(max_stocks)
        
        print("开始技术筛选...")
        results = []
        for idx, row in base_df.iterrows():
            code = row['code']
            name = row['name']
            
            result = self.screen_stock(code)
            if result:
                result['name'] = name
                result['pe'] = round(row['pe'], 2) if pd.notna(row['pe']) else None
                result['market_cap'] = round(row['market_cap'], 2)
                results.append(result)
                print(f"✓ {code} {name} 得分: {result['score']}")
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
