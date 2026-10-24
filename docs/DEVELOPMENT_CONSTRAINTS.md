# 开发环境约束说明

本文档说明本仓库（**cfdialog**）的**实际开发条件**与**责任边界**。

本文件的作用是：让外部能看清“我们做了什么、没条件做什么”，而不是套用一套“有本地 IDE、有 CI、有真机”的标准模板。

> 相关文档：[README](../README.md) | [CHANGELOG](../CHANGELOG.md) | [贡献指南](../CONTRIBUTING.md) | [AI 披露](AI_DISCLOSURE.md)。

---

## 一、开发环境（按实际勾选）

- [ ] 有本地 IDE / SDK，可本地编译
- [ ] 有本地 diff 工具，可逐行审阅
- [x] 可跑 lint / 单元测试 —— *（`python -m unittest discover -s tests -v`，纯标准库）*
- [x] 走标准 PR 流程 —— *（个人项目，直接 push main 为主）*
- [x] **仅靠移动端开发** —— *（主要使用 Android 上的 Pydroid 3 编写与运行 Python，MGit 做版本管理）*
- [x] **仅靠云端 CI 编译** —— *（GitHub Actions，无本地 Windows / macOS 环境）*
- [ ] 有 Windows 真机 —— *（Windows 分区枚举靠 CI 编译验证 + 用户反馈）*
- [ ] 有 macOS 真机 —— *（macOS 分支完全靠代码审阅 + CI 语法检查）*

> 未勾选的条目，代表**本仓库物理上无法执行**，不是“忽略了”。

---

## 二、我们实际执行的机制（做了什么就勾什么）

### 披露

- [x] 提供 `docs/AI_DISCLOSURE.md`，说明 AI 参与范围与比例
- [x] README 顶部链接本文件
- [ ] Commit message 标注 `[ai-assisted]` —— *（使用 Conventional Commits，未强制标注）*

### 门禁

- [x] **unittest 门禁** —— *（`tests/test_smoke.py`，22 条测试，覆盖 import / 扩展名 / 语言 / 分区 / copy / save）*
- [x] **语法矩阵** —— *（Python 3.8–3.13 全跑 `compileall` + import）*
- [x] **跨 OS 矩阵** —— *（ubuntu / windows / macos × 3.8 / 3.12）*
- [x] **语言包加载验证** —— *（`tools/demo.py --list-langs`，应看到 8–9 种语言）*
- [x] **文档生成验证** —— *（`tools/gen_docs.py --out <temp>`，验证 patch 生效）*
- [x] **demo --auto informational** —— *（`continue-on-error: true`，输出进 artifact）*

### 测试

- [x] **本地 unittest** —— *（Android Pydroid 3 上跑过，22 tests OK）*
- [x] **本地 demo --list-langs** —— *（8 种语言可见）*
- [x] **本地 compileall** —— *（cfdialog.py / tools / examples 全部通过）*
- [x] **本地 gen_docs --out** —— *（3 份文档生成成功）*
- [x] **Android 真机** —— *（Termux / Pydroid 3 上 `python cfdialog.py` 打开文件管理器）*
- [ ] **Windows 真机** —— *（无盘符卷枚举、UAC 提权、隐藏位设置均未在本机验证）*
- [ ] **macOS 真机** —— *（`open` 命令打开文件、`/Volumes` 挂载点枚举未验证）*

> 未勾选的条目，代表**本仓库没有条件做**，不是“忘了做”。

---

## 三、诚实声明

**以下情况如实标注，不得美化：**

- **关于真机测试**：核心浏览器 / 文件管理器 / i18n 已在 Android（Termux / Pydroid 3）上真机验证。Windows 无盘符卷、macOS `open` 打开、Android root 提权的部分边缘场景未完全覆盖。
- **关于云端编译**：CI 编译通过仅代表语法与依赖正确，不代表所有功能在您的特定设备上绝对可用。
- **关于 AI 生成与正则补丁**：本项目属于极端的 AI 辅助驱动开发。在整理仓库结构时，AI 写的原地整理脚本曾把临时文件（`temp_*.py`）误复制进 `tools/`，靠后续 `fixup_cfdialog.py` 清理。这提醒：AI 生成的“自复制”逻辑必须人工审阅。
- **关于 `demo --auto` 的 `ar` 失败**：`demo.py` T02 里 `("ar", "ar")` 在无 `lg/ar.txt` 时必失败。当前已提供占位包 `lg/ar.txt`（`prompt_*` 为阿拉伯语，其余英文），完整翻译仍待补。CI 里 `demo-auto` 仍保持 informational，等 `ar` 完整后再升级为真门禁。

---

## 四、敏感模块清单（按实际填写）

| 模块 | 验证状态 |
|---|---|
| `cfdialog.py` `_browse()`（浏览器主循环） | ✅ 真机测试（Android Pydroid 3） |
| `cfdialog.py` `file_manager()`（只读 / 读写） | ✅ 真机测试（Android Pydroid 3） |
| `cfdialog.py` `_list_windows_partitions()`（无盘符卷） | ⚠️ 仅 CI 语法验证（无 Windows 真机） |
| `cfdialog.py` `_relaunch_windows()`（UAC） | ⚠️ 仅代码审阅（无 Windows 真机） |
| `cfdialog.py` `_relaunch_root()`（Android su / Linux sudo） | ✅ 部分真机测试（Android su 已验证；sudo 未验证） |
| `cfdialog.py` `_load_lang_pack()`（外部包加载） | ✅ 真机测试（8 种语言） |
| `cfdialog.py` `_is_hidden()` / `_set_hidden()`（Windows 隐藏位） | ⚠️ 仅代码审阅 |
| `tools/demo.py` `--auto` | ✅ 本地通过（除 `ar` 占位包外） |
| `tests/test_smoke.py` | ✅ 本地 22 tests OK + CI 矩阵 |
| `.github/workflows/ci.yml` | ✅ CI 运行通过 |

> 标注 `⚠️ 仅 CI` 的模块，**不代表不能发布**，但使用前请评估风险。

---

## 五、我们承认这不完美

形式化的 PR 流程、逐行代码审阅、本地静态分析，这些在本仓库里**可能全部缺位**。

我们用「**披露 + 门禁（unittest + CI） + 默认保守**」承担了**实质责任**，而不是假装做到了所有**形式责任**。

这是约束下的选择，不是对标准的否定。

---

## 六、给其他极限约束开发者的建议

如果你也在极端约束下开发（无本地 IDE / 移动端 / 单文件库），这套最小责任清单供参考：

1. **诚实披露 AI 参与度**（不要美化比例）
2. **能做的门禁不绕过**（有 unittest 就卡 unittest，有 CI 就卡 CI）
3. **测试状态如实标注**（做了就勾，没做就写“未验证”）
4. **敏感模块清单公开**（让外部能核对你测过什么）
5. **已知失败不隐藏**（`ar` 占位包 + informational job 是诚实的选择，不是掩盖）

**五件事做到了，你就已经承担了人类责任。**
