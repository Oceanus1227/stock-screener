#!/usr/bin/env python3
"""
策略回测程序

用法:
    python backtest.py                      # 回测默认股票池
    python backtest.py --codes 000001,000002  # 回测指定股票
    python backtest.py --top 50             # 回测成交额前50的股票
    python backtest.py --output report.html # 指定输出文件
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backtest.engine import BacktestEngine
from backtest.report import BacktestReport
from data.fetcher import fetcher

def main():
    parser = argparse.ArgumentParser(description='股票筛选策略回测')
    parser.add_argument('--codes', type=str, help='回测股票代码，逗号分隔')
    parser.add_argument('--top', type=int, default=30, help='回测成交额前N的股票')
    parser.add_argument('--output', type=str, default='backtest_report.html', help='输出文件')
    args = parser.parse_args()
    
    print("="*60)
    print("📊 策略回测启动")
    print("="*60)
    
    # 获取回测股票列表
    if args.codes:
        codes = args.codes.split(',')
    else:
        print(f"获取成交额前{args.top}的股票...")
        stock_list = fetcher.get_stock_list()
        stock_list = stock_list.sort_values('volume', ascending=False).head(args.top)
        codes = stock_list['code'].tolist()
    
    print(f"回测股票数: {len(codes)}")
    
    # 运行回测
    engine = BacktestEngine()
    results = engine.run_backtest(codes)
    
    if not results:
        print("❌ 没有产生有效交易信号")
        return
    
    # 生成报告
    report = BacktestReport()
    report.generate_html(results, args.output)
    
    print("\n✅ 回测完成！")

if __name__ == '__main__':
    main()
