# Reddit share 短链接解析失败处理

> 来源会话：2026-07-02 · 植物种植机耗材/订阅定价研究 · r/gardyn

## 现象

用户给出的 Reddit share 链接形如：

```
https://www.reddit.com/r/Gardyn/s/nx2NRbY8I7
```

- `curl -sIL` 跟随重定向时返回 403。
- 浏览器自动化在受限环境（无完整 Chromium/GLIBC 问题）下也无法解析。
- 该短码只对应一个帖子，但无法直接映射到 `permalink`。

## 原因

Reddit share URL 需要登录态或客户端 JS 解析，autonomous fetch 拿不到真实目标 URL。pullpush.io 存档 API 也不提供短码反查。

## 正确做法

1. **立即告诉用户无法直接访问该链接**。
2. **请用户提供帖子标题或完整 permalink**（如 `https://www.reddit.com/r/Gardyn/comments/1k7v07t/...`）。
3. **用 pullpush 拉取该 subreddit 全量/近期数据**，按标题关键词或时间段匹配，很可能覆盖该帖子内容。
4. **若无法确认是否覆盖**，在最终报告中标注：
   > "未包含用户提供的特定 share 链接原文；以下分析基于 r/Gardyn 同期数据推断。"

## 本会话案例

用户提供的 `https://www.reddit.com/r/Gardyn/s/nx2NRbY8I7` 经 pullpush 数据检索后，匹配到高赞帖子：

- 标题：*"I’m just mad and want to rant."*
- 链接：`https://www.reddit.com/r/Gardyn/comments/1k7v07t/...`
- 核心内容：$900 Gardyn 整机 + $400/yr Kelby 订阅，基础低水位提醒被 paywall。

最终该帖子被纳入分析并引用在用户原声页面中。
