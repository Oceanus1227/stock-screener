"""
飞书推送模块
"""
import requests
import json
from typing import List, Dict
from datetime import datetime
from config.settings import settings

class FeishuNotifier:
    """飞书机器人推送"""
    
    def __init__(self):
        self.webhook_url = settings.FEISHU_WEBHOOK_URL
    
    def send_card(self, title: str, stocks: List[Dict]) -> bool:
        """发送富文本卡片消息"""
        if not self.webhook_url:
            print("飞书Webhook未配置")
            return False
        
        # 构建表格内容
        table_content = []
        for i, s in enumerate(stocks[:15], 1):
            sentiment_tag = s.get('sentiment_label', '-')
            sentiment_color = "green" if sentiment_tag == "偏多" else "red" if sentiment_tag == "偏空" else "grey"
            
            table_content.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{i}. {s['name']}** ({s['code']}) | 得分: {s.get('total_score', s['score']):.1f} | 情绪: <font color='{sentiment_color}'>{sentiment_tag}</font>"
                }
            })
            table_content.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"💰 价格: ¥{s['price']} | 📈 涨跌幅: {s['change_pct']}% | 📊 RSI: {s['rsi']} | 🔊 量比: {s['volume_ratio']}"
                }
            })
            table_content.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"🚩 信号: {', '.join(s['signals'])}"
                }
            })
            
            if 'sentiment' in s and s['sentiment'].get('summary'):
                table_content.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"🤖 AI: {s['sentiment']['summary'][:80]}..."
                    }
                })
            
            table_content.append({"tag": "hr"})
        
        card = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"📊 {title} - {datetime.now().strftime('%m-%d %H:%M')}"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"筛选出 **{len(stocks)}** 只符合条件的股票，以下是得分前15名："
                        }
                    },
                    {"tag": "hr"},
                    *table_content,
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": "⚠️ 本报告由AI自动生成，仅供参考，不构成投资建议"
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(self.webhook_url, json=card, timeout=10)
            if response.status_code == 200:
                print("飞书推送成功")
                return True
            else:
                print(f"飞书推送失败: {response.text}")
                return False
        except Exception as e:
            print(f"飞书推送错误: {e}")
            return False
    
    def send_simple(self, message: str) -> bool:
        """发送简单文本消息"""
        if not self.webhook_url:
            return False
        
        payload = {
            "msg_type": "text",
            "content": {"text": message}
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"推送错误: {e}")
            return False

# 全局实例
feishu = FeishuNotifier()
