"""
策略回测引擎
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta
from data.fetcher import fetcher
from config.settings import settings

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self):
        self.config = settings.BACKTEST
    
    def backtest_stock(self, code: str, start_date: str, end_date: str) -> Dict:
        """
        单只股票回测
        模拟买入信号出现后的表现
        """
        df = fetcher.get_kline(code, days=120)
        if len(df) < 60:
            return None
        
        trades = []
        position = None
        
        for i in range(40, len(df) - self.config['hold_days']):
            if position is None:
                # 检查买入信号
                signal = self._check_buy_signal(df, i)
                if signal:
                    position = {
                        'entry_date': df.iloc[i]['date'],
                        'entry_price': df.iloc[i]['close'],
                        'signal_score': signal['score']
                    }
            else:
                # 检查卖出条件
                exit_signal = self._check_sell(df, i, position)
                if exit_signal:
                    exit_price = df.iloc[i]['close']
                    pnl = (exit_price - position['entry_price']) / position['entry_price']
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': df.iloc[i]['date'],
                        'entry_price': round(position['entry_price'], 2),
                        'exit_price': round(exit_price, 2),
                        'pnl_pct': round(pnl * 100, 2),
                        'hold_days': (datetime.strptime(df.iloc[i]['date'], '%Y-%m-%d') - 
                                     datetime.strptime(position['entry_date'], '%Y-%m-%d')).days,
                        'exit_reason': exit_signal['reason']
                    })
                    position = None
        
        if not trades:
            return None
        
        # 计算统计数据
        df_trades = pd.DataFrame(trades)
        wins = len(df_trades[df_trades['pnl_pct'] > 0])
        losses = len(df_trades[df_trades['pnl_pct'] <= 0])
        
        return {
            'code': code,
            'total_trades': len(trades),
            'win_rate': round(wins / len(trades) * 100, 2),
            'avg_pnl': round(df_trades['pnl_pct'].mean(), 2),
            'avg_win': round(df_trades[df_trades['pnl_pct'] > 0]['pnl_pct'].mean(), 2) if wins > 0 else 0,
            'avg_loss': round(df_trades[df_trades['pnl_pct'] <= 0]['pnl_pct'].mean(), 2) if losses > 0 else 0,
            'max_pnl': round(df_trades['pnl_pct'].max(), 2),
            'min_pnl': round(df_trades['pnl_pct'].min(), 2),
            'avg_hold_days': round(df_trades['hold_days'].mean(), 1),
            'trades': trades
        }
    
    def _check_buy_signal(self, df: pd.DataFrame, idx: int) -> Dict:
        """检查买入信号"""
        from indicators.technical import TechnicalIndicators
        
        # 计算指标
        df_calc = df.iloc[:idx+1].copy()
        df_calc = TechnicalIndicators.calculate_all(df_calc)
        
        if len(df_calc) < 30:
            return None
        
        latest = df_calc.iloc[-1]
        prev = df_calc.iloc[-2]
        
        # 买入条件
        conditions = []
        
        # MACD金叉
        if latest['macd_golden_cross'] or (latest['macd_dif'] > latest['macd_dea'] and 
                                           prev['macd_dif'] <= prev['macd_dea']):
            conditions.append('macd')
        
        # 均线金叉
        if latest['ma_golden_cross'] or (latest['ma5'] > latest['ma20'] and 
                                         prev['ma5'] <= prev['ma20']):
            conditions.append('ma_cross')
        
        # 成交量放大
        if latest['volume_ratio'] > 1.5:
            conditions.append('volume')
        
        # RSI在合理区间
        if 30 <= latest['rsi'] <= 70:
            conditions.append('rsi')
        
        # 布林带
        if 0.4 < latest['bb_position'] < 0.8:
            conditions.append('bb')
        
        if len(conditions) >= 3:
            return {'score': len(conditions) * 20}
        return None
    
    def _check_sell(self, df: pd.DataFrame, idx: int, position: Dict) -> Dict:
        """检查卖出信号"""
        current_price = df.iloc[idx]['close']
        entry_price = position['entry_price']
        entry_idx = df[df['date'] == position['entry_date']].index[0]
        hold_days = idx - entry_idx
        
        pnl = (current_price - entry_price) / entry_price
        
        # 止盈
        if pnl >= self.config['take_profit']:
            return {'reason': '止盈'}
        
        # 止损
        if pnl <= -self.config['stop_loss']:
            return {'reason': '止损'}
        
        # 最大持有期
        if hold_days >= self.config['hold_days']:
            return {'reason': '到期'}
        
        # MACD死叉
        if idx > 0:
            from indicators.technical import TechnicalIndicators
            df_slice = df.iloc[:idx+1].copy()
            df_slice = TechnicalIndicators.calculate_all(df_slice)
            if len(df_slice) > 1:
                latest = df_slice.iloc[-1]
                prev = df_slice.iloc[-2]
                if latest['macd_dif'] < latest['macd_dea'] and prev['macd_dif'] >= prev['macd_dea']:
                    return {'reason': 'MACD死叉'}
        
        return None
    
    def run_backtest(self, codes: List[str]) -> List[Dict]:
        """批量回测"""
        results = []
        for code in codes:
            print(f"回测 {code}...")
            result = self.backtest_stock(code, None, None)
            if result:
                results.append(result)
        return results
