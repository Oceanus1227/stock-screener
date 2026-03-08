"""
技术指标计算模块
使用pandas实现TA-Lib功能（无需安装TA-Lib二进制库）
"""
import pandas as pd
import numpy as np

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """简单移动平均线"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """指数移动平均线"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """RSI相对强弱指标"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """MACD指标，返回(DIF, DEA, MACD)"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        dif = ema_fast - ema_slow
        dea = TechnicalIndicators.ema(dif, signal)
        macd = (dif - dea) * 2
        return dif, dea, macd
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> tuple:
        """布林带，返回(上轨, 中轨, 下轨)"""
        middle = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """ATR真实波动幅度"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=period).mean()
    
    @staticmethod
    def volume_ratio(volume: pd.Series, period: int = 20) -> pd.Series:
        """量比 = 当日成交量 / 前N日平均成交量"""
        avg_volume = volume.rolling(window=period).mean()
        return volume / avg_volume
    
    @staticmethod
    def golden_cross(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series:
        """金叉信号：短期均线上穿长期均线"""
        cross = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        return cross
    
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
        df['ma5'] = TechnicalIndicators.sma(close, 5)
        df['ma10'] = TechnicalIndicators.sma(close, 10)
        df['ma20'] = TechnicalIndicators.sma(close, 20)
        df['ma60'] = TechnicalIndicators.sma(close, 60)
        
        # RSI
        df['rsi'] = TechnicalIndicators.rsi(close, 14)
        
        # MACD
        df['macd_dif'], df['macd_dea'], df['macd'] = TechnicalIndicators.macd(close)
        df['macd_golden_cross'] = TechnicalIndicators.golden_cross(df['macd_dif'], df['macd_dea'])
        
        # 布林带
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = TechnicalIndicators.bollinger_bands(close)
        df['bb_position'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR
        df['atr'] = TechnicalIndicators.atr(high, low, close, 14)
        df['atr_ratio'] = df['atr'] / close * 100  # ATR占价格百分比
        
        # 成交量
        df['volume_ma20'] = TechnicalIndicators.sma(volume, 20)
        df['volume_ratio'] = TechnicalIndicators.volume_ratio(volume, 20)
        
        # 均线金叉
        df['ma_golden_cross'] = TechnicalIndicators.golden_cross(df['ma5'], df['ma20'])
        
        return df
