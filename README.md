# Executive Diligence（企业高管背调 Skill）

基于公开信息的系统化企业高管/企业家背调工作流：**基础信息 → 全网检索 → 社交监控（可选）→ 事件脉络 → 报告与台账**，配套多平台扫码登录获取 Cookie、公众号检索、负面台账（Excel）生成等工具脚本。

> 全程只用公开信息；事实 / 指控 / 传闻三级标注；同名他人明确区分；每条结论带信源。请阅读 [docs/compliance.md](docs/compliance.md) 后再使用。

## 特性

- **三种背调模式**：快速（检索+摘要）/ 标准（+负面台账 Excel）/ 深度（+社交监控+事件脉络），开始时可让用户选择
- **多平台登录获取 Cookie**：微博 / 小红书 / 抖音 / 知乎 / 视频号助手 / 公众号平台 / 微信网页版，扫码登录自动写入 `.env`（`scripts/login.py`）
- **公众号检索**：搜狗微信搜索工具，翻页 + 去重 + JSON 输出（`scripts/sogou_search.py`）
- **负面台账**：15 列格式 Excel 生成/追加，分组与优先级配色（`scripts/build_ledger.py`）
- **平台边界文档化**：各平台登录/Cookie/检索能力与限制实测结论见 [docs/platform-matrix.md](docs/platform-matrix.md)

## 快速开始

```bash
# 1. 依赖（Python 3.10+）
pip install -r requirements.txt
playwright install chromium

# 2. 登录平台获取 Cookie（交互选择平台，扫码登录）
python skill/scripts/login.py

# 3. 公众号检索（无需登录）
python skill/scripts/sogou_search.py --keyword "目标人物或公司" --pages 2 --output result.json

# 4. 负面台账生成
python skill/scripts/build_ledger.py entries.json 台账.xlsx
```

登录细节与无交互终端（`--signal` 信号模式）用法见 [skill/SKILL.md](skill/SKILL.md) 阶段 3。

## 背调流程

1. **执行前**：确认任务单（姓名/关联企业/同名区分线索）并选择模式（快速/标准/深度，可叠加 deep-research）
2. **阶段 1 基础信息**：工商登记、任职履历、股权结构（web 检索交叉验证）
3. **阶段 2 全网检索**：新闻、司法信用、负面关键词、公司与行业
4. **阶段 3 社交监控（可选）**：微博/小红书监控、公众号检索（需登录时用 `login.py`）
5. **阶段 4 事件脉络**：时间线 + 事实/指控/传闻分级
6. **阶段 5 产出**：背调报告（Markdown）+ 负面台账（Excel）

## 目录结构

```
├── skill/
│   ├── SKILL.md          # skill 指令文档（工作流定义）
│   ├── scripts/          # login / get_cookies / sogou_search / build_ledger
│   └── templates/        # report.md 报告模板
├── docs/                 # platform-matrix / compliance
├── examples/             # 脱敏示例输出
├── tests/                # 纯逻辑单元测试（无外部依赖，python 直接跑）
└── envs/                 # 本地 .env 输出目录（gitignore，不入库）
```

## 赞助与商业支持

核心功能**永久开源**（Apache-2.0），欢迎通过以下方式支持持续维护：

- **GitHub Sponsors**：https://github.com/sponsors/bocai-harry （点击仓库右上角 Sponsor 按钮亦可）
- 赞助 / 付费支持可获得的权益（规划中，欢迎通过 Issues 或仓库主页联系洽谈）：
  - 新平台 / 新渠道的优先适配
  - 平台接口变更的优先修复与技术支持
  - 企业版（规划）：批量背调、审计日志、团队协作、飞书深度集成、托管部署
- 商业合作 / 定制需求：GitHub Issues 或仓库主页联系邮箱

## 合规与许可

- 背调涉及个人信息，仅限**公开信息 + 合法用途**，风险自负，详见 [docs/compliance.md](docs/compliance.md)
- 本项目基于 **Apache-2.0** 开源，见 [LICENSE](LICENSE)；贡献见 [CONTRIBUTING.md](CONTRIBUTING.md)
- 贡献者需同时满足 **DCO**（提交签名）与 **CLA**（[CLA.md](CLA.md) 授权），确保贡献可用于本项目（含未来商业版本）
