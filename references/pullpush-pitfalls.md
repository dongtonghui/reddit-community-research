# pullpush.io API 已知陷阱与规避

> 本文件记录 pullpush.io API 在实际使用中的非文档化行为和陷阱。
> 最后更新: 2026-06-02

---

## 1. 时间基准陷阱

**问题**: pullpush 数据有显著延迟，最新存档可能只到数周/数月前。

**错误做法**:
```python
# ❌ 用当前系统时间计算 cutoff
three_months_ago = int((datetime.now() - timedelta(days=90)).timestamp())
```

**正确做法**:
```python
# ✅ 先采样获取数据最新时间，以此为基准
resp = requests.get(
    "https://api.pullpush.io/reddit/search/submission/",
    params={"subreddit": "Gardyn", "size": 10, "sort": "desc"},
    headers=HEADERS, timeout=30
)
latest_ts = max(p["created_utc"] for p in resp.json()["data"])
cutoff = latest_ts - 90 * 86400  # 从数据最新时间往回推
```

**示例**: 2026-06-02 抓取时，pullpush 最新数据只到 2025-05-18。

---

## 2. 评论 API 参数限制

**问题**: `link_id` 参数在 `/reddit/search/comment/` 端点返回 400。

**错误做法**:
```python
# ❌ link_id 参数不受支持
resp = requests.get(
    "https://api.pullpush.io/reddit/search/comment/",
    params={"link_id": "t3_xxx", "size": 100},  # 返回 400
)
```

**正确做法**:
```python
# ✅ 用 subreddit 参数全量获取，本地分组
resp = requests.get(
    "https://api.pullpush.io/reddit/search/comment/",
    params={"subreddit": "Gardyn", "size": 100, "sort": "desc"},
)
comments = resp.json()["data"]

# 本地按帖子分组
by_post = {}
for c in comments:
    lid = c.get("link_id", "").replace("t3_", "")
    by_post.setdefault(lid, []).append(c)
```

---

## 3. 分页参数行为

| 参数 | 行为 | 注意 |
|------|------|------|
| `sort=desc` | 按时间倒序（最新在前） | 默认行为 |
| `before=<ts>` | 获取时间戳 **小于** ts 的数据 | 用于向后翻页（获取更旧的数据） |
| `after=<ts>` | 获取时间戳 **大于** ts 的数据 | 用于向前翻页（获取更新的数据），但数据延迟时不生效 |

**分页模板**:
```python
all_posts = []
before_ts = None
while True:
    params = {"subreddit": "xxx", "size": 100, "sort": "desc"}
    if before_ts:
        params["before"] = before_ts
    resp = requests.get("...", params=params)
    posts = resp.json()["data"]
    if not posts:
        break
    all_posts.extend(posts)
    before_ts = min(p["created_utc"] for p in posts)
    time.sleep(0.5)
```

---

## 4. 关键词匹配噪音

**问题**: 短关键词如 "plan" 会匹配 "plant"，"member" 会匹配 "remember"。

**解决方案**:
```python
# 方案1: 词边界检查
def word_in_text(word, text):
    return f" {word} " in f" {text} "

# 方案2: 正则词边界
import re
pattern = re.compile(r'\bplan\b', re.IGNORECASE)

# 方案3: 标题优先匹配（标题比正文更精确）
# 对于 question 类帖子，优先检查 title
```

---

## 5. 数据去重

pullpush 可能返回重复数据，建议在分析前按 `id` 去重：

```python
seen = set()
unique_posts = []
for p in posts:
    if p["id"] not in seen:
        seen.add(p["id"])
        unique_posts.append(p)
```
