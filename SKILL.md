---
name: reddit-community-research
description: >
  系统性爬取 Reddit 社区数据并进行观点整合分析。覆盖：subreddit 数据获取、
  用户痛点提取、情绪信号分析、功能需求优先级排序。使用 pullpush.io API
  绕过 Reddit 反爬限制，无需 Reddit API 认证。
triggers:
  - 用户要求爬取 Reddit 数据
  - 用户需要分析竞品社区用户反馈
  - 用户要求进行社交媒体聆听/竞品调研
  - 用户需要基于 Reddit 的用户需求分析
---

# Reddit 社区研究与观点整合

## 核心原则

> **反爬铁律**：同一方案失败 **≥2 次** 后，必须立即切换策略。
> Reddit 官方 API (PRAW) 和公开 JSON API 均已被反爬拦截，
> 直接使用 **pullpush.io 存档 API** 作为首选方案。

## 工具链优先级

| 优先级 | 方案 | 适用场景 | 状态 |
|--------|------|----------|------|
| 1 | **pullpush.io API** | 帖子/评论数据获取 | ✅ 推荐 |
| 2 | PRAW (Reddit API) | 需要认证的高频操作 | ⚠️ 需 client_id/secret |
| 3 | 浏览器自动化 | 需要渲染页面时 | ⚠️ 需 Playwright/CDP |
| 4 | 公开 JSON API | 简单数据获取 | ❌ 已返回 403 |

## 执行流程

### Phase 1: 确认目标

向用户确认：
1. 目标 subreddit 名称（如 r/Gardyn）
2. 关键词过滤（可选，不设则全量获取）
3. 数据量（建议 50-100 帖子）
4. 时间范围（pullpush 按时间倒序获取）

**🔴 CHECKPOINT · 🛑 STOP：确认以上 4 项后再进入 Phase 2。**

### Phase 2: 环境检查

```bash
# 检查 Python 和 requests
python3 --version
python3 -c "import requests; print('requests OK')"
```

如果 requests 未安装：`python3 -m pip install requests --user`

### Phase 3: 数据爬取

使用 pullpush.io API：

```python
import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# 获取帖子
resp = requests.get(
    "https://api.pullpush.io/reddit/search/submission/",
    params={"subreddit": "SUBREDDIT_NAME", "size": 100, "sort": "desc"},
    headers=HEADERS,
    timeout=30
)
posts = resp.json()["data"]

# 获取评论
resp = requests.get(
    "https://api.pullpush.io/reddit/search/comment/",
    params={"subreddit": "SUBREDDIT_NAME", "size": 100, "sort": "desc"},
    headers=HEADERS,
    timeout=30
)
comments = resp.json()["data"]
```

**分页逻辑**：
- 使用 `before` 参数，值为上一批数据的最小 `created_utc`
- 每批间隔 0.5s，避免 rate limit

**🔴 CHECKPOINT：爬取完成后检查 `data` 是否为空。空数据 → 告知用户 "subreddit 可能不存在或暂无存档数据"，不要进入 Phase 4。**

### Phase 4: 数据结构化

输出文件结构：
```
reddit_{subreddit}数据/
├── 帖子列表.json              # 帖子基础数据
├── 帖子_{id}.json            # 单篇帖子 + 评论
├── 全部帖子及评论.json        # 完整数据集
├── 爬取统计.json              # 元数据与统计
├── 数据分析摘要.json          # 关键词/痛点/互动分析
├── 深度痛点分析.json          # 结构化痛点归属
├── 观点整合报告.md            # 社区概况 + 战略启示
└── 痛点矩阵与功能需求深度分析.md  # 完整分析
```

### Phase 5: 观点整合分析

#### 5.1 痛点分类体系

| 类别 | 关键词示例 |
|------|-----------|
| 水位/灌溉系统 | water, leak, pump, drain, reservoir, refill |
| 发芽/幼苗死亡 | germination, sprout, die, wilt, seedling |
| 霉菌/藻类/病害 | mold, algae, slime, fungus, mildew, disease |
| 营养/肥料问题 | food, nutrient, fertilizer, deficiency, burn |
| 光照/空间布局 | light, crowd, space, layout, block, position |
| 硬件故障 | not working, broken, error, malfunction |
| 根系管理 | root, trim, control, plug, drain hole |
| 收获/采收时机 | harvest, flower, bolting, ready, ripe |
| 软件/App体验 | app, notification, subscription, software |
| 耗材/配件 | rockwool, ycube, pod, cover, seed |

#### 5.2 情绪信号提取

| 情绪 | 关键词 |
|------|--------|
| 愤怒/挫败 | mad, angry, frustrated, absurd, rant |
| 焦虑/担忧 | worried, concern, nervous, stress |
| 困惑/求助 | confused, help, what is, how, unsure |
| 失望/后悔 | disappointed, regret, waste, expensive |
| 满意/喜悦 | happy, excited, love, proud, success |

#### 5.3 功能需求提取

