# cfdialog v0.3.0

> 单文件、零依赖、跨平台 CLI 文件对话框库
> Single-file, zero-dependency, cross-platform CLI file dialog library
> Python 3.8+  ·  MIT-style

## 目录 / Table of Contents

1. [简介 / Introduction](#1-简介--introduction)
2. [快速开始 / Quick Start](#2-快速开始--quick-start)
3. [目录结构 / Folder Layout](#3-目录结构--folder-layout)
4. [核心 API / Core API](#4-核心-api--core-api)
5. [文件管理器 / File Manager](#5-文件管理器--file-manager)
6. [语言包 / Language Packs](#6-语言包--language-packs)
7. [调试开关 / Debug Switch](#7-调试开关--debug-switch)
8. [分区切换 / Partitions](#8-分区切换--partitions)
9. [键位表 / Keymap](#9-键位表--keymap)
10. [FAQ](#10-faq)
11. [开发文档 / Developer Docs](#11-开发文档--developer-docs)
12. [致谢 / Acknowledgements](#12-致谢--acknowledgements)

## 1. 简介 / Introduction

### 1.1 中文

`cfdialog` 是一个**单文件、零依赖**的 Python 库，为没有 GUI 的终端环境（服务器、Android/Termux、Pydroid、SSH、CI）提供文件 / 文件夹选择、保存、文件管理与自动提权能力。

库的核心只内置**简体中文**和**英语**；其他语言放在 `lg/` 目录下的 txt 文件里，运行时按需加载。

### 1.2 English

`cfdialog` is a **single-file, zero-dependency** Python library that brings file / folder selection, saving, file management and auto-elevation to pure-terminal environments (servers, Android/Termux, Pydroid, SSH, CI).

The core ships with **Simplified Chinese** and **English** only. All other languages live as plain text packs in `lg/` and are loaded on demand.

### 1.3 特性 / Features

| 特性 | 说明 |
| --- | --- |
| 交互式 CLI 浏览器 | 数字选择、目录跳转、返回上级、返回起点、多选、隐藏文件 |
| 两种读取模式 | 只给路径 / 自动复制到工作目录 |
| 扩展名过滤 | 单个、多个、不限制 |
| 文件管理器 | 只读 / 读写，支持删除 / 复制 / 剪切 / 粘贴 / 重命名 / 打开 / 属性 |
| 保存时自由命名 | 仅保存单个文件时可用 |
| Windows 分区 | 含无盘符分区，任意页面按 `g` 切换 |
| 语言包 | 内置 zh_CN / en，其余从 lg/*.txt 加载 |
| 调试开关 | ts.txt 控制 log 保存与强制语言 |
| 自动提权 | Windows UAC / Android root / Linux sudo-su |
| 直接运行即用 | python cfdialog.py 打开文件管理器（读写） |

| Feature | Description |
| --- | --- |
| Interactive CLI browser | Numeric entry, dir nav, back, home, multi-select, hidden toggle |
| Two read modes | path only / auto copy to work dir |
| Extension filter | Single / multiple / no limit |
| File manager | read-only / read-write; delete / copy / cut / paste / rename / open / attrs |
| Free file naming on save | Only when saving a single file |
| Windows partitions | Includes letter-less volumes; press `g` anywhere |
| Language packs | Built-in zh_CN / en; others loaded from lg/*.txt |
| Debug switch | ts.txt controls log saving and force_language |
| Auto elevation | Windows UAC / Android root / Linux sudo-su |
| Run directly | python cfdialog.py opens the file manager (read-write) |

## 2. 快速开始 / Quick Start

### 2.1 依赖 / Requirements

- Python ≥ 3.8

- Standard library only (no third-party packages)

### 2.2 示例代码 / Example Code

```python
from cfdialog import (
    pick_file, pick_folder, save, file_manager,
    set_language, get_language,
)

# --- 文件选择器：单选，只给路径 ---
p = pick_file(mode="path")

# --- 文件选择器：多选，复制到 ./imported ---
ps = pick_file(multiple=True, mode="copy", work_dir="./imported",
               extensions=[".txt", ".md"])

# --- 文件夹选择器 ---
d = pick_folder()

# --- 保存：允许用户自定义文件名 ---
out = save("report.txt", free_name=True)

# --- 保存：批量复制 ---
save(["a.txt", "b.txt"], mode="copy")

# --- 文件管理器 ---
file_manager(access="readwrite")     # 或 access="readonly"

# --- 语言 ---
print(get_language())                # 例如 "zh_CN"
set_language("ja")                   # 手动切换（ts.txt 未强制时有效）
```

### 2.3 直接运行 / Run Directly

把 `cfdialog.py` 放在任意目录下，直接运行：

```bash
python cfdialog.py
```

会打开**读写模式的文件管理器**，起始目录为当前工作目录。

```bash
python cfdialog.py
```

Opens the file manager in **read-write** mode, starting from the current working directory.

## 3. 目录结构 / Folder Layout

```text
basic/
├── cfdialog.py            # 主库（内置 zh_CN / en）
├── lg/                    # 外部语言包
│   ├── zh_TW.txt
│   ├── ja.txt
│   ├── ko.txt
│   ├── ru.txt
│   ├── fr.txt
│   └── es.txt
├── log/                   # 调试 log（ts.txt 开启后自动创建）
│   └── YYYYMMDD.txt
├── ts.txt                 # 调试开关
├── gen_lang_packs.py      # [开发辅助] 批量生成语言包
├── make_custom_lang.py    # [开发辅助] 交互式制作语言包
└── gen_docs.py            # [开发辅助] 生成本文档
```

**提示**：`gen_lang_packs.py`、`make_custom_lang.py`、`gen_docs.py` 都是开发辅助脚本，正式发布版可以不含它们。

**Note**: `gen_lang_packs.py`, `make_custom_lang.py`, `gen_docs.py` are development helpers and can be excluded from a release.

## 4. 核心 API / Core API

### 4.1 选择器 / Pickers

```python
# --- pick_file ---
pick_file(multiple=False, mode="copy", work_dir=None,
          start_dir=None, extensions=None, overwrite=False,
          show_hidden=False, prompt=None, lang=None)

# --- pick_folder ---
pick_folder(multiple=False, mode="path", work_dir=None,
            start_dir=None, show_hidden=False,
            prompt=None, lang=None)

# --- pick （统一入口）---
pick(select="file",        # "file" | "folder" | "any"
     multiple=False,
     mode="path",          # "path" | "copy"
     work_dir=None,
     start_dir=None,
     extensions=None,
     overwrite=False,
     show_hidden=False,
     prompt=None,
     lang=None)
```

| 参数 / Param | 说明 / Notes |
| --- | --- |
| `mode='path'` | 只返回选中项的路径 / return the chosen path only |
| `mode='copy'` | 把选中项复制到 `work_dir`（默认 cwd），返回副本路径 / copy to `work_dir`, return copy path |
| `multiple=True` | 返回 `List[Path]` / returns `List[Path]` |
| `extensions` | `".txt"` / `[".txt", ".md"]` / `None` |
| `lang` | 本次调用临时指定语言 / override language for this call |

### 4.2 保存器 / Savers

```python
# --- save ---
save(sources=None, target_dir=None, mode="path",
     work_dir=None, free_name=False, default_name=None,
     overwrite=False, on_progress=None,
     start_dir=None, show_hidden=False,
     prompt=None, lang=None)

# --- save_folder （便捷包装）---
save_folder(start_dir=None, show_hidden=False,
            prompt=None, lang=None)
```

| 参数 / Param | 说明 / Notes |
| --- | --- |
| `mode='path'` | 只返回目录，由调用方自己写文件 / return the dir only |
| `mode='copy'` | 把 sources 复制到目标目录 / copy sources into target |
| `free_name=True` | 仅单个源有效：弹出提示让用户自定义文件名 / single source only: prompt for a custom name |
| `sources=None` | 只选目录不复制 / choose dir only |
| `on_progress` | 批量进度回调 `(i, total, src)` / batch progress callback |

### 4.3 速查表 / Cheat Sheet

| 我想…… | 用法 |
| --- | --- |
| 选一个文件（只给路径） | `pick_file(mode='path')` |
| 选多个文件并复制过来 | `pick_file(multiple=True, mode='copy')` |
| 只显示 `.txt` | `pick_file(extensions='.txt')` |
| 只显示图片 | `pick_file(extensions=['.jpg', '.png'])` |
| 选一个文件夹 | `pick_folder()` |
| 让用户选保存目录 | `save(mode='path')` |
| 保存单个文件并可自由命名 | `save('src.txt', free_name=True)` |
| 保存多个文件到同一目录 | `save(['a','b'], mode='copy')` |
| 打开文件管理器 | `file_manager(access='readwrite')` |
| 切换语言 | `set_language('ja')` |
| 单次调用指定语言 | `pick_file(lang='ja')` |
| 注册新语言（运行时） | `register_language('de', {...})` |
| 关闭自动提权 | `set_auto_elevate(False)` |
| 处理用户取消 | `except BrowserCancelled` |

| I want to… | Use |
| --- | --- |
| Pick one file (path only) | `pick_file(mode='path')` |
| Pick many and copy them | `pick_file(multiple=True, mode='copy')` |
| Show only `.txt` | `pick_file(extensions='.txt')` |
| Show only images | `pick_file(extensions=['.jpg', '.png'])` |
| Pick a folder | `pick_folder()` |
| Let the user pick a save dir | `save(mode='path')` |
| Save one file with a custom name | `save('src.txt', free_name=True)` |
| Save many files to one dir | `save(['a','b'], mode='copy')` |
| Open the file manager | `file_manager(access='readwrite')` |
| Change language | `set_language('ja')` |
| Override language once | `pick_file(lang='ja')` |
| Register a language at runtime | `register_language('de', {...})` |
| Disable auto-elevation | `set_auto_elevate(False)` |
| Handle user cancel | `except BrowserCancelled` |

## 5. 文件管理器 / File Manager

```python
from cfdialog import file_manager

# 只读：禁用 rm / ct / ps / rn / at
file_manager(access="readonly")

# 读写：全部可用
file_manager(access="readwrite", start_dir="/home/user")
```

### 5.1 可用操作 / Available Operations

| 操作 / Op | 说明 / Notes | 只读 / RO | 读写 / RW |
| --- | --- | --- | --- |
| 导航 / navigation | 数字、`b`、`r`、`g`、`h` | ✔ | ✔ |
| 选择 / select | `sa` 全选 / `sc` 清空 / `s<num>` | ✔ | ✔ |
| `cp` 复制 / copy | 把选中放到剪贴板 | ✔ | ✔ |
| `rm` 删除 / delete | 删除选中 | ✘ | ✔ |
| `ct` 剪切 / cut | 剪切到剪贴板 | ✘ | ✔ |
| `ps` 粘贴 / paste | 从剪贴板粘贴 | ✘ | ✔ |
| `rn` 重命名 / rename | 仅一个选中 | ✘ | ✔ |
| `op` 打开 / open | 系统默认程序打开 | ✔ | ✔ |
| `at` 属性 / attrs | 查看 / 切换只读 / 隐藏 | ✘ | ✔ |
| `info` / `ls` | 查看属性 / 列出已选 | ✔ | ✔ |

**说明**：只读模式仍可**复制到剪贴板**和**打开文件**，但**不允许**任何会修改磁盘内容的操作。

**Note**: read-only mode still allows **copy to clipboard** and **open**, but disables **any** action that would modify the disk.

## 6. 语言包 / Language Packs

### 6.1 语言解析优先级 / Priority

```text
ts.txt  force_language        ← 最高 / highest
    ↓ 无 / none
lang= 参数（单次调用）        ← per-call
    ↓ None
set_language(...)             ← global
    ↓ 未调用
detect_language()             ← system
    ↓ 无匹配
en                            ← 兜底 / fallback
```

### 6.2 内置 / 外部 / Built-in vs External

内置仅两种：`zh_CN`、`en`。其他语言代码（例如 `ja`、`ko`、`ru`、`fr`、`es`、`de`）在运行时会自动从 `lg/<code>.txt` 加载，不存在则回退英语。

Only `zh_CN` and `en` are built-in. Any other code (e.g. `ja`, `ko`, `ru`, `fr`, `es`, `de`) is loaded from `lg/<code>.txt` on demand; a missing pack falls back to English.

### 6.3 语言包格式 / Pack Format

```text
# cfdialog language pack
# code=de
# name=Deutsch
# name_en=German
# native_name=Deutsch

prompt_folder=Ordner auswählen
prompt_file=Datei auswählen
prompt_save=Speicherort auswählen
current_dir=Aktuelles Verzeichnis
...
```

### 6.4 运行时注册 / Runtime Registration

```python
from cfdialog import register_language, set_language

register_language("de", {
    "prompt_folder": "Ordner auswählen",
    "prompt_file":   "Datei auswählen",
    "prompt_save":   "Speicherort auswählen",
})

set_language("de")
```

若想**持久化**为文件，请用 `make_custom_lang.py` 生成 `lg/<code>.txt`。

For a **persistent** pack, use `make_custom_lang.py` to create `lg/<code>.txt`.

## 7. 调试开关 / Debug Switch

### 7.1 ts.txt

```ini
# cfdialog debug config
# 位置: 库目录 / ts.txt

# 是否开启 log 保存
log=true

# log 目录（相对于库目录）
log_dir=log

# 强制语言代码，覆盖一切来源；none 或留空表示不强制
force_language=zh_CN
```

### 7.2 字段 / Fields

| 字段 / Field | 说明 / Notes |
| --- | --- |
| `log` | 是否开启 log 保存 / enable logging |
| `log_dir` | log 目录，相对库目录 / log dir relative to the lib |
| `force_language` | 强制语言代码，覆盖一切；`none` 或留空 = 不强制 / force language, overrides everything |

### 7.3 立即生效 / Live Reload

```python
from cfdialog import reload_debug_config, get_debug_config

reload_debug_config()
print(get_debug_config())
```

## 8. 分区切换 / Partitions

### 8.1 何时可用 / When

**Windows** 上包括：带盘符的驱动器（C:、D:、E:…）以及**未分配盘符的卷**。在**选择器 / 保存器 / 文件管理器**的任意页面按 `g` 打开分区选择器。

On **Windows**, includes drive letters (C:, D:, E:…) **and letter-less volumes**. Press `g` on any page of the picker, saver, or file manager to open the partition chooser.

### 8.2 API

```python
from cfdialog import list_partitions

for p in list_partitions():
    print(p["name"], p["path"], p["label"], p["type"])
# 例 / e.g.
# C:  C:\                System     fixed
# D:  D:\                Data       fixed
# \\?\Volume{...}\     D:\        Backup     volume
```

## 9. 键位表 / Keymap

| 键 | 作用 |
| --- | --- |
| `1` `2` `3` | 进入编号对应的目录 / 选中编号对应的文件 |
| `0` / `b` / `..` | 返回上一级目录 |
| `r` / `~` | 回到启动时所在的目录 |
| `s` | 选中当前目录 |
| `s<数字>` | 切换编号对应条目的选中状态 |
| `a` / `c` / `d` | 多选：全选 / 清空 / 完成 |
| `g` | 切换分区（Windows 含无盘符分区） |
| `h` | 切换是否显示隐藏文件 |
| `q` | 取消并抛 `BrowserCancelled` |
| 直接输入路径 | 跳转到该路径或直接选中该文件 |
| **管理器专用** |  |
| `rm` | 删除选中（只读禁用） |
| `cp` / `ct` | 复制 / 剪切到剪贴板 |
| `ps` | 粘贴（只读禁用） |
| `rn` | 重命名（须恰好一项，只读禁用） |
| `op` | 用系统默认程序打开（须恰好一项） |
| `at` | 查看 / 修改属性（须恰好一项，只读禁用） |
| `info` / `ls` | 查看属性 / 列出已选 |

| Key | Action |
| --- | --- |
| `1` `2` `3` | Enter dir / pick file |
| `0` / `b` / `..` | Go to parent |
| `r` / `~` | Return to start dir |
| `s` | Pick current dir |
| `s<num>` | Toggle item #num |
| `a` / `c` / `d` | Multi-select: all / clear / done |
| `g` | Switch partition (Windows, incl. letter-less) |
| `h` | Toggle hidden files |
| `q` | Cancel (raises `BrowserCancelled`) |
| Direct path | Jump / pick that file |
| **Manager only** |  |
| `rm` | Delete selection (disabled in read-only) |
| `cp` / `ct` | Copy / cut to clipboard |
| `ps` | Paste (disabled in read-only) |
| `rn` | Rename (exactly one, disabled in read-only) |
| `op` | Open with the OS default app (exactly one) |
| `at` | View / edit attrs (exactly one, disabled in read-only) |
| `info` / `ls` | Show attrs / list selection |

## 10. FAQ

### Q1. 为什么 Android 上自动提权会让程序退出？

`su -c` 会新开一个 root 进程，父进程 `sys.exit(0)` 后你看到的就是“程序结束”。**建议**：Android 上 `set_auto_elevate(False)`，提权只在需要时手动做。

### Q1 (EN). Why does Android auto-elevation kill the program?

`su -c` spawns a new root process; the parent `sys.exit(0)` makes the original terminal appear "done". **Recommendation**: call `set_auto_elevate(False)` on Android and elevate manually when needed.

### Q2. 相对路径按哪个目录解析？

`Path.cwd()` —— **运行目录**，不是脚本所在目录。需要改基准就 `os.chdir()`。

### Q2 (EN). Which dir do relative paths resolve against?

`Path.cwd()` — the run dir, **not** the script dir. Use `os.chdir()` if needed.

### Q3. 扩展名过滤为什么对目录不生效？

让用户能进入子目录查找匹配文件。若强制过滤目录会破坏导航。

### Q3 (EN). Why does the extension filter not apply to directories?

So users can navigate into subdirs to find matching files. Filtering dirs would break navigation.

### Q4. 语言包不存在会怎样？

回退到英语，不会报错。库会把 `lg/*.txt` 加载尝试记入 log（若开启）。

### Q4 (EN). What if a language pack is missing?

Fallback to English, no exception. Load attempts are logged if logging is on.

### Q5. 只读模式下 `cp` 为什么可用？

因为 `cp` 只把选中项放入内存中的剪贴板，不写磁盘。`ps` 才真正写盘，所以只读禁用。

### Q5 (EN). Why is `cp` allowed in read-only mode?

`cp` only stores picks in the in-memory clipboard. `ps` actually writes to disk, so it is disabled.

## 11. 开发文档 / Developer Docs

更详细的设计说明、内部实现、扩展方式，请见：

- [`DEVELOPMENT.md`](DEVELOPMENT.md) — English
- [`开发文档.md`](开发文档.md) — 简体中文

For design notes, internals, and extension guides, see the files above.

## 12. 致谢 / Acknowledgements

### 中文

- 本程序在开发过程中使用了 **DeepSeek** 提供的辅助（代码生成、文档撰写、测试用例设计、语言包翻译整理等），在此致谢。
- 感谢所有测试与反馈过 cfdialog 的用户。
- 本项目只依赖 Python 标准库，不含任何第三方运行时依赖。

### English

- This project was developed with assistance from **DeepSeek** (code generation, documentation writing, test design, and language pack drafting). Sincere thanks.
- Thanks to everyone who tested cfdialog and sent feedback.
- The library depends on the Python standard library only; there are no third-party runtime dependencies.

---

*Generated by `gen_docs.py` · cfdialog v0.3.0*
