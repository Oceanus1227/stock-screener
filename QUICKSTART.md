# 🚀 快速开始指南

## 1. 安装（5分钟）

```bash
# 克隆或下载代码
cd stock-screener

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 2. 配置（5分钟）

### 2.1 配置飞书机器人

1. 在飞书群聊中添加「自定义机器人」
2. 复制 Webhook URL
3. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```
4. 编辑 `.env`，填入：
   ```
   FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
   ```

### 2.2 配置Kimi API（可选，用于AI情绪分析）

1. 访问 [Kimi开放平台](https://platform.moonshot.cn/)
2. 注册并创建API Key
3. 在 `.env` 中添加：
   ```
   KIMI_API_KEY=sk-xxxxx
   ```

## 3. 运行（1分钟）

### 方式一：实时筛选（推荐体验）
```bash
python screener.py
```

### 方式二：自选股票池筛选
```bash
# 编辑 watchlist.txt 添加你想监控的股票
python screener.py --watchlist watchlist.txt
```

### 方式三：回测验证策略
```bash
python backtest.py --top 30
```
打开生成的 `backtest_report.html` 查看结果

## 4. 自动化部署（GitHub Actions）

### 4.1 推送到GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/stock-screener.git
git push -u origin main
```

### 4.2 配置Secrets
在 GitHub 仓库 → Settings → Secrets and variables → Actions 中添加：

| Secret Name | Value |
|------------|-------|
| `FEISHU_WEBHOOK_URL` | 你的飞书Webhook URL |
| `KIMI_API_KEY` | Kimi API Key（可选） |

### 4.3 自动运行
工作流已配置为：
- ⏰ 工作日 9:00 自动运行（开盘前30分钟）
- 🖱️ 支持手动触发
- 📊 自动推送结果到飞书

## 5. 自定义筛选条件

编辑 `config/settings.py` 中的 `SCREENING` 字典：

```python
SCREENING = {
    'pe_min': 5,        # 最小市盈率
    'pe_max': 25,       # 最大市盈率
    'rsi_min': 30,      # RSI下限
    'rsi_max': 70,      # RSI上限
    'volume_ratio': 1.5, # 量比（成交量/20日均量）
    'min_market_cap': 50, # 最小市值(亿)
    'price_min': 3,     # 最小股价
}
```

## 6. 成本估算

| 项目 | 费用 | 说明 |
|------|------|------|
| GitHub Actions | ¥0 | 免费2000分钟/月 |
| akshare数据 | ¥0 | 开源免费 |
| Kimi API | ¥0-50/月 | 免费额度充足，高频约50元/月 |
| 飞书推送 | ¥0 | 免费 |
| **总计** | **¥0-50/月** | 对比Bloomberg ¥22万/年 |

## 7. 常见问题

### Q: 运行时报错 akshare 找不到数据？
A: 确保网络连接正常，akshare 需要从东方财富等网站获取数据。

### Q: 飞书收不到消息？
```bash
# 测试飞书配置
python -c "from notification.feishu import feishu; feishu.send_simple('测试消息')"
```

### Q: 如何只运行筛选不推送？
```bash
python screener.py --no-push
```

### Q: 如何跳过AI分析节省成本？
```bash
python screener.py --no-ai
```

## 8. 后续优化建议

1. **增加更多数据源**：接入Wind/Tushare Pro
2. **加入更多指标**：KDJ、OBV、资金流向
3. **机器学习筛选**：用历史数据训练选股模型
4. **实盘跟踪**：记录每日筛选结果，追踪后续表现

---

**⚠️ 免责声明**：本工具仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。
