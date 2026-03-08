"""
AI情绪分析模块
使用Kimi API分析股票新闻情绪
"""
import requests
import json
from typing import List, Dict
from config.settings import settings

class SentimentAnalyzer:
    """情绪分析器"""
    
    def __init__(self):
        self.api_key = settings.KIMI_API_KEY
        self.api_url = settings.KIMI_API_URL
    
    def analyze(self, stock_name: str, news_list: List[Dict]) -> Dict:
        """
        分析股票新闻情绪
        """
        if not news_list:
            return {'score': 0, 'label': '中性', 'summary': '暂无新闻'}
        
        if not self.api_key:
            return {'score': 0, 'label': '未配置', 'summary': 'Kimi API未配置'}
        
        # 构建新闻文本
        news_text = "\n".join([f"{i+1}. {n['title']}" for i, n in enumerate(news_list)])
        
        prompt = f"""请分析以下关于{stock_name}的新闻标题的情绪倾向。

新闻标题：
{news_text}

请按以下JSON格式返回分析结果：
{{
    "score": 情绪得分(-100到100，负值偏空，正值偏多，0为中性),
    "label": "偏多"或"偏空"或"中性",
    "summary": "一句话总结新闻要点和投资启示"
}}

只返回JSON，不要有其他内容。"""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'moonshot-v1-8k',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # 解析JSON
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                result = json.loads(content)
                return {
                    'score': result.get('score', 0),
                    'label': result.get('label', '中性'),
                    'summary': result.get('summary', '')
                }
            else:
                print(f"API调用失败: {response.status_code}")
                return {'score': 0, 'label': '错误', 'summary': f'API错误: {response.status_code}'}
                
        except Exception as e:
            print(f"情绪分析出错: {e}")
            return {'score': 0, 'label': '错误', 'summary': str(e)}
    
    def batch_analyze(self, stock_results: List[Dict]) -> List[Dict]:
        """
        批量分析股票情绪（仅分析得分最高的前10只以控制成本）
        """
        from data.fetcher import fetcher
        
        print("开始AI情绪分析...")
        for i, stock in enumerate(stock_results[:10]):
            print(f"分析 {stock['name']} ({i+1}/10)...")
            
            news = fetcher.get_stock_news(stock['code'], num=5)
            sentiment = self.analyze(stock['name'], news)
            stock['sentiment'] = sentiment
            stock['sentiment_score'] = sentiment['score']
            stock['sentiment_label'] = sentiment['label']
            
            # 综合得分 = 技术得分 + 情绪得分/10
            stock['total_score'] = stock['score'] + sentiment['score'] / 10
        
        # 重新排序
        stock_results.sort(key=lambda x: x.get('total_score', x['score']), reverse=True)
        return stock_results

# 全局实例
analyzer = SentimentAnalyzer()
