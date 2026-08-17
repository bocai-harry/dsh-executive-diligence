# Changelog

本项目采用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 风格，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 变更

- 澄清定位：本项目是 DSH **Skill（技能）** 而非 DSH 插件；README 与 GitHub 仓库描述同步更新，移除 `dsh-plugin` topic

## [0.2.0] - 2026-08-17

### 变更

- 仓库更名为 `dsh-executive-diligence`，README / 描述突出 DeepSeek Harness（DSH）技能插件身份（由 DSH 编写并在其环境运行），并链接 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
- topics 增加 `deepseek-harness` / `dsh` / `plugin`
- SKILL.md 前注新增 `version` 字段，与 `pyproject.toml` 版本号对齐（0.2.0）

### 新增

- **调研前说明（成本与预期管理）**：开始检索前向用户说明——大企业高管/多企业背景下采用分层聚焦检索（先核心信息，按需扩展）；权限控制/反爬限流/登录态失效报错快速降级（同一来源连续失败 ≥2 次即放弃重试，换渠道或记为信息缺口，标注「未能核实」）；新增精简/标准/深度三档预算表（每关键词检索次数、每维度记录上限、web_fetch 上限），默认「标准」档
- **负面事件平台扩散与脉络分析（可选拓展）**：先检索主流媒体负面报道 → 同事件聚类并按集中度（篇数×时间密集度×严重性）取 Top 事件 → 定向扩散检索（微博/小红书/知乎/抖音/公众号/贴吧/豆瓣/脉脉/裁判文书网/信用公示，每平台 1 次）→ 事件×平台扩散矩阵与传播路径 → 定向事件报告 `<姓名>_<事件>_事件报告_<日期>.md`
- deep-research 拓展数量上限：子代理 ≤6 路、每路检索 ≤3 轮、返回证据 ≤5 条、补缺迭代 ≤1 轮
- 贡献者许可协议 [CLA.md](CLA.md)：贡献者在 DCO 之外签署 CLA，将贡献的版权/专利授权给维护者（含未来商业版本）
- `CONTRIBUTING.md`：贡献机制升级为 DCO + CLA 双重要求
- `README.md`：新增「赞助与商业支持」区块；`.github/FUNDING.yml` 启用 GitHub Sponsors 按钮（需在账号开启 Sponsors）

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