| 需求 | 关键词 |
|------|--------|
| 水位监测/预警 | water level, low water, refill, notification |
| 智能诊断/AI医生 | what is this, identify, diagnose, normal |
| 种植指导/教程 | how to, tips, advice, guide, first time |
| 空间管理助手 | crowd, space, layout, arrange, block |
| 收获时机提醒 | when to harvest, ready, flower, bolting |
| 耗材自动补货 | run out, need more, order, alternative |

### Phase 6: 输出交付

**🔴 CHECKPOINT · 🛑 STOP：交付前确认所有 JSON + MD 文件已生成。向用户展示文件清单和关键发现摘要，等用户确认是否需要补充分析。**

1. 所有 JSON 数据文件保存到 `~/workspace/reddit_{subreddit}数据/`
2. 生成 Markdown 分析报告
3. 将交付物复制到 workspace 目录

## 已知问题与规避

| 场景 | 触发条件 | 一线修复 | 仍失败兜底 |
|------|---------|---------|-----------|
| **pullpush 返回空数据** | `resp.json()["data"]` 为空数组 | ① 检查 subreddit 名称拼写（`curl -sI https://reddit.com/r/xxx/` 确认存在）② 尝试 `search/submission/` 和 `search/comment/` 两个端点 ③ 扩大 size 到 100 | 告知用户："该 subreddit 在 pullpush 存档中无数据。可能原因：subreddit 不存在、设为私有、或为新创建暂无存档。建议换一个 subreddit 或尝试 PRAW。" |
| **pullpush 返回 5xx** | HTTP 状态码 ≥500 | ① 等待 5s 重试 ② 指数退避：10s → 20s → 40s，最多 3 次 | 告知用户 pullpush 服务暂不可用，建议 10 分钟后重试。不静默跳过 |
| **Reddit 官方 API 401** | 需认证 | 使用 pullpush.io（本技能首选方案） | 若 pullpush 也不可用，询问用户是否有 Reddit client_id/secret 用于 PRAW |
| **Playwright GLIBC 错误** | 系统版本过低 | 避免使用浏览器方案，切换到 pullpush API | N/A — 本技能不依赖 Playwright |
| **AutoModerator 噪音** | 数据中 author="AutoModerator" 占比 >10% | Phase 4 数据结构化时过滤 `author='AutoModerator'` 和 `body='[deleted]'` | 若过滤后数据量 <20，告知用户数据稀疏，建议扩大 size 参数 |
| **requests 未安装** | `import requests` 失败 | `python3 -m pip install requests --user` | 若 pip 不可用，尝试 `apt-get install python3-requests` |
| **关键词匹配零结果** | 中文关键词在英文内容中无命中 | 使用双语关键词表（见反例黑名单 #7）。切换为英文关键词重试 | 若双语均无结果，告知用户该话题在该社区讨论较少 |

## 代码模板

完整爬虫代码参考：`scripts/reddit_crawler_template.py`

核心依赖：
```bash
python3 -m pip install requests --user
```

## 相关资源

- pullpush.io API 文档: https://api.pullpush.io/
- Reddit API (PRAW): https://praw.readthedocs.io/

---

## 反例与黑名单（不要做的事）

| # | 反模式 | 为什么不要做 | 正确做法 |
|---|--------|-----------|---------|
| 1 | **直接用 `curl reddit.com/r/xxx.json`** | Reddit JSON API 已全面返回 403，浪费时间 | 首选 pullpush.io 存档 API，备选 PRAW |
| 2 | **不确认 subreddit 是否存在就开始爬** | `r/NonExistentSub` 返回空数据，静默失败 | Phase 1 用 `curl -sI https://reddit.com/r/xxx/` 检查 HTTP 状态码 |
| 3 | **一次性请求 500+ 条数据不设分页** | pullpush 单次上限 ~100 条，超量截断 | 使用 `before` 参数分页，每批 100 条，间隔 0.5s |
| 4 | **不过滤 AutoModerator 和 [deleted]** | 噪音污染数据分析，AutoMod 欢迎消息无分析价值 | Phase 4 数据结构化时过滤 `author='AutoModerator'` 和 `body='[deleted]'` |
| 5 | **用 Playwright 爬 Reddit** | GLIBC 版本兼容问题频发，环境依赖重 | 除非需要登录态内容，否则用 API 方案 |
| 6 | **空数据静默跳过不报错** | 用户等半天不知道数据是空的还是爬失败了 | pullpush 返回 `data:[]` 时显式告知："subreddit 可能不存在或暂无存档数据" |
| 7 | **关键词过滤用中文匹配英文内容** | 中文关键词（"水泵"）无法匹配英文帖子（"pump"） | 双语关键词表：`{"灌溉": ["water","pump","irrigation"], "霉菌": ["mold","algae","fungus"]}` |
| 8 | **分析报告无优先级排序** | 30 条痛点平铺，用户不知道先修哪个 | 按提及频次 × 情绪强度排序，Top 5 放报告开头 |

### 触发场景

Phase 5 分析生成前对照本表逐条检查。任一反模式命中 → 修复后继续。
