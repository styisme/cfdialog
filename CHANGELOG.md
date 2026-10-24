# Changelog

本文件记录 **cfdialog** 的版本更新历史。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Planned
- Windows 无盘符卷在 CI 上的自动化测试
- macOS 真机回归
- `lg/ar.txt` 补全完整阿拉伯语翻译（当前为占位）

---

## [0.3.0] - 2026-11-07

### Added
- **语言包外置**：核心只内置 `zh_CN` / `en`，其他语言从 `lg/*.txt` 按需加载。
- **调试开关 `ts.txt`**：`log` / `log_dir` / `force_language` 三键配置。
- **直接运行**：`python cfdialog.py` 打开文件管理器（读写模式）。
- **运行时语言注册**：`register_language()` / `unregister_language()` / `list_languages()` / `get_language_meta()`。
- **分区切换**：Windows 上包含无盘符卷，任意页面按 `g` 切换。
- **自动提权**：Windows UAC / Android root / Linux sudo-su。
- **`copy_into()` 公开工具**：带 `_unique_path` 重名自动改名。

### Changed
- 语言解析优先级：`ts.txt force_language` > 单次 `lang=` > `set_language()` > `detect_language()` > `en`。
- 单文件内部按“配置 → i18n → 平台 → 文件操作 → 浏览器 → 公开 API”分区。
- README 拆分为 `README.md`（中文）+ `README_EN.md`（英文）。

### Fixed
- `_normalize_lang_code()` 对 `zh-Hans` / `zh-Hant` / `jp` / `kr` 等别名归一化。
- 文件管理器只读模式仍允许 `cp` / `op` / `info`，禁用 `rm` / `ct` / `ps` / `rn` / `at`。

---

## [0.2.0] - 2026-10-xx

### Added
- 文件管理器（只读 / 读写）。
- 多选、扩展名过滤、隐藏文件切换。

---

## [0.1.0] - 2026-10-xx

### Added
- 首版 `pick_file` / `pick_folder` / `save` / `save_folder`。
- 内置 `zh_CN` / `en` 语言包。

---

## 版本对比链接

[Unreleased]: https://github.com/styisme/cfdialog/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/styisme/cfdialog/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/styisme/cfdialog/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/styisme/cfdialog/releases/tag/v0.1.0
