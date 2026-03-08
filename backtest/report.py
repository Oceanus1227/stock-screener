"""
回测报告生成
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict

class BacktestReport:
    """回测报告生成器"""
    
    def generate_html(self, results: List[Dict], output_file: str = 'backtest_report.html'):
        """生成HTML报告"""
        if not results:
            print("没有回测结果")
            return
        
        df = pd.DataFrame([{
            '代码': r['code'],
            '交易次数': r['total_trades'],
            '胜率(%)': r['win_rate'],
            '平均收益(%)': r['avg_pnl'],
            '平均盈利(%)': r['avg_win'],
            '平均亏损(%)': r['avg_loss'],
            '最大收益(%)': r['max_pnl'],
            '最大亏损(%)': r['min_pnl'],
            '平均持仓(天)': r['avg_hold_days']
        } for r in results])
        
        # 计算组合统计
        total_trades = sum(r['total_trades'] for r in results)
        avg_win_rate = df['胜率(%)'].mean()
        avg_return = df['平均收益(%)'].mean()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>股票筛选策略回测报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
        .summary {{ background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary-item {{ display: inline-block; margin: 10px 20px; }}
        .summary-label {{ color: #666; font-size: 14px; }}
        .summary-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .positive {{ color: #4CAF50; }}
        .negative {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 股票筛选策略回测报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h3>📈 组合统计</h3>
            <div class="summary-item">
                <div class="summary-label">回测股票数</div>
                <div class="summary-value">{len(results)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">总交易次数</div>
                <div class="summary-value">{total_trades}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">平均胜率</div>
                <div class="summary-value">{avg_win_rate:.1f}%</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">平均收益</div>
                <div class="summary-value" style="color: {'#4CAF50' if avg_return > 0 else '#f44336'}">
                    {avg_return:.2f}%
                </div>
            </div>
        </div>
        
        <h2>详细回测结果</h2>
        {df.to_html(index=False, classes='data-table', escape=False)}
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"回测报告已生成: {output_file}")
        
        # 打印摘要
        print("\n" + "="*60)
        print("回测结果摘要")
        print("="*60)
        print(f"回测股票数: {len(results)}")
        print(f"总交易次数: {total_trades}")
        print(f"平均胜率: {avg_win_rate:.1f}%")
        print(f"平均收益: {avg_return:.2f}%")
        print(f"排名前5:\n")
        top5 = df.nlargest(5, '平均收益(%)')[['代码', '交易次数', '胜率(%)', '平均收益(%)']]
        print(top5.to_string(index=False))
