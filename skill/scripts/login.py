#!/usr/bin/env python
r"""多平台登录获取 Cookie 的交互入口（skill 用）。

包装 scripts/get_cookies.py：列出平台让你选，然后跑对应平台的扫码登录，
把 Cookie 写入对应监控工具的 .env。在真实终端里运行；无交互终端（自动化/CI）
请加 --signal 用信号文件触发。

输出路径优先级（从高到低）：
  1. --output 显式指定；
  2. --env-dir / 环境变量 DILIGENCE_ENV_DIR 指定的基础目录（输出到 <dir>/<平台>/<工具>.env，如 D:\weibo-monitor\.env）；
  3. 默认仓库内 envs/ 目录（已 gitignore，不入库）。

用法：
  python login.py                          # 交互选择平台（推荐）
  python login.py --platform xhs           # 直接指定平台，跳过菜单
  python login.py --list                   # 只列出平台与默认输出路径
  python login.py --signal D:\flag.txt     # 信号模式（无交互终端）
  python login.py --timeout-minutes 15     # 自定义最长等待分钟数
  python login.py --env-dir D:\            # 输出到 D:\weibo-monitor\.env 等既有位置
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent  # <repo>/skill/scripts -> <repo>
GET_COOKIES = HERE / "get_cookies.py"

# 平台 -> 相对输出路径（相对 --env-dir / 默认 envs/ 目录；可用 --output 完全覆盖）
DEFAULT_OUTPUTS = {
    "weibo": "weibo-monitor/.env",
    "xhs": "xhs-monitor/.env",
    "douyin": "douyin-monitor/.env",
    "zhihu": "zhihu-monitor/.env",
    "channels": "channels-monitor/.env",
    "mp": "mp-monitor/.env",
    "wxweb": "wechat-web/.env",
}

PLATFORM_NAMES = {
    "weibo": "微博",
    "xhs": "小红书",
    "douyin": "抖音",
    "zhihu": "知乎",
    "channels": "微信视频号（视频号助手）",
    "mp": "微信公众号（后台）",
    "wxweb": "微信网页版（视频号/搜一搜；部分微信号被腾讯限制无法登录）",
}


def resolve_output(platform, args):
    if args.output:
        return args.output
    base = args.env_dir or os.environ.get("DILIGENCE_ENV_DIR")
    if base:
        return str(Path(base) / DEFAULT_OUTPUTS[platform])
    return str(REPO_ROOT / "envs" / DEFAULT_OUTPUTS[platform])


def main():
    ap = argparse.ArgumentParser(description="多平台登录获取 Cookie（包装 get_cookies.py）")
    ap.add_argument("--platform", choices=list(DEFAULT_OUTPUTS), help="直接指定平台，跳过菜单")
    ap.add_argument("--output", help=".env 输出路径（最高优先级）")
    ap.add_argument("--env-dir", help="输出基础目录（也读环境变量 DILIGENCE_ENV_DIR）；默认仓库内 envs/")
    ap.add_argument("--signal", help="信号文件路径（无交互终端时用）")
    ap.add_argument("--timeout-minutes", type=int, help="最长等待分钟数（默认 10）")
    ap.add_argument("--list", action="store_true", help="只列出平台与默认输出路径")
    args = ap.parse_args()

    if args.list:
        print("平台 → 输出路径（按当前配置解析）：")
        for k, name in PLATFORM_NAMES.items():
            print(f"  {k:<10} {name}  ->  {resolve_output(k, args)}")
        return 0

    platform = args.platform
    if not platform:
        keys = list(DEFAULT_OUTPUTS)
        print("选择要登录的平台：")
        for i, k in enumerate(keys, 1):
            print(f"  {i}. {PLATFORM_NAMES[k]}")
        try:
            choice = input("输入序号（回车默认 1 微博）: ").strip()
        except EOFError:
            choice = "1"
        idx = int(choice) if choice.isdigit() and 1 <= int(choice) <= len(keys) else 1
        platform = keys[idx - 1]

    cmd = [sys.executable, str(GET_COOKIES), platform]
    cmd += ["--output", resolve_output(platform, args)]
    if args.signal:
        cmd += ["--signal", args.signal]
    if args.timeout_minutes:
        cmd += ["--timeout-minutes", str(args.timeout_minutes)]

    print(f">>> 平台: {PLATFORM_NAMES[platform]}（{platform}）", flush=True)
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
