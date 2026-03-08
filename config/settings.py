"""
配置管理模块
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """应用配置"""
    
    # 飞书配置
    FEISHU_WEBHOOK_URL = os.getenv('FEISHU_WEBHOOK_URL', '')
    
    # Kimi API配置
    KIMI_API_KEY = os.getenv('KIMI_API_KEY', '')
    KIMI_API_URL = 'https://api.moonshot.cn/v1/chat/completions'
    
    # 钉钉配置
    DINGTALK_WEBHOOK_URL = os.getenv('DINGTALK_WEBHOOK_URL', '')
    DINGTALK_SECRET = os.getenv('DINGTALK_SECRET', '')
    
    # 企业微信配置
    WECHAT_WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL', '')
    
    # 邮件配置
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    
    # 筛选参数
    SCREENING = {
        'pe_min': 5,
        'pe_max': 25,
        'rsi_min': 30,
        'rsi_max': 70,
        'volume_ratio': 1.5,  # 成交量/20日均量
        'min_market_cap': 50,  # 最小市值(亿)
        'price_min': 3,  # 最小股价
        'max_stocks': 50,  # 最多分析股票数（控制API成本）
    }
    
    # 回测参数
    BACKTEST = {
        'initial_capital': 100000,  # 初始资金
        'position_size': 0.2,  # 单笔仓位(20%)
        'stop_loss': 0.08,  # 止损8%
        'take_profit': 0.15,  # 止盈15%
        'hold_days': 20,  # 最长持有天数
    }

settings = Settings()
