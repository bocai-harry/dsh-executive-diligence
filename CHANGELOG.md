# Changelog

本项目采用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 风格，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-08-17

### 新增（初始开源版）

- Skill 工作流：快速 / 标准 / 深度三种背调模式，开始时与用户确认；基础信息、全网检索（含 deep-research 可选拓展）、社交监控、事件脉络、报告与台账五阶段
- `scripts/login.py`：多平台登录交互入口（微博/小红书/抖音/知乎/视频号助手/公众号平台/微信网页版），输出路径三级解析（`--output` → `DILIGENCE_ENV_DIR`/`--env-dir` → 仓库 `envs/`）
- `scripts/get_cookies.py`：扫码登录获取 Cookie 写入 `.env`；交互终端回车 / 关键 Cookie 自动检测 / `--signal` 信号文件三种触发；stdin 非交互时自动降级不误抓；`--timeout-minutes` 可配
- `scripts/sogou_search.py`：搜狗微信搜索公众号文章/主页检索，翻页 + 去重 + 日期解析（yyyy-m-d / m月d日 / timeConvert epoch）+ 验证码检测 + JSON 输出
- `scripts/build_ledger.py`：负面内容台账（15 列 Excel）生成/追加，分组与优先级配色
- 文档：`docs/platform-matrix.md`（平台适配矩阵，含匿名 Cookie 误触发、微信网页版账号限制、视频号无网页检索等实测边界）、`docs/compliance.md`（合规与免责）
- 测试：`tests/test_parsers.py` 纯逻辑单元测试（无外部依赖）
- 许可：Apache-2.0

### 已知边界（实测结论，详见 docs/platform-matrix.md）

- 微信视频号公共内容**无网页检索渠道**：视频号助手为管理后台无公开搜索；微信网页版（wxweb）部分账号被腾讯限制登录；关键词检索只能在微信 App/桌面客户端内手动进行
- 搜狗微信搜索**仅索引公众号内容**，不含视频号
- 小红书未登录也下发匿名 `web_session`、知乎未登录也下发匿名 `z_c0`，关键 Cookie 自动检测可能提前触发——需要真正登录时用 `--signal`
