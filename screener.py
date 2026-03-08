#!/usr/bin/env python3
"""
A股AI股票筛选器 - 主程序

用法:
    python screener.py                    # 运行筛选
    python screener.py --no-ai            # 跳过AI情绪分析
    python screener.py --max 100          # 最多分析100只股票
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from indicators.screener import StockScreener
from ai.sentiment import analyzer
from notification.feishu import feishu
from data.fetcher import fetcher

def main():
    parser = argparse.ArgumentParser(description='A股AI股票筛选器')
    parser.add_argument('--no-ai', action='store_true', help='跳过AI情绪分析')
    parser.add_argument('--max', type=int, default=None, help='最多分析的股票数量')
    parser.add_argument('--no-push', action='store_true', help='不推送消息')
    parser.add_argument('--watchlist', type=str, default=None, help='自选股票池文件(每行一个代码)')
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 A股AI股票筛选器启动")
    print("="*60)
    
    # 初始化筛选器
    screener = StockScreener()
    
    # 运行筛选
    if args.watchlist and Path(args.watchlist).exists():
        # 自选股票池模式
        print(f"读取自选股票池: {args.watchlist}")
        with open(args.watchlist, 'r') as f:
            codes = [line.strip() for line in f if line.strip()]
        
        results = []
        for code in codes:
            result = screener.screen_stock(code)
            if result:
                stock_info = fetcher.get_stock_list()
                info = stock_info[stock_info['code'] == code]
                if not info.empty:
                    result['name'] = info.iloc[0]['name']
                    result['pe'] = round(info.iloc[0]['pe'], 2) if pd.notna(info.iloc[0]['pe']) else None
                    result['market_cap'] = round(info.iloc[0]['market_cap'], 2)
                results.append(result)
    else:
        # 全市场筛选
        results = screener.run_screening(max_stocks=args.max)
    
    if not results:
        print("❌ 未找到符合条件的股票")
        feishu.send_simple("📊 今日筛选结果：未找到符合条件的股票")
        return
    
    print(f"\n✅ 筛选完成，共找到 {len(results)} 只符合条件的股票")
    
    # AI情绪分析
    if not args.no_ai:
        results = analyzer.batch_analyze(results)
    
    # 打印结果
    print("\n" + "="*60)
    print("📈 筛选结果 TOP 10")
    print("="*60)
    for i, r in enumerate(results[:10], 1):
        sentiment = f"[{r.get('sentiment_label', '-')}]" if 'sentiment_label' in r else ""
        total = f"综合:{r.get('total_score', r['score']):.1f}" if 'total_score' in r else f"技术:{r['score']}"
        print(f"{i}. {r['name']}({r['code']}) ¥{r['price']} {sentiment} {total}")
        print(f"   信号: {', '.join(r['signals'])} | RSI:{r['rsi']} 量比:{r['volume_ratio']}")
        if 'sentiment' in r and r['sentiment'].get('summary'):
            print(f"   AI: {r['sentiment']['summary'][:60]}...")
        print()
    
    # 推送飞书
    if not args.no_push:
        feishu.send_card("A股AI筛选报告", results)
    
    print("\n✅ 完成！")

if __name__ == '__main__':
    import pandas as pd  # 用于自选模式
    main()
