# Security Policy（安全策略）

## 敏感数据处理约定

本项目脚本会接触**登录态 Cookie**（`get_cookies.py` / `login.py` 写入 `.env`）与抓取结果。约定如下：

- Cookie 等同登录态，仅存本机 `.env`，**禁止**提交到仓库、外传或写入日志
- `.env`、日志、抓取产物已由 `.gitignore` 覆盖；提交前请自查 `git status`
- 脚本不保存、不上传任何账号密码；登录在用户本机的真实浏览器中完成
- 如果脚本有 bug 导致 Cookie 被打印到日志/标准输出，请立即按下方渠道报告

## 报告漏洞

发现以下问题请**私密**报告（不要开公开 issue）：

1. 脚本泄露 Cookie / 账号信息到日志、文件或网络
2. 脚本被用于绕过平台风控、验证码或安全机制（本项目明确禁止此类用途，见 docs/compliance.md）
3. 仓库或 issue 中出现真实个人信息

报告渠道：在 GitHub 仓库创建 **Security Advisory**（Settings → Security → Advisories → New draft advisory），或通过仓库主页的维护者联系邮箱。

## 响应承诺

- 涉及真实 Cookie/个人信息泄露：24 小时内响应
- 一般安全问题：7 天内响应
- 修复后发布补丁版本并在 CHANGELOG 记录

## 安全使用提醒

- 背调仅限公开信息与合法用途；请遵守目标平台的服务条款与当地法律（见 [docs/compliance.md](docs/compliance.md)）
- 不要把你的 `.env` / Cookie 给任何人；`login.py` 输出路径默认在仓库 `envs/`（gitignore），也可用 `--env-dir` 指向自己的监控工具目录
