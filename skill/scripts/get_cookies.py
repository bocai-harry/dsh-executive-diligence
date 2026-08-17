#!/usr/bin/env python
r"""定向监测平台 Cookie 获取脚本（Playwright 浏览器登录，小白友好）。

打开一个真实浏览器窗口，你在窗口里自己登录目标平台；登录完成后回到命令行按回车，
脚本自动抓取登录态 Cookie 并写入监控工具的 .env —— 全程无需手动复制粘贴 Cookie，
你的账号密码也不会经过这个脚本。

支持平台（platform 参数）：
  weibo         微博                 → WEIBO_COOKIE          （关键字段 SUB）
  xhs           小红书               → XHS_COOKIE            （关键字段 web_session）
  douyin        抖音                 → DOUYIN_COOKIE         （关键字段 sessionid）
  zhihu         知乎                 → ZHIHU_COOKIE          （关键字段 z_c0）
  channels      微信视频号（视频号助手）→ WECHAT_CHANNELS_COOKIE （扫码登录，回车确认）
  mp            微信公众号（后台）     → WECHAT_MP_COOKIE     （扫码登录，关键字段 slave_sid）
  wxweb         微信网页版             → WECHAT_WEB_COOKIE    （扫码登录；含视频号/搜一搜的完整网页客户端）

用法：
  python get_cookies.py <platform> [--output D:\path\.env] [--signal D:\path\flag] [--timeout-minutes N]
  --output           可选：写入目标 .env 文件的对应变量；不提供则只打印 Cookie 串。
  --signal <文件>     可选：信号模式——不等待回车，改为等待该文件出现（外部确认登录后创建该文件）即抓取。
                     用于脚本在无交互终端（自动化/CI）里运行，或平台下发匿名同名关键 Cookie（如小红书 web_session）
                     时确保等真正的登录。调用方负责在运行前删除旧信号文件。
  --timeout-minutes  可选：最长等待分钟数，默认 10。

触发方式（满足其一即抓取）：
  1) stdin 是交互终端（TTY）：登录后在此窗口按回车；
  2) 检测到平台关键 Cookie（SUB / web_session / sessionid / z_c0 / slave_sid）：
     ⚠️ 部分平台未登录也会下发同名 Cookie（实测：小红书 web_session、知乎 z_c0），可能误触发；
     要确保等到真正登录，请用 --signal；
  3) 指定了 --signal：该文件出现即抓取（信号模式下不做关键 Cookie 自动检测，避免误触发）。

依赖：python + playwright（pip install playwright && playwright install chromium）
"""
import argparse
import sys
import threading
import time
from pathlib import Path

