"""
技术指标计算模块
使用 ta 库（纯Python，无需TA-Lib二进制依赖）
"""
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        if len(df) < 30:
            return df
        
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # 移动平均线
        df['ma5'] = SMAIndicator(close, window=5).sma_indicator()
        df['ma10'] = SMAIndicator(close, window=10).sma_indicator()
        df['ma20'] = SMAIndicator(close, window=20).sma_indicator()
        df['ma60'] = SMAIndicator(close, window=60).sma_indicator()
        
        # RSI
        df['rsi'] = RSIIndicator(close, window=14).rsi()
        
        # MACD
        macd = MACD(close, window_slow=26, window_fast=12, window_sign=9)
        df['macd_dif'] = macd.macd()
        df['macd_dea'] = macd.macd_signal()
        df['macd'] = macd.macd_diff()
        df['macd_golden_cross'] = (df['macd_dif'] > df['macd_dea']) & (df['macd_dif'].shift(1) <= df['macd_dea'].shift(1))
        
        # 布林带
        bb = BollingerBands(close, window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_position'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR
        df['atr'] = AverageTrueRange(high, low, close, window=14).average_true_range()
        df['atr_ratio'] = df['atr'] / close * 100
        
        # 成交量
        df['volume_ma20'] = SMAIndicator(volume, window=20).sma_indicator()
        df['volume_ratio'] = volume / df['volume_ma20']
        
        # 均线金叉
        df['ma_golden_cross'] = (df['ma5'] > df['ma20']) & (df['ma5'].shift(1) <= df['ma20'].shift(1))
        
        return df
