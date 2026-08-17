# 贡献指南（Contributing）

欢迎提交 Issue 与 Pull Request。本项目小且务实，规则尽量少，但以下几条请务必遵守。

## 敏感信息红线

- **绝不提交** `.env`、Cookie、Webhook、账号信息、日志与抓取产物（`.gitignore` 已覆盖，提交前自查）
- 涉及个人可识别信息的 issue/PR 请脱敏（目标人物改占位符）
- 发现泄露请按 [SECURITY.md](SECURITY.md) 处理

## 代码与行为

- Python 脚本：Python 3.10+，`ruff` 默认规则（`line-length=120`），提交前跑：
  ```bash
  pip install ruff
  ruff check skill/scripts tests
  python tests/test_parsers.py
  ```
- 新增纯逻辑函数尽量补进 `tests/test_parsers.py`（无外部依赖，直接 `python` 可跑）
- 涉及真实浏览器/登录的脚本（`get_cookies.py` 等）不要求自动化测试，但**必须注明平台边界与人工验证步骤**（参照 `docs/platform-matrix.md`）

## 新增平台（如微博/小红书/抖音等）

1. 在 `get_cookies.py` 的 `PLATFORMS` 加条目：URL、登录提示、关键 Cookie、`.env` 变量名、域名过滤标记
2. 在 `login.py` 的 `DEFAULT_OUTPUTS` / `PLATFORM_NAMES` 加映射
3. 实测扫码登录 + 抓取，并把结论更新到 `docs/platform-matrix.md`（含匿名 Cookie 误触发等坑）
4. 更新 `SKILL.md` 阶段 3 与 README

## DCO（Developer Certificate of Origin）

本项目贡献采用 DCO 机制（与 Apache 系一致）：每条提交须附带签名，表明你有权贡献且同意贡献可用于本项目（含未来商业版本）：

```bash
git commit -s -m "feat: ..."
# 提交信息末尾会自动带上：Signed-off-by: 你的名字 <邮箱>
```

未签名的提交会被拒绝合入。完整 DCO 文本见 https://developercertificate.org/ 。

## 分支与提交

- 小改动直接提交到主分支（当前为单维护者起步阶段）；较大的新功能建议先开 Issue 讨论
- 提交信息用中文或英文均可，清晰描述「做了什么 / 为什么」

## 平台反爬与合规提醒

- 各平台有反爬与风控：保持低频、遵守平台条款；触发验证码时降低频率
- 抓取仅限公开内容与本人登录态；不逆向签名、不绕过验证、不伪造请求
- 合规边界详见 [docs/compliance.md](docs/compliance.md)
