# reddit-community-research

> 系统性爬取 Reddit 社区数据并进行观点整合分析的 Hermes Agent Skill。

[![Skill Score](https://img.shields.io/badge/skill_score-92.3%2F100-brightgreen)](#)
[![Darwin Optimized](https://img.shields.io/badge/darwin-optimized-blue)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 简介

`reddit-community-research` 是一个专为 Hermes Agent 设计的 Skill，用于**系统性爬取 Reddit 社区数据并进行观点整合分析**。覆盖：

- subreddit 数据获取
- 用户痛点提取
- 情绪信号分析
- 功能需求优先级排序

**核心优势**：使用 [pullpush.io](https://api.pullpush.io/) 存档 API 绕过 Reddit 反爬限制，**无需 Reddit API 认证**。

## 适用场景

- 竞品社区用户反馈分析
- 社交媒体聆听 / 竞品调研
- 基于 Reddit 的用户需求分析
- 产品痛点挖掘与功能优先级排序

## 快速开始

### 前置依赖

```bash
python3 --version  # >= 3.8
python3 -m pip install requests --user
```

### 使用流程

```bash
# 1. 在 Hermes Agent 中触发 skill
# 触发词："爬取 Reddit 数据"、"分析竞品社区反馈"、"社交媒体聆听"

# 2. 按 Phase 执行（6 阶段流水线）
# Phase 1: 确认目标（subreddit / 关键词 / 数据量 / 时间范围）
# Phase 2: 环境检查（Python + requests）
# Phase 3: 数据爬取（pullpush.io API）
# Phase 4: 数据结构化（JSON 输出）
# Phase 5: 观点整合分析（痛点 / 情绪 / 需求）
# Phase 6: 输出交付（Markdown 报告）
```

### 最小代码示例

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
    params={"subreddit": "Gardyn", "size": 100, "sort": "desc"},
    headers=HEADERS,
    timeout=30
)
posts = resp.json()["data"]

# 获取评论
resp = requests.get(
    "https://api.pullpush.io/reddit/search/comment/",
    params={"subreddit": "Gardyn", "size": 100, "sort": "desc"},
    headers=HEADERS,
    timeout=30
)
comments = resp.json()["data"]
```

## Skill 结构

```
reddit-community-research/
├── SKILL.md                          # Skill 主文件（触发词 + 完整工作流）
├── references/
│   └── pullpush-pitfalls.md          # pullpush.io 非文档化陷阱
├── README.md                         # 本文件
└── LICENSE                           # MIT 许可证
```

## 核心特性

| 特性 | 说明 |
|------|------|
| **零认证** | 无需 Reddit API Key，直接使用 pullpush.io 存档数据 |
| **反爬铁律** | 同一方案失败 ≥2 次后自动切换策略 |
| **时间基准校准** | 自动处理 pullpush 数据延迟，避免时间计算错误 |
| **三段式 Fallback** | 每个已知问题都有「一线修复 → 仍失败兜底」的完整矩阵 |
| **反例黑名单** | 10 条常见反模式，防止踩坑 |
| **情绪信号提取** | 5 类情绪（愤怒/焦虑/困惑/失望/满意）自动识别 |
| **功能需求映射** | 6 类需求（水位监测/智能诊断/种植指导/空间管理/收获提醒/耗材补货） |

## 已知问题与规避

| 场景 | 一线修复 | 兜底方案 |
|------|---------|---------|
| pullpush 返回空数据 | 检查拼写、尝试双端点、扩大 size | 告知用户 subreddit 可能不存在或暂无存档 |
| pullpush 评论 API 400 | 改用 subreddit 参数全量获取，本地分组 | pullpush API 限制，非调用错误 |
| pullpush 数据时间滞后 | 采样查看最新时间，以此为基准往回推 | 向用户说明存档延迟 |
| pullpush 返回 5xx | 指数退避重试（5s → 10s → 20s） | 告知用户服务暂不可用，10 分钟后重试 |
| 关键词匹配零结果 | 双语关键词表（中文 → 英文） | 告知用户该话题讨论较少 |

详见 [`references/pullpush-pitfalls.md`](references/pullpush-pitfalls.md)。

## 评分历史

本 Skill 经过 [Darwin Skill](https://github.com/alchaincyf/darwin-skill) 自动优化，评分从 **57.3/100** 提升至 **92.3/100**。

| 轮次 | 变更 | 维度提升 |
|------|------|---------|
| R1 | 新增反例黑名单 8 条 | dim9: 2 → 8 (+3.6) |
| R2 | 4 个 CHECKPOINT 覆盖 Phase 1/2/3/6 | dim4: 2 → 7 (+3.0) |
| R3 | 已知问题表升级为三段式 fallback 矩阵 7 条 | dim3: 5 → 7 (+2.4) |

## 输出示例

分析完成后生成以下文件结构：

```
reddit_{subreddit}数据/
├── 帖子列表.json
├── 全部帖子及评论.json
├── 爬取统计.json
├── 数据分析摘要.json
├── 深度痛点分析.json
├── 观点整合报告.md
└── 痛点矩阵与功能需求深度分析.md
```

## 相关资源

- [pullpush.io API 文档](https://api.pullpush.io/)
- [Reddit API (PRAW)](https://praw.readthedocs.io/)
- [Hermes Agent 文档](https://hermes-agent.nousresearch.com/docs)

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。

---

> 本 Skill 由 Darwin Optimizer 自动优化，基于 Hermes Agent Skill 框架。
