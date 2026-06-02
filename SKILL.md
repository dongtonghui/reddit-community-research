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

### Phase 2: 环境检查

```bash
# 检查 Python 和 requests
python3 --version
python3 -c "import requests; print('requests OK')"
```

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

1. 所有 JSON 数据文件保存到 `~/workspace/reddit_{subreddit}数据/`
2. 生成 Markdown 分析报告
3. 将交付物复制到 workspace 目录

## 已知问题与规避

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Reddit 官方 API 401 | 需认证 | 使用 pullpush.io |
| Reddit JSON API 403 | 反爬拦截 | 使用 pullpush.io |
| Playwright GLIBC 错误 | 系统版本过低 | 避免使用，改用 API |
| pullpush 数据延迟 | 存档服务非实时 | 接受 T+1 延迟 |
| AutoModerator 噪音 | 自动欢迎消息 | 过滤 author="AutoModerator" |

## 代码模板

完整爬虫代码参考：`scripts/reddit_crawler_template.py`

核心依赖：
```bash
python3 -m pip install requests --user
```

## 相关资源

- pullpush.io API 文档: https://api.pullpush.io/
- Reddit API (PRAW): https://praw.readthedocs.io/
