# 示例（脱敏）

本目录存放**脱敏**的示例输出，仅用于展示工具输出格式，不含真实个人可识别信息。

## sogou_sample.json

`scripts/sogou_search.py` 的输出示例（已脱敏、截断）：

```json
{
  "keyword": "示例关键词",
  "type": "2",
  "pages_requested": 1,
  "captcha": false,
  "total": 3,
  "items": [
    {
      "title": "示例文章标题一",
      "account": "示例公众号",
      "date": "2026-08-01",
      "summary": "示例摘要……",
      "href": "https://weixin.sogou.com/link?url=..."
    }
  ],
  "note": "仅索引微信公众号内容，不含视频号；href 为搜狗加密跳转链接",
  "generated_at": "2026-08-17T00:00:00"
}
```

## 真实输出参考

- 搜狗检索：`python skill/scripts/sogou_search.py --keyword "关键词" --pages 2 --output result.json`
- 小红书搜索（浏览器注入 Cookie）：见 `docs/platform-matrix.md`「小红书网页搜索」行
- 负面台账：`python skill/scripts/build_ledger.py entries.json 台账.xlsx`
