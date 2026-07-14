# 在 Deck 附录中引用 reddit-community-research 技能

## 场景

用户要将 `reddit-community-research` 技能作为工作坊/演讲附录页列出，并给出下载/安装链接。该技能当前可能不是公开仓库，需要谨慎处理链接展示。

## 链接验证

在生成附录页前，必须验证链接可访问性：

```python
import urllib.request, json

for repo in ["USER/REPO"]:
    url = f"https://api.github.com/repos/{repo}"
    req = urllib.request.Request(url, headers={"User-Agent": "hermes-agent"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"{repo}: {data['html_url']} | private={data['private']} | archived={data['archived']}")
    except Exception as e:
        print(f"{repo}: NOT ACCESSIBLE - {e}")
```

## 附录页写法

### 如果仓库公开

直接给出 GitHub 链接和安装路径：

```html
<a href="https://github.com/USER/REPO" target="_blank">下载与安装</a>
<div class="install-note">安装：将仓库 clone 到 ~/.hermes/skills/research/REPO/</div>
```

### 如果仓库不公开（常见情况）

不要在附录页上放会 404 的链接。推荐写法：

- 按钮文字改为「查看安装源」或「获取方式」
- 说明：「该技能为社区/私有分发，若公开链接不可访问，请在 Hermes 中运行 `hermes skills search reddit` 或通过工作坊渠道获取。」
- 同时提供替代入口：如 `awesome-hermes-agent` 列表、或 `hermes-skills` 搜索指引

## 工作流程描述（用于附录页展示）

```
1. 确认目标：subreddit、关键词、时间范围、数据量
2. 获取数据：pullpush.io 或 Tavily 作为备选
3. 结构化：过滤噪音、分类痛点、提取情绪
4. 输出报告：痛点矩阵、需求优先级、真实原声引用
```

适用场景：竞品社区调研、用户需求验证、社交媒体聆听、Reddit 情报。

## 参考

- 本技能 SKILL.md 的 Phase 1-6 完整流程
- `tavily-reddit-fallback.md`：当 pullpush 不可用时用 Tavily 快速完成社区情报
- `demand-validation-template.md`：Reddit 需求验证关键词表
