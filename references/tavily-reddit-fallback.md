# Tavily 作为 Reddit 社区情报备选方案与月度监测工作流

当 pullpush.io 不可用（502/超时）或用户需要定期产出竞品社区报告时，使用 Tavily 可以在 1-2 分钟内获得带分类、频次和引用的综合报告，无需处理 Reddit 反爬。

## 适用场景

- pullpush.io 返回 502/429/超时
- 不需要原始帖子全量数据，只需要痛点分类和典型引用
- 竞品快速扫描（Gardyn、AeroGarden、LettuceGrow 等）
- 时间紧，先做快速情报，再决定是否投入深度爬取
- **月度/定期监测**：需要每月自动抓取多个品牌并输出可视化报告

## 不适用场景

- 需要完整评论树和逐条分析
- 需要精确时间范围（Tavily 对 Reddit 的抓取有延迟）
- 需要大规模数据集训练/打标

## 操作模式

### 模式 A：快速综合（推荐）

```bash
tvly research "Gardyn indoor garden Reddit complaints problems pain points 2024 2025" --model mini --json
```

输出结构：
- 分类痛点（硬件、软件、订阅、维护等）
- 提及频次
- 严重程度
- 用户原声引用
- 来源 URL 列表

### 模式 B：原始帖子列表

```bash
tvly search "site:reddit.com/r/Gardyn pump failed OR lid issues OR subscription cost 2024" --max-results 10 --json
```

输出结构：
- 10 条具体帖子标题/URL/摘录
- 可进一步用 Tavily extract 或 browser 深入阅读

## 月度监测工作流

把 Tavily 作为主力来源时，可建立每月自动跑的竞品社区监测：

```python
# scripts/run_monthly_research.py
import json, os, subprocess, shlex, time
from datetime import datetime

BRANDS = ["Gardyn", "AeroGarden", "LettuceGrow"]
API_KEY=os.env...ndef run_research(query):
    cmd = f"tvly research {shlex.quote(query)} --model mini --json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env={**os.environ, "TAVILY_API_KEY": API_KEY})
    return json.loads(result.stdout) if result.returncode == 0 else None

for brand in BRANDS:
    query = f"{brand} indoor garden Reddit complaints problems pain points last 12 months"
    data = run_research(query)
    if data:
        with open(f"data/{brand.lower()}_pain_points_{datetime.now().strftime('%Y-%m-%d')}.json", "w") as f:
            json.dump(data, f, indent=2)
    time.sleep(2)
```

配合 huashu-design 的 `research-to-deck-template.md`，把 JSON 转译为 9 页产品决策 deck：
- 封面 / 方法 / 发现 1 / 发现 2 / 优先级 / 真实痛点 / 情绪 / 结论 / 建议

cron 示例：

```bash
0 9 1 * * cd /path/to/project && bash scripts/run_pipeline.sh
```

## 实测案例：Gardyn 痛点研究

**背景**：用户需要了解 Gardyn 植物种植机在 Reddit 上的最近一年痛点。

**测试结果**：

| 方法 | 结果 | 耗时 |
|------|------|------|
| `tvly research` | ✅ 成功：7 大痛点、18 条来源、 severity 排序 | ~45 秒 |
| `tvly search` | ✅ 成功：10 条具体帖子 | ~2 秒 |
| pullpush.io | ❌ 502 Bad Gateway | - |
| old.reddit 直接抓取 | ❌ 被反爬拦截 | - |

**核心发现（来自 Tavily 报告）**：

1. 硬件可靠性（9 帖）：水泵/盖子腐蚀、传感器失效是最大痛点
2. App/软件故障（7 帖）：Wi-Fi 断连、配对失败、服务端更新导致设备离线
3. 植物生长表现（5 帖）：30 pod 空间拥挤、thinning 困惑、产量不稳定
4. 订阅/价格（5 帖）：年费 $120-240 被认为过贵
5. 设置与维护（4 帖）：加水量指南不清、Wi-Fi 重连问题

**型号趋势**：
- Gardyn 3.0：泵和盖故障最多
- Gardyn 2.0：2024 年 3 月服务端更新导致大量设备故障
- Gardyn 4.0：UI  sluggish、社交功能弱

## 与 pullpush 的互补关系

| 维度 | pullpush | Tavily |
|------|----------|--------|
| 数据完整度 | 高（可拿全量帖子+评论） | 中（仅索引到的页面） |
| 速度 | 慢（需分页、去重、分析） | 快（1-2 分钟出报告） |
| 反爬风险 | 中（第三方服务可能 down） | 低 |
| 结构化输出 | 需自己处理 | 自带分类总结 |
| 原始评论 | 可获取 | 不可获取 |
| 自动化友好度 | 中（需写分页、去重、错误处理） | 高（一条命令出一个品牌报告） |

## 工作流程建议

```
Phase 1: 尝试 pullpush.io 快速采样
  ↓ 成功 → 进入完整社区分析流程
  ↓ 失败（502/429/空数据） → 切换到 Tavily 快速模式

Phase 2: Tavily 输出初步假设 + 关键引用

Phase 3（可选）：根据 Tavily 发现的帖子 URL，用 browser 或 extract 深入阅读高价值帖子

Phase 4（监测场景）：多个品牌批量抓取 → 生成结构化 JSON → 用 huashu-design 转译成 deck

Phase 5: 在报告中标注数据局限性（"基于 Tavily 索引，非全量 Reddit 数据"）
```

## 报告局限性标注模板

```markdown
> 数据来源：Tavily 对 Reddit 公开帖子的索引，非 Reddit 全量数据。
> 局限性：可能缺少最新帖子、评论细节和已删除内容。
> 建议：如需全量分析，请在 pullpush.io 恢复后补充原始数据爬取。
```

## 相关技能

- `tavily-search` — 快速搜索特定关键词/站点的 Reddit 帖子
- `tavily-research` — 综合研究和分类输出
- `huashu-design` — 研究结论转 HTML Deck，见 `research-to-deck-template.md`
- `reddit-community-research` — 主技能，pullpush 可用时的完整流程