PLATFORMS = {
    "weibo": {
        "url": "https://weibo.com",
        "hint": "请在打开的浏览器窗口里登录微博（扫码或账密均可）。登录成功后回到此窗口按回车。",
        "key_cookie": "SUB",
        "env_var": "WEIBO_COOKIE",
        "domain_marker": "weibo",
    },
    "xhs": {
        "url": "https://www.xiaohongshu.com",
        "hint": "请在打开的浏览器窗口里登录小红书。登录成功后回到此窗口按回车。",
        "key_cookie": "web_session",
        "env_var": "XHS_COOKIE",
        "domain_marker": "xiaohongshu",
    },
    "douyin": {
        "url": "https://www.douyin.com",
        "hint": "请在打开的浏览器窗口里登录抖音（扫码或账密）。登录成功后回到此窗口按回车。",
        "key_cookie": "sessionid",
        "env_var": "DOUYIN_COOKIE",
        "domain_marker": "douyin",
    },
    "zhihu": {
        "url": "https://www.zhihu.com",
        "hint": "请在打开的浏览器窗口里登录知乎（账密或扫码）。登录成功后回到此窗口按回车。",
        "key_cookie": "z_c0",
        "env_var": "ZHIHU_COOKIE",
        "domain_marker": "zhihu",
    },
    "channels": {
        "url": "https://channels.weixin.qq.com",
        "hint": "请在打开的浏览器窗口里用微信扫码登录「微信视频号助手」。手机确认后回到此窗口按回车。",
        "key_cookie": "",  # 扫码登录，依赖回车/信号文件确认
        "env_var": "WECHAT_CHANNELS_COOKIE",
        "domain_marker": "weixin.qq.com",
    },
    "mp": {
        "url": "https://mp.weixin.qq.com",
        "hint": "请在打开的浏览器窗口里用微信扫码登录「微信公众号平台」。手机确认后回到此窗口按回车。",
        "key_cookie": "slave_sid",
        "env_var": "WECHAT_MP_COOKIE",
        "domain_marker": "weixin.qq.com",
    },
    "wxweb": {
        "url": "https://web.wechat.com",
        "hint": "请在浏览器窗口用微信扫码登录微信网页版。手机确认后等待自动完成（无关键 Cookie，建议配 --signal）。",
        "key_cookie": "",
        "env_var": "WECHAT_WEB_COOKIE",
        "domain_marker": "wechat.com",
    },
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
DEFAULT_MAX_WAIT_MINUTES = 10


def collect_cookies(platform, signal_path, max_wait_minutes):
    """打开浏览器让用户登录，返回该平台域名的 Cookie 列表。"""
    cfg = PLATFORMS[platform]
    from playwright.sync_api import sync_playwright

    tty = sys.stdin.isatty()
    if signal_path:
        print(f">>> 运行模式：信号模式（等待 {signal_path} 出现；不做关键 Cookie 自动检测）")
    elif tty:
        print(">>> 运行模式：交互模式（登录后在此窗口按回车）")
    else:
        key_cookie = cfg.get("key_cookie")
        if key_cookie:
            print(f">>> 运行模式：自动检测模式（stdin 非交互，不等待回车；等待关键 Cookie {key_cookie} 出现）")
        else:
            print(">>> 运行模式：本平台无关键 Cookie 且 stdin 非交互，无法按回车——请用 --signal 指定信号文件")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="zh-CN")
        page = ctx.new_page()
        page.goto(cfg["url"], wait_until="domcontentloaded", timeout=60000)
        print(f"\n>>> {cfg['hint']}")
        print(f">>> 最多等待 {max_wait_minutes} 分钟。")

        enter_done = threading.Event()
        stdin_closed = False
        if not signal_path:
            def wait_enter():
                nonlocal stdin_closed
                try:
                    input()
                except EOFError:
                    # stdin 关闭（无交互终端/自动化环境）时不再等待回车；
                    # 但 isatty() 在某些环境会误报 True，所以必须在这里降级。
                    stdin_closed = True
                    print(">>> 提示：stdin 无输入（非交互），不会等待回车；改为等待关键 Cookie 或信号文件。")
                    return
                enter_done.set()

            threading.Thread(target=wait_enter, daemon=True).start()

        deadline = time.time() + max_wait_minutes * 60
        key_cookie = cfg.get("key_cookie")
        last_report = 0.0
        while time.time() < deadline:
            if enter_done.is_set():
                print("已按回车，开始抓取 Cookie…")
                break
            if signal_path and Path(signal_path).exists():
                print(f"信号文件已出现（{signal_path}），开始抓取 Cookie…")
                break
            if not signal_path and key_cookie and any(
                c["name"] == key_cookie and c.get("value") for c in ctx.cookies()
            ):
                print(f"已检测到登录态（{key_cookie}），开始抓取 Cookie…")
                break
            now = time.time()
            if now - last_report >= 10:
                last_report = now
                n = len(ctx.cookies())
                if signal_path:
                    cond = "信号文件"
                elif key_cookie:
                    cond = f"关键 Cookie {key_cookie}"
                else:
                    cond = "回车"
                print(f"等待登录中… 当前 {n} 个 Cookie，触发条件：{cond}，剩余 {int(deadline - now)} 秒")
            time.sleep(2)
        else:
            print("等待超时，按当前 Cookie 处理（可能未登录）。")

        cookies = ctx.cookies()
        browser.close()
        return cookies


def format_cookie_string(cookies, platform):
    """只保留目标平台域名的 cookie，拼成 'k=v; k2=v2' 串。"""
    marker = PLATFORMS[platform]["domain_marker"]
    parts = [f"{c['name']}={c['value']}" for c in cookies if marker in (c.get("domain") or "")]
    return "; ".join(parts)


def write_env_var(env_path, var, value):
    """把 var=value 写入/更新 .env（值为字符串，允许含 ; = % 等）。"""
    p = Path(env_path)
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    out, replaced = [], False
    for line in lines:
        if line.strip().startswith(f"{var}="):
            out.append(f'{var}="{value}"')
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(f'{var}="{value}"')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    # stdout 重定向到文件/管道时逐行输出，便于外部实时观察进度（如 --signal 模式）
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="用浏览器登录获取平台 Cookie 并写入 .env")
    ap.add_argument("platform", choices=list(PLATFORMS), help="目标平台：" + " / ".join(PLATFORMS))
    ap.add_argument("--output", help="写入的目标 .env 路径（如 D:\\weibo-monitor\\.env）；不填则只打印")
    ap.add_argument("--signal", help="信号文件路径：文件出现即抓取（无交互终端 / 防匿名关键 Cookie 误触发时用）")
    ap.add_argument("--timeout-minutes", type=int, default=DEFAULT_MAX_WAIT_MINUTES, help="最长等待分钟数，默认 10")
    args = ap.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("缺少 playwright：请先执行  pip install playwright && playwright install chromium")
        sys.exit(2)

    cookies = collect_cookies(args.platform, args.signal, args.timeout_minutes)
    cookie_str = format_cookie_string(cookies, args.platform)
    if not cookie_str:
        print("\n未抓到该平台的 Cookie，请确认已在浏览器里登录。")
        sys.exit(1)

    var = PLATFORMS[args.platform]["env_var"]
    if args.output:
        write_env_var(args.output, var, cookie_str)
        print(f"\n已写入 {args.output} 的 {var}（长度 {len(cookie_str)}）")
    else:
        print(f"\n{var}=")
        print(cookie_str)
    print("\n提示：Cookie 等同登录态，仅保存于本机 .env，请勿外传；失效后重新运行本脚本即可。")


if __name__ == "__main__":
    main()
