# AI 生成说明

本项目（**cfdialog**）是一个单文件、零依赖、跨平台的 Python CLI 文件对话框库。在 v0.1.0 到 v0.3.0 的迭代过程中，大量使用了大型语言模型（LLM）辅助生成代码、文档与测试。

本说明遵循 [AI 开发规范](https://github.com/styisme/ai-development-guidelines)，透明地界定 AI 与人类在项目中的实际贡献比例与责任边界。

> 相关文档：[README](../README.md) | [CHANGELOG](../CHANGELOG.md) | [贡献指南](../CONTRIBUTING.md) | [开发约束](DEVELOPMENT_CONSTRAINTS.md)。

---

## 🤖 AI 深度参与的部分

在 v0.1.0 到 v0.3.0 的迭代中，AI 承担了极大规模的“体力活”与“高危操作”：

- **单文件架构重构**：
  - 把原本分散的模块整合进 `cfdialog.py`，用注释大分隔线切成 16 个有序区块，依赖方向单向。
  - 用 `__all__` + 下划线前缀约定公开/私有边界。
- **CLI 浏览器引擎**：
  - `_browse()` 主循环、`_render_browse()` 固定 72 列渲染、`_list_dir()` 枚举 + 扩展名过滤。
  - `_browse_partitions()` 分区选择器（Windows 盘符 + 无盘符卷）。
- **i18n 系统**：
  - 内置 `zh_CN` / `en`，外置 `lg/*.txt` 按需加载。
  - 语言代码归一化（`zh-Hans` → `zh_CN`、`jp` → `ja`、`kr` → `ko`）。
  - 优先级链：`ts.txt force_language` > 单次 `lang=` > `set_language()` > `detect_language()` > `en`。
- **文件管理器**：
  - 只读 / 读写双模式；Windows 用 `GetFileAttributesW` / `SetFileAttributesW` 切换真实只读/隐藏位。
  - 剪贴板 + 粘贴、重命名、属性编辑。
- **自动提权**：
  - Windows UAC（`ShellExecuteW("runas")`）、Android root（`su -c`）、Linux/macOS（`sudo` → `su`）。
  - `_maybe_elevate()` 只问一次，`relaunched` 时父进程立即 `sys.exit(0)`。
- **测试与 CI**：
  - `tools/demo.py`（1500+ 行）：自动测试 + 手动测试 + 语言菜单 + 分区查看器。
  - `tests/test_smoke.py`：22 条 unittest 门禁。
  - `.github/workflows/ci.yml`：syntax × 6 Python 版本、test × 3 OS × 2 版本、demo-langs、gen_docs、demo-auto。
- **文档生成**：
  - `tools/gen_docs.py`：生成 README / DEVELOPMENT / 开发文档。
  - `tools/gen_lang_packs.py`：批量生成 6 个语言包。
  - `tools/make_custom_lang.py`：交互式单语言包制作器。

---

## 🧑‍💻 人类参与的部分

作为项目主导者，人类的职责是“提出痛点、把控方向、验证结果、抓虫”：

- **极端需求提出**：
  - “要一个单文件、零依赖的 CLI 文件对话框，能跑在 Termux / Pydroid / SSH 里。”
  - “语言包不能编译进去，用户要能自己加。”
  - “Windows 的无盘符卷也要能选。”
  - “Android 上 su 提权会丢终端，得能关掉。”
- **真机验证**：
  - 在 Android（Termux / Pydroid 3）上跑 `python cfdialog.py`、`tools/demo.py --list-langs`。
  - 在 Windows 上验证无盘符卷列举（`list_partitions()`）。
  - 在 Linux 上验证 `sudo` / `su` 提权分支。
- **Bug 定位与拦截**：
  - 发现 `_normalize_lang_code("ar")` 在无 `lg/ar.txt` 时返回 `None`，导致 `demo.py` T02 必失败 → 补 `lg/ar.txt` 占位包。
  - 发现 `gen_docs.py` 默认写到 CWD，在 `tools/` 下运行会污染目录 → patch 成默认写到仓库根。
  - 发现整理脚本把临时文件误复制进 `tools/` → 加 `temp_*.py` 清理。
- **CI 架构决策**：
  - `demo --auto` 因为已知 `ar` 失败，先做 informational（`continue-on-error: true`），补完 `ar` 后升级为真门禁。
  - `syntax` job 覆盖 Python 3.8–3.13，避免 `from __future__ import annotations` 等语法在新旧版本上行为不一致。
- **语言包审校**：
  - 6 个外部语言包（zh_TW/ja/ko/ru/fr/es）的关键词条人工校对。
  - `ar` 占位包明确标注“仅 `prompt_*` 为阿拉伯语”。

---

## ⚠️ 风险提示

由于大量核心代码与测试为 AI 辅助生成，请注意以下风险：

1. **单文件架构的副作用**：`cfdialog.py` 约 1900 行，所有模块都在一个文件里。修改任意区块都可能影响其他区块的隐式契约（如 `_STRINGS` 的 key 集合）。修改后必须跑 `python -m unittest discover -s tests -v` + `python tools/demo.py --auto`。
2. **i18n 回退的隐性依赖**：`_t()` 在 key 缺失时回退英语，表面上不报错，但会让某些语言出现“半英文”界面。新增 key 时必须同步 `_BUILTIN_STRINGS["en"]` 和 `_BUILTIN_STRINGS["zh_CN"]`。
3. **跨平台差异**：Windows 分区枚举、Android 提权、POSIX 隐藏位分别在三个平台有不同实现。CI 只在 Linux 上跑完整矩阵，Windows / Android 的关键分支靠真机验证。
4. **AI 对新系统机制的滞后性**：Android 11+ 的分区存储、Windows 11 的卷挂载行为变化，AI 不会主动跟进，必须靠人类真机反馈纠偏。

---

## 📜 许可

本项目代码使用 [MIT 协议](../LICENSE)。
