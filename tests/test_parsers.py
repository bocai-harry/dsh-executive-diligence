"""纯逻辑单元测试：不依赖网络/浏览器，直接 `python tests/test_parsers.py` 运行（CI 亦如此）。"""
import datetime
import json
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skill" / "scripts"))

import build_ledger  # noqa: E402
import get_cookies  # noqa: E402
import sogou_search  # noqa: E402

PASS = 0
FAIL = []


def check(name, cond, detail=""):
    global PASS
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL {name}  {detail}")


def test_sogou_parse_date():
    print("[sogou_search.parse_date]")
    check("yyyy-m-d", sogou_search.parse_date("2026-2-23") == "2026-02-23")
    check("yyyy年m月d日", sogou_search.parse_date("2026年2月23日") == "2026-02-23")
    check("m月d日(当年)", sogou_search.parse_date("2月23日") == f"{datetime.date.today().year}-02-23")
    check(
        "timeConvert epoch",
        sogou_search.parse_date("document.write(timeConvert('1786883027'))") == "2026-08-16",
    )
    check("剥掉 document.write", "document.write(" not in sogou_search.parse_date("x document.write(timeConvert('1'))"))
    check("空串", sogou_search.parse_date("") == "")
    check("无日期文本", sogou_search.parse_date("一些没有日期的文本") == "")


def test_get_cookies_format():
    print("[get_cookies.format_cookie_string]")
    cookies = [
        {"name": "SUB", "value": "abc", "domain": ".weibo.com"},
        {"name": "x", "value": "1", "domain": ".weibo.cn"},
        {"name": "other", "value": "2", "domain": ".example.com"},
    ]
    s = get_cookies.format_cookie_string(cookies, "weibo")
    check("按域名过滤并拼接", s == "SUB=abc; x=1", repr(s))


def test_build_ledger():
    print("[build_ledger.load_entries]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "entries.json"
        data = [{"分组": "A 建议处置", "平台/账号": "微博·@x"}, {"分组": "B 不建议投诉"}]
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        rows = build_ledger.load_entries(str(p))
        check("按 HEADERS 取字段", rows[0][0] == "A 建议处置" and rows[1][0] == "B 不建议投诉", repr(rows))
        p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
        rows2 = build_ledger.load_entries(str(p))
        check("BOM 容忍", rows2[0][0] == "A 建议处置", repr(rows2))


def main():
    test_sogou_parse_date()
    test_get_cookies_format()
    test_build_ledger()
    print(f"\n通过 {PASS} 项，失败 {len(FAIL)} 项")
    if FAIL:
        print("失败项:", FAIL)
        sys.exit(1)


if __name__ == "__main__":
    main()
