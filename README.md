# A股AI股票筛选器 - 增强版

一个功能完整的A股量化筛选系统，支持多因子筛选、AI情绪分析、飞书实时推送、策略回测。

## 功能特性

- 📊 **多因子筛选**：P/E、RSI、MACD、布林带、ATR、成交量、均线金叉
- 🤖 **AI情绪分析**：Kimi API分析新闻情绪，识别利好/利空
- 📱 **实时推送**：飞书/钉钉/企业微信机器人推送
- 📈 **策略回测**：验证筛选策略的历史表现
- ⏰ **定时运行**：GitHub Actions或本地cron自动执行
- 🎯 **自选监控**：自定义股票池监控

## 技术栈

| 组件 | 用途 | 成本 |
|------|------|------|
| akshare | A股实时数据 | 免费 |
| pandas/ta-lib | 技术分析 | 免费 |
| Kimi API | AI情绪分析 | ~¥50/月（高频） |
| 飞书Webhook | 消息推送 | 免费 |
| GitHub Actions | 定时调度 | 免费(2000分钟/月) |

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env`，填入你的API密钥：
```bash
cp .env.example .env
```

### 3. 运行筛选
```bash
python screener.py
```

### 4. 运行回测
```bash
python backtest.py
```

## 项目结构

```
stock-screener/
├── config/
│   └── settings.py          # 配置管理
├── data/
│   ├── fetcher.py           # 数据获取
│   └── cache.py             # 数据缓存
├── indicators/
│   ├── technical.py         # 技术指标计算
│   └── screener.py          # 筛选逻辑
├── ai/
│   └── sentiment.py         # AI情绪分析
├── notification/
│   ├── feishu.py            # 飞书推送
│   ├── dingtalk.py          # 钉钉推送
│   └── wechat.py            # 企业微信推送
├── backtest/
│   ├── engine.py            # 回测引擎
│   └── report.py            # 回测报告
├── utils/
│   └── logger.py            # 日志工具
├── screener.py              # 主程序（筛选）
├── backtest.py              # 回测主程序
├── requirements.txt
├── .env.example
└── README.md
```

## 筛选条件说明

### 基础条件
- **市盈率**：5-25倍（排除高估和亏损股）
- **成交量**：> 20日均量1.5倍（放量）
- **市值**：> 50亿（流动性）

### 技术指标
- **RSI**：30-70（非极端）
- **MACD**：金叉（DIF上穿DEA）
- **布林带**：价格突破中轨向上
- **ATR**：近5日ATR > 前5日（波动放大）
- **均线**：5日线上穿20日线（金叉）

## 回测功能

```bash
# 回测过去6个月的筛选策略
python backtest.py --period 6m --output report.html
```

## 定时运行

### GitHub Actions
已配置 `.github/workflows/screener.yml`，每天9:00自动运行（开盘前）。

### 本地Cron
```bash
# 编辑crontab
crontab -e

# 添加（工作日9:00运行）
0 9 * * 1-5 cd /path/to/stock-screener && python screener.py >> logs/screener.log 2>&1
```

## License

MIT
