#!/usr/bin/env python
r"""搜狗微信搜索检索工具（公众号文章/公众号主页，skill 用）。

检索微信公众号内容并输出 JSON。**不包含微信视频号**——视频号没有公开网页检索
接口（搜狗微信搜索页面标注「以下内容来自微信公众平台」），视频号内容只能在
微信 App/桌面客户端内手动检索。

用法：
  python sogou_search.py --keyword 问界M9 --type 2 --pages 2 --output result.json
  python sogou_search.py --keyword 某公司名 --type 1            # 公众号主页
  python sogou_search.py --keyword 某高管 --pages 3 --show      # 显示浏览器窗口

参数：
  --keyword  检索词（必填）
  --type     2=文章（默认），1=公众号主页
  --pages    翻页数，1-10，默认 1（每页 10 条，去重输出）
  --output   结果 JSON 路径（可选，不填只打印到控制台）
  --show     显示浏览器窗口（默认无头）

注意：
  - 搜狗有反爬：连续高频检索可能触发验证码（结果中 captcha=true），降低频率或稍后重试；
  - href 为搜狗加密跳转链接（weixin.sogou.com/link?url=...），需在浏览器打开后跳到公众号原文。
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
BASE = "https://weixin.sogou.com/weixin"
MAX_PAGES = 10

EXTRACT_JS = """() => {
    const pick = (root, sel) => {
        const n = root.querySelector(sel);
        return n ? n.textContent.trim().replace(/\\s+/g, ' ') : '';
    };
    let nodes = Array.from(document.querySelectorAll('.news-list > li'));
    if (nodes.length === 0) {
        // 兜底：按 sogou_vr 容器 id 抓（公众号主页等布局）
        nodes = Array.from(document.querySelectorAll('li[id*=sogou_vr_]'));
    }
    return nodes.map(li => {
        const a = li.querySelector('h3 a') || li.querySelector('a[href*="/link?url="]');
        return {
            title: a ? a.textContent.trim().replace(/\\s+/g, ' ') : '',
            href: a ? a.href : '',
            summary: pick(li, '.txt-info'),
            account: pick(li, '.s-p .all-time-y2'),
            date_text: pick(li, '.s-p .s2')
        };
    }).filter(x => x.title);
}"""


def parse_date(text):
    """从 s2 文本提取日期：剥掉 document.write 脚本；匹配 yyyy-m-d / m月d日 / timeConvert epoch。"""
    epoch = re.search(r"timeConvert\('(\d{10})'\)", text)
    if epoch:
        return datetime.fromtimestamp(int(epoch.group(1))).strftime("%Y-%m-%d")
    text = re.sub(r"document\.write\([^)]*\)", "", text)
    m = re.search(r"(\d{4})[-年/](\d{1,2})[-月/](\d{1,2})", text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m2 = re.search(r"(\d{1,2})月(\d{1,2})日", text)
    if m2:
        return f"{datetime.now().year}-{int(m2.group(1)):02d}-{int(m2.group(2)):02d}"
    return ""


def main():
    ap = argparse.ArgumentParser(description="搜狗微信搜索（公众号文章/公众号主页）")
    ap.add_argument("--keyword", required=True, help="检索词（必填）")
    ap.add_argument("--type", choices=["1", "2"], default="2", help="2=文章（默认），1=公众号主页")
    ap.add_argument("--pages", type=int, default=1, help=f"翻页数 1-{MAX_PAGES}，默认 1")
    ap.add_argument("--output", help="结果 JSON 路径（不填只打印）")
    ap.add_argument("--show", action="store_true", help="显示浏览器窗口（默认无头）")
    args = ap.parse_args()
    pages = max(1, min(args.pages, MAX_PAGES))

    items, captcha = [], False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.show)
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1360, "height": 900}, locale="zh-CN")
        page = ctx.new_page()
        for n in range(1, pages + 1):
            url = f"{BASE}?type={args.type}&query={quote(args.keyword)}&page={n}&ie=utf8"
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3500)
            body = " ".join(page.inner_text("body").split())
            if "验证码" in body or "请输入验证码" in body:
                captcha = True
                print(f"[page {n}] 触发验证码，停止翻页。", flush=True)
                break
            cards = page.evaluate(EXTRACT_JS)
            print(f"[page {n}] 卡片 {len(cards)} 条", flush=True)
            for c in cards:
                c["date"] = parse_date(c.pop("date_text", ""))
                items.append(c)
            if n < pages and not captcha:
                time.sleep(2)
        browser.close()

    seen, dedup = set(), []
    for it in items:
        if it["title"] not in seen:
            seen.add(it["title"])
            dedup.append(it)

    result = {
        "keyword": args.keyword,
        "type": args.type,
        "pages_requested": pages,
        "captcha": captcha,
        "total": len(dedup),
        "items": dedup,
        "note": "仅索引微信公众号内容，不含视频号；href 为搜狗加密跳转链接",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    for i, it in enumerate(dedup, 1):
        print(f"[{i}] {it['title']} | {it['account']} | {it['date']}")
        print(f"    {it['summary'][:50]} | {it['href'][:80]}")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已保存: {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
