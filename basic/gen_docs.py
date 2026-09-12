#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_docs.py — 生成 cfdialog 的 README 与开发帮助文档

生成:
    README.md        中英双语合并的说明文档
    DEVELOPMENT.md   英文开发文档
    开发文档.md       中文开发文档

用法:
    python gen_docs.py                 # 生成全部
    python gen_docs.py --out ./docs    # 输出到指定目录
    python gen_docs.py --only readme   # 只生成 README
    python gen_docs.py --only dev      # 只生成两个开发文档
    python gen_docs.py --only dev-en   # 只生成英文开发文档
    python gen_docs.py --only dev-zh   # 只生成中文开发文档

注意:
    gen_docs.py 和 gen_lang_packs.py 均为开发辅助工具，
    正式发布版可以不含这两个文件。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

# =========================================================================== #
#                        文档元信息                                            #
# =========================================================================== #

LIB_NAME = "cfdialog"
LIB_VERSION = "0.3.0"
PYTHON_MIN = "3.8+"
AUTHOR_NOTE = "单文件、零依赖、跨平台 CLI 文件对话框库"

README_FILE = "README.md"
DEV_EN_FILE = "DEVELOPMENT.md"
DEV_ZH_FILE = "开发文档.md"


# =========================================================================== #
#                        Markdown 工具                                         #
# =========================================================================== #

def h(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def code(lang: str, body: str) -> str:
    return f"```{lang}\n{body.strip(chr(10))}\n```"


def table(headers: List[str], rows: List[List[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join([head, sep] + body)


def quote(text: str) -> str:
    return "\n".join("> " + ln for ln in text.splitlines())


def join(blocks: List[str]) -> str:
    return "\n\n".join(b for b in blocks if b and b.strip())


# =========================================================================== #
#                        共享内容片段                                          #
# =========================================================================== #

def _feature_table(lang: str) -> str:
    if lang == "zh":
        return table(
            ["特性", "说明"],
            [
                ["交互式 CLI 浏览器", "数字选择、目录跳转、返回上级、返回起点、多选、隐藏文件"],
                ["两种读取模式", "只给路径 / 自动复制到工作目录"],
                ["扩展名过滤", "单个、多个、不限制"],
                ["文件管理器", "只读 / 读写，支持删除 / 复制 / 剪切 / 粘贴 / 重命名 / 打开 / 属性"],
                ["保存时自由命名", "仅保存单个文件时可用"],
                ["Windows 分区", "含无盘符分区，任意页面按 `g` 切换"],
                ["语言包", "内置 zh_CN / en，其余从 lg/*.txt 加载"],
                ["调试开关", "ts.txt 控制 log 保存与强制语言"],
                ["自动提权", "Windows UAC / Android root / Linux sudo-su"],
                ["直接运行即用", "python cfdialog.py 打开文件管理器（读写）"],
            ],
        )
    return table(
        ["Feature", "Description"],
        [
            ["Interactive CLI browser", "Numeric entry, dir nav, back, home, multi-select, hidden toggle"],
            ["Two read modes", "path only / auto copy to work dir"],
            ["Extension filter", "Single / multiple / no limit"],
            ["File manager", "read-only / read-write; delete / copy / cut / paste / rename / open / attrs"],
            ["Free file naming on save", "Only when saving a single file"],
            ["Windows partitions", "Includes letter-less volumes; press `g` anywhere"],
            ["Language packs", "Built-in zh_CN / en; others loaded from lg/*.txt"],
            ["Debug switch", "ts.txt controls log saving and force_language"],
            ["Auto elevation", "Windows UAC / Android root / Linux sudo-su"],
            ["Run directly", "python cfdialog.py opens the file manager (read-write)"],
        ],
    )


def _quick_start_code() -> str:
    return code("python", """
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
""")


def _api_cheatsheet(lang: str) -> str:
    if lang == "zh":
        return table(
            ["我想……", "用法"],
            [
                ["选一个文件（只给路径）", "`pick_file(mode='path')`"],
                ["选多个文件并复制过来", "`pick_file(multiple=True, mode='copy')`"],
                ["只显示 `.txt`", "`pick_file(extensions='.txt')`"],
                ["只显示图片", "`pick_file(extensions=['.jpg', '.png'])`"],
                ["选一个文件夹", "`pick_folder()`"],
                ["让用户选保存目录", "`save(mode='path')`"],
                ["保存单个文件并可自由命名", "`save('src.txt', free_name=True)`"],
                ["保存多个文件到同一目录", "`save(['a','b'], mode='copy')`"],
                ["打开文件管理器", "`file_manager(access='readwrite')`"],
                ["切换语言", "`set_language('ja')`"],
                ["单次调用指定语言", "`pick_file(lang='ja')`"],
                ["注册新语言（运行时）", "`register_language('de', {...})`"],
                ["关闭自动提权", "`set_auto_elevate(False)`"],
                ["处理用户取消", "`except BrowserCancelled`"],
            ],
        )
    return table(
        ["I want to…", "Use"],
        [
            ["Pick one file (path only)", "`pick_file(mode='path')`"],
            ["Pick many and copy them", "`pick_file(multiple=True, mode='copy')`"],
            ["Show only `.txt`", "`pick_file(extensions='.txt')`"],
            ["Show only images", "`pick_file(extensions=['.jpg', '.png'])`"],
            ["Pick a folder", "`pick_folder()`"],
            ["Let the user pick a save dir", "`save(mode='path')`"],
            ["Save one file with a custom name", "`save('src.txt', free_name=True)`"],
            ["Save many files to one dir", "`save(['a','b'], mode='copy')`"],
            ["Open the file manager", "`file_manager(access='readwrite')`"],
            ["Change language", "`set_language('ja')`"],
            ["Override language once", "`pick_file(lang='ja')`"],
            ["Register a language at runtime", "`register_language('de', {...})`"],
            ["Disable auto-elevation", "`set_auto_elevate(False)`"],
            ["Handle user cancel", "`except BrowserCancelled`"],
        ],
    )


def _browser_keymap(lang: str) -> str:
    if lang == "zh":
        return table(
            ["键", "作用"],
            [
                ["`1` `2` `3`", "进入编号对应的目录 / 选中编号对应的文件"],
                ["`0` / `b` / `..`", "返回上一级目录"],
                ["`r` / `~`", "回到启动时所在的目录"],
                ["`s`", "选中当前目录"],
                ["`s<数字>`", "切换编号对应条目的选中状态"],
                ["`a` / `c` / `d`", "多选：全选 / 清空 / 完成"],
                ["`g`", "切换分区（Windows 含无盘符分区）"],
                ["`h`", "切换是否显示隐藏文件"],
                ["`q`", "取消并抛 `BrowserCancelled`"],
                ["直接输入路径", "跳转到该路径或直接选中该文件"],
                ["**管理器专用**", ""],
                ["`rm`", "删除选中（只读禁用）"],
                ["`cp` / `ct`", "复制 / 剪切到剪贴板"],
                ["`ps`", "粘贴（只读禁用）"],
                ["`rn`", "重命名（须恰好一项，只读禁用）"],
                ["`op`", "用系统默认程序打开（须恰好一项）"],
                ["`at`", "查看 / 修改属性（须恰好一项，只读禁用）"],
                ["`info` / `ls`", "查看属性 / 列出已选"],
            ],
        )
    return table(
        ["Key", "Action"],
        [
            ["`1` `2` `3`", "Enter dir / pick file"],
            ["`0` / `b` / `..`", "Go to parent"],
            ["`r` / `~`", "Return to start dir"],
            ["`s`", "Pick current dir"],
            ["`s<num>`", "Toggle item #num"],
            ["`a` / `c` / `d`", "Multi-select: all / clear / done"],
            ["`g`", "Switch partition (Windows, incl. letter-less)"],
            ["`h`", "Toggle hidden files"],
            ["`q`", "Cancel (raises `BrowserCancelled`)"],
            ["Direct path", "Jump / pick that file"],
            ["**Manager only**", ""],
            ["`rm`", "Delete selection (disabled in read-only)"],
            ["`cp` / `ct`", "Copy / cut to clipboard"],
            ["`ps`", "Paste (disabled in read-only)"],
            ["`rn`", "Rename (exactly one, disabled in read-only)"],
            ["`op`", "Open with the OS default app (exactly one)"],
            ["`at`", "View / edit attrs (exactly one, disabled in read-only)"],
            ["`info` / `ls`", "Show attrs / list selection"],
        ],
    )


def _folder_layout() -> str:
    return code("text", """
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
""")


def _ts_example() -> str:
    return code("ini", """
# cfdialog debug config
# 位置: 库目录 / ts.txt

# 是否开启 log 保存
log=true

# log 目录（相对于库目录）
log_dir=log

# 强制语言代码，覆盖一切来源；none 或留空表示不强制
force_language=zh_CN
""")


def _lang_pack_example() -> str:
    return code("text", """
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
""")


# =========================================================================== #
#                        README.md （中英双语）                                #
# =========================================================================== #

def build_readme() -> str:
    parts: List[str] = []

    parts.append(h(1, f"{LIB_NAME} v{LIB_VERSION}"))
    parts.append(quote(
        f"{AUTHOR_NOTE}\n"
        f"Single-file, zero-dependency, cross-platform CLI file dialog library\n"
        f"Python {PYTHON_MIN}  ·  MIT-style"
    ))

    # ----- TOC -----
    parts.append(join([
        h(2, "目录 / Table of Contents"),
        "\n".join([
            "1. [简介 / Introduction](#1-简介--introduction)",
            "2. [快速开始 / Quick Start](#2-快速开始--quick-start)",
            "3. [目录结构 / Folder Layout](#3-目录结构--folder-layout)",
            "4. [核心 API / Core API](#4-核心-api--core-api)",
            "5. [文件管理器 / File Manager](#5-文件管理器--file-manager)",
            "6. [语言包 / Language Packs](#6-语言包--language-packs)",
            "7. [调试开关 / Debug Switch](#7-调试开关--debug-switch)",
            "8. [分区切换 / Partitions](#8-分区切换--partitions)",
            "9. [键位表 / Keymap](#9-键位表--keymap)",
            "10. [FAQ](#10-faq)",
            "11. [开发文档 / Developer Docs](#11-开发文档--developer-docs)",
            "12. [致谢 / Acknowledgements](#12-致谢--acknowledgements)",
        ]),
    ]))

    # ----- 1. 简介 -----
    parts.append(join([
        h(2, "1. 简介 / Introduction"),
        h(3, "1.1 中文"),
        "`cfdialog` 是一个**单文件、零依赖**的 Python 库，"
        "为没有 GUI 的终端环境（服务器、Android/Termux、Pydroid、SSH、CI）"
        "提供文件 / 文件夹选择、保存、文件管理与自动提权能力。",
        "库的核心只内置**简体中文**和**英语**；其他语言放在 `lg/` 目录下的 txt 文件里，"
        "运行时按需加载。",
        h(3, "1.2 English"),
        "`cfdialog` is a **single-file, zero-dependency** Python library that brings "
        "file / folder selection, saving, file management and auto-elevation to "
        "pure-terminal environments (servers, Android/Termux, Pydroid, SSH, CI).",
        "The core ships with **Simplified Chinese** and **English** only. "
        "All other languages live as plain text packs in `lg/` and are loaded on demand.",
        h(3, "1.3 特性 / Features"),
        _feature_table("zh"),
        _feature_table("en"),
    ]))

    # ----- 2. 快速开始 -----
    parts.append(join([
        h(2, "2. 快速开始 / Quick Start"),
        h(3, "2.1 依赖 / Requirements"),
        join([
            "- Python ≥ 3.8",
            "- Standard library only (no third-party packages)",
        ]),
        h(3, "2.2 示例代码 / Example Code"),
        _quick_start_code(),
        h(3, "2.3 直接运行 / Run Directly"),
        "把 `cfdialog.py` 放在任意目录下，直接运行：",
        code("bash", "python cfdialog.py"),
        "会打开**读写模式的文件管理器**，起始目录为当前工作目录。",
        code("bash", "python cfdialog.py"),
        "Opens the file manager in **read-write** mode, starting from the current "
        "working directory.",
    ]))

    # ----- 3. 目录结构 -----
    parts.append(join([
        h(2, "3. 目录结构 / Folder Layout"),
        _folder_layout(),
        "**提示**：`gen_lang_packs.py`、`make_custom_lang.py`、`gen_docs.py` "
        "都是开发辅助脚本，正式发布版可以不含它们。",
        "**Note**: `gen_lang_packs.py`, `make_custom_lang.py`, `gen_docs.py` are "
        "development helpers and can be excluded from a release.",
    ]))

    # ----- 4. 核心 API -----
    parts.append(join([
        h(2, "4. 核心 API / Core API"),
        h(3, "4.1 选择器 / Pickers"),
        code("python", """
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
"""),
        table(
            ["参数 / Param", "说明 / Notes"],
            [
                ["`mode='path'`", "只返回选中项的路径 / return the chosen path only"],
                ["`mode='copy'`", "把选中项复制到 `work_dir`（默认 cwd），返回副本路径 / copy to `work_dir`, return copy path"],
                ["`multiple=True`", "返回 `List[Path]` / returns `List[Path]`"],
                ["`extensions`", "`\".txt\"` / `[\".txt\", \".md\"]` / `None`"],
                ["`lang`", "本次调用临时指定语言 / override language for this call"],
            ],
        ),
        h(3, "4.2 保存器 / Savers"),
        code("python", """
# --- save ---
save(sources=None, target_dir=None, mode="path",
     work_dir=None, free_name=False, default_name=None,
     overwrite=False, on_progress=None,
     start_dir=None, show_hidden=False,
     prompt=None, lang=None)

# --- save_folder （便捷包装）---
save_folder(start_dir=None, show_hidden=False,
            prompt=None, lang=None)
"""),
        table(
            ["参数 / Param", "说明 / Notes"],
            [
                ["`mode='path'`", "只返回目录，由调用方自己写文件 / return the dir only"],
                ["`mode='copy'`", "把 sources 复制到目标目录 / copy sources into target"],
                ["`free_name=True`", "仅单个源有效：弹出提示让用户自定义文件名 / single source only: prompt for a custom name"],
                ["`sources=None`", "只选目录不复制 / choose dir only"],
                ["`on_progress`", "批量进度回调 `(i, total, src)` / batch progress callback"],
            ],
        ),
        h(3, "4.3 速查表 / Cheat Sheet"),
        _api_cheatsheet("zh"),
        _api_cheatsheet("en"),
    ]))

    # ----- 5. 文件管理器 -----
    parts.append(join([
        h(2, "5. 文件管理器 / File Manager"),
        code("python", """
from cfdialog import file_manager

# 只读：禁用 rm / ct / ps / rn / at
file_manager(access="readonly")

# 读写：全部可用
file_manager(access="readwrite", start_dir="/home/user")
"""),
        h(3, "5.1 可用操作 / Available Operations"),
        table(
            ["操作 / Op", "说明 / Notes", "只读 / RO", "读写 / RW"],
            [
                ["导航 / navigation", "数字、`b`、`r`、`g`、`h`", "✔", "✔"],
                ["选择 / select", "`sa` 全选 / `sc` 清空 / `s<num>`", "✔", "✔"],
                ["`cp` 复制 / copy", "把选中放到剪贴板", "✔", "✔"],
                ["`rm` 删除 / delete", "删除选中", "✘", "✔"],
                ["`ct` 剪切 / cut", "剪切到剪贴板", "✘", "✔"],
                ["`ps` 粘贴 / paste", "从剪贴板粘贴", "✘", "✔"],
                ["`rn` 重命名 / rename", "仅一个选中", "✘", "✔"],
                ["`op` 打开 / open", "系统默认程序打开", "✔", "✔"],
                ["`at` 属性 / attrs", "查看 / 切换只读 / 隐藏", "✘", "✔"],
                ["`info` / `ls`", "查看属性 / 列出已选", "✔", "✔"],
            ],
        ),
        "**说明**：只读模式仍可**复制到剪贴板**和**打开文件**，"
        "但**不允许**任何会修改磁盘内容的操作。",
        "**Note**: read-only mode still allows **copy to clipboard** and **open**, "
        "but disables **any** action that would modify the disk.",
    ]))

    # ----- 6. 语言包 -----
    parts.append(join([
        h(2, "6. 语言包 / Language Packs"),
        h(3, "6.1 语言解析优先级 / Priority"),
        code("text", """
ts.txt  force_language        ← 最高 / highest
    ↓ 无 / none
lang= 参数（单次调用）        ← per-call
    ↓ None
set_language(...)             ← global
    ↓ 未调用
detect_language()             ← system
    ↓ 无匹配
en                            ← 兜底 / fallback
"""),
        h(3, "6.2 内置 / 外部 / Built-in vs External"),
        "内置仅两种：`zh_CN`、`en`。其他语言代码（例如 `ja`、`ko`、`ru`、`fr`、`es`、`de`）"
        "在运行时会自动从 `lg/<code>.txt` 加载，不存在则回退英语。",
        "Only `zh_CN` and `en` are built-in. Any other code (e.g. `ja`, `ko`, `ru`, "
        "`fr`, `es`, `de`) is loaded from `lg/<code>.txt` on demand; a missing pack "
        "falls back to English.",
        h(3, "6.3 语言包格式 / Pack Format"),
        _lang_pack_example(),
        h(3, "6.4 运行时注册 / Runtime Registration"),
        code("python", """
from cfdialog import register_language, set_language

register_language("de", {
    "prompt_folder": "Ordner auswählen",
    "prompt_file":   "Datei auswählen",
    "prompt_save":   "Speicherort auswählen",
})

set_language("de")
"""),
        "若想**持久化**为文件，请用 `make_custom_lang.py` 生成 `lg/<code>.txt`。",
        "For a **persistent** pack, use `make_custom_lang.py` to create `lg/<code>.txt`.",
    ]))

    # ----- 7. 调试开关 -----
    parts.append(join([
        h(2, "7. 调试开关 / Debug Switch"),
        h(3, "7.1 ts.txt"),
        _ts_example(),
        h(3, "7.2 字段 / Fields"),
        table(
            ["字段 / Field", "说明 / Notes"],
            [
                ["`log`", "是否开启 log 保存 / enable logging"],
                ["`log_dir`", "log 目录，相对库目录 / log dir relative to the lib"],
                ["`force_language`", "强制语言代码，覆盖一切；`none` 或留空 = 不强制 / force language, overrides everything"],
            ],
        ),
        h(3, "7.3 立即生效 / Live Reload"),
        code("python", """
from cfdialog import reload_debug_config, get_debug_config

reload_debug_config()
print(get_debug_config())
"""),
    ]))

    # ----- 8. 分区 -----
    parts.append(join([
        h(2, "8. 分区切换 / Partitions"),
        h(3, "8.1 何时可用 / When"),
        "**Windows** 上包括：带盘符的驱动器（C:、D:、E:…）以及**未分配盘符的卷**。"
        "在**选择器 / 保存器 / 文件管理器**的任意页面按 `g` 打开分区选择器。",
        "On **Windows**, includes drive letters (C:, D:, E:…) **and letter-less "
        "volumes**. Press `g` on any page of the picker, saver, or file manager to "
        "open the partition chooser.",
        h(3, "8.2 API"),
        code("python", """
from cfdialog import list_partitions

for p in list_partitions():
    print(p["name"], p["path"], p["label"], p["type"])
# 例 / e.g.
# C:  C:\\                System     fixed
# D:  D:\\                Data       fixed
# \\\\?\\Volume{...}\\     D:\\        Backup     volume
"""),
    ]))

    # ----- 9. 键位 -----
    parts.append(join([
        h(2, "9. 键位表 / Keymap"),
        _browser_keymap("zh"),
        _browser_keymap("en"),
    ]))

    # ----- 10. FAQ -----
    parts.append(join([
        h(2, "10. FAQ"),
        h(3, "Q1. 为什么 Android 上自动提权会让程序退出？"),
        "`su -c` 会新开一个 root 进程，父进程 `sys.exit(0)` 后你看到的就是“程序结束”。"
        "**建议**：Android 上 `set_auto_elevate(False)`，提权只在需要时手动做。",
        h(3, "Q1 (EN). Why does Android auto-elevation kill the program?"),
        "`su -c` spawns a new root process; the parent `sys.exit(0)` makes the "
        "original terminal appear \"done\". **Recommendation**: call "
        "`set_auto_elevate(False)` on Android and elevate manually when needed.",
        h(3, "Q2. 相对路径按哪个目录解析？"),
        "`Path.cwd()` —— **运行目录**，不是脚本所在目录。需要改基准就 `os.chdir()`。",
        h(3, "Q2 (EN). Which dir do relative paths resolve against?"),
        "`Path.cwd()` — the run dir, **not** the script dir. Use `os.chdir()` if needed.",
        h(3, "Q3. 扩展名过滤为什么对目录不生效？"),
        "让用户能进入子目录查找匹配文件。若强制过滤目录会破坏导航。",
        h(3, "Q3 (EN). Why does the extension filter not apply to directories?"),
        "So users can navigate into subdirs to find matching files. Filtering dirs "
        "would break navigation.",
        h(3, "Q4. 语言包不存在会怎样？"),
        "回退到英语，不会报错。库会把 `lg/*.txt` 加载尝试记入 log（若开启）。",
        h(3, "Q4 (EN). What if a language pack is missing?"),
        "Fallback to English, no exception. Load attempts are logged if logging is on.",
        h(3, "Q5. 只读模式下 `cp` 为什么可用？"),
        "因为 `cp` 只把选中项放入内存中的剪贴板，不写磁盘。`ps` 才真正写盘，"
        "所以只读禁用。",
        h(3, "Q5 (EN). Why is `cp` allowed in read-only mode?"),
        "`cp` only stores picks in the in-memory clipboard. `ps` actually writes to "
        "disk, so it is disabled.",
    ]))

    # ----- 11. 开发文档 -----
    parts.append(join([
        h(2, "11. 开发文档 / Developer Docs"),
        "更详细的设计说明、内部实现、扩展方式，请见：",
        "\n".join([
            "- [`DEVELOPMENT.md`](DEVELOPMENT.md) — English",
            "- [`开发文档.md`](开发文档.md) — 简体中文",
        ]),
        "For design notes, internals, and extension guides, see the files above.",
    ]))

    # ----- 12. 致谢 -----
    parts.append(join([
        h(2, "12. 致谢 / Acknowledgements"),
        h(3, "中文"),
        "\n".join([
            "- 本程序在开发过程中使用了 **DeepSeek** 提供的辅助（代码生成、"
            "文档撰写、测试用例设计、语言包翻译整理等），在此致谢。",
            "- 感谢所有测试与反馈过 cfdialog 的用户。",
            "- 本项目只依赖 Python 标准库，不含任何第三方运行时依赖。",
        ]),
        h(3, "English"),
        "\n".join([
            "- This project was developed with assistance from **DeepSeek** "
            "(code generation, documentation writing, test design, and language "
            "pack drafting). Sincere thanks.",
            "- Thanks to everyone who tested cfdialog and sent feedback.",
            "- The library depends on the Python standard library only; there are "
            "no third-party runtime dependencies.",
        ]),
    ]))

    parts.append("---")
    parts.append(
        f"*Generated by `gen_docs.py` · {LIB_NAME} v{LIB_VERSION}*"
    )

    return join(parts) + "\n"


# =========================================================================== #
#                        DEVELOPMENT.md （英文）                               #
# =========================================================================== #

def build_dev_en() -> str:
    parts: List[str] = []

    parts.append(h(1, f"{LIB_NAME} — Development Documentation"))
    parts.append(quote(
        f"Version {LIB_VERSION} | Python {PYTHON_MIN}\n"
        "Audience: contributors, integrators, reviewers."
    ))

    parts.append(join([
        h(2, "Table of Contents"),
        "\n".join([
            "1. [Design Goals](#1-design-goals)",
            "2. [Architecture](#2-architecture)",
            "3. [Public API](#3-public-api)",
            "4. [Browser Engine](#4-browser-engine)",
            "5. [File Manager](#5-file-manager)",
            "6. [i18n System](#6-i18n-system)",
            "7. [Debug System](#7-debug-system)",
            "8. [Elevation](#8-elevation)",
            "9. [Windows Partitions](#9-windows-partitions)",
            "10. [Copy / Move Semantics](#10-copy--move-semantics)",
            "11. [Extending](#11-extending)",
            "12. [Testing](#12-testing)",
            "13. [Release Checklist](#13-release-checklist)",
            "14. [FAQ](#14-faq)",
            "15. [Acknowledgements](#15-acknowledgements)",
        ]),
    ]))

    parts.append(join([
        h(2, "1. Design Goals"),
        "\n".join([
            "- **Single file**: `cfdialog.py` is the only runtime dependency. "
            "Easy to ship to Android, CI, embedded systems.",
            "- **Zero third-party deps**: only the Python standard library.",
            "- **Terminal-first**: works over SSH, in Termux, in Pydroid, in CI logs.",
            "- **Extensible without forking**: languages and debug options are "
            "driven by plain text files that live next to the library.",
            "- **Functional API**: `pick_*` / `save_*` / `file_manager` are "
            "module-level functions, no instances to manage.",
        ]),
    ]))

    parts.append(join([
        h(2, "2. Architecture"),
        h(3, "2.1 Layers"),
        code("text", """
┌────────────────────────────────────────────┐
│            User code (your_app.py)          │
└────────────────────────────────────────────┘
              ↓ calls
┌────────────────────────────────────────────┐
│ Public API                                  │
│   pick / pick_file / pick_folder            │
│   save / save_folder                        │
│   file_manager                              │
│   request_elevation / set_language ...      │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│ Core engine                                 │
│   _browse()        interactive loop          │
│   _list_dir()      enumerate + ext filter    │
│   _render_browse() terminal rendering        │
│   _browse_partitions() partition chooser     │
│   copy_into / _move_into                     │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│ Support                                     │
│   _STRINGS / _t()           i18n            │
│   _load_lang_pack()         lg/*.txt        │
│   _normalize_lang_code()    lang codemap    │
│   _normalize_extensions()   ext codemap     │
│   reload_debug_config()     ts.txt          │
│   list_partitions()         platform        │
└────────────────────────────────────────────┘
"""),
        h(3, "2.2 Module Layout (single file)"),
        table(
            ["Section", "Contents"],
            [
                ["Constants", "`LIB_DIR`, `LG_DIR`, `LOG_DIR`, `TS_FILE`, `SUPPORTED_LANGUAGES`, `BUILTIN_LANGUAGES`"],
                ["Exceptions", "`BrowserCancelled`"],
                ["Debug", "`reload_debug_config`, `get_debug_config`, `_debug_log`"],
                ["i18n", "`_BUILTIN_STRINGS`, `_STRINGS`, `_LANG_META`, `_load_lang_pack`, `_t`, public language APIs"],
                ["Elevation", "`request_elevation`, `_relaunch_windows`, `_relaunch_root`, `_maybe_elevate`"],
                ["Partitions", "`list_partitions`, `_list_windows_partitions`, `_win_enumerate_volumes`"],
                ["Extensions", "`_normalize_extensions`, `_match_extension`"],
                ["File ops", "`copy_into`, `_move_into`, `_unique_path`, `_remove_path`"],
                ["Browser", "`_browse`, `_list_dir`, `_render_browse`, `_browse_partitions`"],
                ["Pickers", "`pick`, `pick_file`, `pick_folder`"],
                ["Savers", "`save`, `save_folder`, `_prompt_free_name`"],
                ["Manager", "`file_manager`, `_open_path`, `_is_readonly`, `_set_readonly`, `_is_hidden`, `_set_hidden`"],
                ["Entry", "`_main` (runs `file_manager(access='readwrite')`)"],
            ],
        ),
    ]))

    parts.append(join([
        h(2, "3. Public API"),
        h(3, "3.1 Signature Summary"),
        code("python", """
def pick(select="file", multiple=False, mode="path",
         work_dir=None, start_dir=None, extensions=None,
         overwrite=False, show_hidden=False,
         prompt=None, lang=None): ...

def pick_file(multiple=False, mode="copy", work_dir=None,
              start_dir=None, extensions=None, overwrite=False,
              show_hidden=False, prompt=None, lang=None): ...

def pick_folder(multiple=False, mode="path", work_dir=None,
                start_dir=None, show_hidden=False,
                prompt=None, lang=None): ...

def save(sources=None, target_dir=None, mode="path",
         work_dir=None, free_name=False, default_name=None,
         overwrite=False, on_progress=None,
         start_dir=None, show_hidden=False,
         prompt=None, lang=None): ...

def save_folder(start_dir=None, show_hidden=False,
                prompt=None, lang=None): ...

def file_manager(start_dir=None, access="readwrite",
                 show_hidden=False, prompt=None, lang=None): ...

def list_partitions() -> list[dict]: ...

def request_elevation(interactive=True, ask=None, lang=None) -> str: ...
def set_auto_elevate(enabled: bool) -> None: ...
def is_elevated() -> bool: ...
def is_windows() -> bool: ...
def is_android() -> bool: ...
def has_root_available() -> bool: ...

def get_language() -> str: ...
def set_language(lang) -> str: ...
def detect_language() -> str: ...
def register_language(code, strings=None, base=None, meta=None, **kw) -> str: ...
def unregister_language(code) -> bool: ...
def list_languages() -> list[str]: ...
def get_language_meta(code) -> dict: ...

def reload_debug_config() -> dict: ...
def get_debug_config() -> dict: ...

def copy_into(src, dst_dir, overwrite=False) -> Path: ...
"""),
        h(3, "3.2 Return Value Conventions"),
        table(
            ["Function", "Single", "Multiple", "Cancel"],
            [
                ["`pick_file(mode='path')`", "`Path`", "`List[Path]`", "`BrowserCancelled`"],
                ["`pick_file(mode='copy')`", "`Path` (copy)", "`List[Path]`", "`BrowserCancelled`"],
                ["`pick_folder()`", "`Path`", "`List[Path]`", "`BrowserCancelled`"],
                ["`save(mode='path')`", "`Path` (dir)", "—", "`None`"],
                ["`save(mode='copy')`", "`Path` (copy)", "`List[Path]`", "`None`"],
                ["`save(free_name=True)`", "`Path` (target file)", "—", "`None`"],
                ["`file_manager()`", "`None`", "—", "—"],
            ],
        ),
    ]))

    parts.append(join([
        h(2, "4. Browser Engine"),
        h(3, "4.1 Main Loop"),
        code("text", """
while True:
    items = _list_dir(cur, show_hidden, exts, t)
    _render_browse(...)
    raw = input("> ").strip()
    dispatch(raw)
"""),
        h(3, "4.2 Dispatch Table"),
        table(
            ["Input", "Handler"],
            [
                ["`q` / `quit` / `exit`", "raise `BrowserCancelled`"],
                ["`g`", "open `_browse_partitions` and change `cur`"],
                ["`b` / `back` / `..`", "`cur = cur.parent`"],
                ["`r` / `~`", "`cur = origin`"],
                ["`h`", "flip `show_hidden`"],
                ["`c` / `a` / `d`", "multi-select: clear / all / done"],
                ["`s`", "pick current dir"],
                ["`s<num>`", "toggle item #num"],
                ["`<num>`", "enter dir or pick file"],
                ["path string", "resolve and jump / pick"],
            ],
        ),
        h(3, "4.3 Rendering"),
        "`_render_browse` prints a fixed-width banner (72 columns), the current "
        "directory, optional format limit, optional hidden marker, optional "
        "selection counter, the item list, then the key hints.",
        "`_format_size` produces compact sizes (`1.2K`, `3.4M`, `5.6G`).",
    ]))

    parts.append(join([
        h(2, "5. File Manager"),
        h(3, "5.1 State"),
        code("python", """
cur            # current directory
origin         # the start_dir passed in
picked         # list[Path] of selected items
clipboard      # list[Path]
clipboard_mode # None | "copy" | "cut"
allow_write    # access == "readwrite"
"""),
        h(3, "5.2 Read-Only Restrictions"),
        table(
            ["Command", "Read-only", "Rationale"],
            [
                ["`rm`", "disabled", "modifies disk"],
                ["`ct`", "disabled", "a pending cut is destructive on paste"],
                ["`ps`", "disabled", "writes to disk"],
                ["`rn`", "disabled", "modifies disk"],
                ["`at`", "disabled", "changes file attributes"],
                ["`cp`", "allowed", "in-memory clipboard only"],
                ["`op`", "allowed", "opens, does not modify"],
                ["`info` / `ls`", "allowed", "read-only inspection"],
            ],
        ),
        h(3, "5.3 Attributes"),
        "On Windows the manager uses `GetFileAttributesW` / `SetFileAttributesW` "
        "so the actual **read-only** and **hidden** bits are toggled.",
        "On POSIX, read-only is toggled via `os.chmod`; the hidden flag is a "
        "no-op (POSIX hides files by leading dot only).",
    ]))

    parts.append(join([
        h(2, "6. i18n System"),
        h(3, "6.1 Load Order"),
        code("text", """
1. Built-in _BUILTIN_STRINGS (zh_CN, en)
2. _load_lang_pack(code)   → lg/<code>.txt
3. _normalize_lang_code()  → alias map
4. Fallback to en
"""),
        h(3, "6.2 Pack Format"),
        code("text", """
# comments are metadata (leading '#')
# code=de
# name=Deutsch
# name_en=German
# native_name=Deutsch

prompt_folder=Ordner auswählen
prompt_file=Datei auswählen
...
"""),
        "Any key not present in the pack falls back to English at lookup time.",
        h(3, "6.3 Priority"),
        code("text", """
ts.txt  force_language         ← highest
   ↓ none
per-call lang= argument
   ↓ None
global set_language()
   ↓ not called
detect_language()
   ↓ no match
en
"""),
    ]))

    parts.append(join([
        h(2, "7. Debug System"),
        h(3, "7.1 ts.txt"),
        _ts_example(),
        h(3, "7.2 Global State"),
        code("python", """
_DEBUG = {
    "log": False,
    "log_dir": "log",
    "force_language": None,
}
"""),
        "`reload_debug_config()` re-reads the file. Call it after editing `ts.txt`.",
        "`_debug_log(msg)` appends to `log/YYYYMMDD.txt` when `log=true`.",
    ]))

    parts.append(join([
        h(2, "8. Elevation"),
        h(3, "8.1 Trigger"),
        "Elevation is **not** triggered at import. `_maybe_elevate()` runs on the "
        "**first** call to `pick_*`, `save_*`, or `file_manager`. A module-level "
        "`_ELEVATION_DONE` flag ensures it happens only once.",
        h(3, "8.2 Platform Strategy"),
        table(
            ["Platform", "Detection", "Mechanism"],
            [
                ["Windows", "`IsUserAnAdmin()`", "`ShellExecuteW(\"runas\", ...)` (UAC)"],
                ["Android", "`os.geteuid() == 0`", "`su -c \"<cmd>\"`"],
                ["Linux / macOS", "`os.geteuid() == 0`", "`sudo` then `su`"],
            ],
        ),
        h(3, "8.3 Return Values"),
        table(
            ["Value", "Meaning"],
            [
                ["`already`", "Already elevated"],
                ["`relaunched`", "Elevated process started; caller must `sys.exit(0)`"],
                ["`denied`", "User refused or elevation failed"],
                ["`unavailable`", "No elevation path (e.g. unrooted Android)"],
                ["`not_needed`", "Platform does not need elevation"],
            ],
        ),
        h(3, "8.4 Android"),
        "`su -c` spawns a new root process and the terminal session is lost. "
        "The parent **must** exit immediately after seeing `relaunched`. For "
        "this reason the demo disables auto-elevation on Android.",
    ]))

    parts.append(join([
        h(2, "9. Windows Partitions"),
        h(3, "9.1 Sources"),
        "\n".join([
            "- `GetLogicalDrives()` → drive letters (C:, D:, …)",
            "- `FindFirstVolumeW` / `FindNextVolumeW` → all volumes incl. **letter-less**",
            "- `GetVolumePathNamesForVolumeNameW` → mount points of each volume",
            "- `GetVolumeInformationW` → volume label",
        ]),
        h(3, "9.2 Volume Filter"),
        "A volume is skipped if any of its mount points is already a drive letter "
        "returned by `GetLogicalDrives()`. Letter-less volumes are listed with "
        "their `\\\\?\\Volume{...}\\` device path, which `os.listdir` accepts.",
    ]))

    parts.append(join([
        h(2, "10. Copy / Move Semantics"),
        h(3, "10.1 Name Clash"),
        code("python", """
def _unique_path(target: Path) -> Path:
    # a.txt -> a_1.txt -> a_2.txt
    # dir/  -> dir_1/ -> dir_2/
"""),
        "`overwrite=True` removes the existing target first; `False` picks a "
        "non-conflicting name.",
        h(3, "10.2 Directory Copy"),
        "Directories are copied recursively via `shutil.copytree`. Files use "
        "`shutil.copy2` to preserve metadata.",
        h(3, "10.3 Move"),
        "`_move_into` uses `shutil.move`, with the same collision policy.",
    ]))

    parts.append(join([
        h(2, "11. Extending"),
        h(3, "11.1 New Language Pack"),
        "Either drop a `lg/<code>.txt` file or call `register_language()` at runtime.",
        h(3, "11.2 New Select Mode"),
        code("python", """
if select not in ("file", "dir", "any", "executable"):
    ...

def accepts(p, is_dir):
    if select == "executable":
        return not is_dir and os.access(p, os.X_OK)
    ...
"""),
        h(3, "11.3 Custom Renderer"),
        code("python", """
import cfdialog, os

def my_render(cur, items, picked, multiple, prompt,
              show_hidden, exts, access, manager, t):
    os.system("clear")
    print(f"📁 {cur}")
    for i, (name, p, is_dir) in enumerate(items, 1):
        icon = "📂" if is_dir else "📄"
        print(f"  {i:>3}. {icon} {name}")

cfdialog._render_browse = my_render
"""),
        h(3, "11.4 Custom Copy"),
        code("python", """
import cfdialog
from pathlib import Path

_orig = cfdialog.copy_into

def my_copy(src, dst, overwrite=False):
    # keep symlinks as symlinks, etc.
    return _orig(src, dst, overwrite)

cfdialog.copy_into = my_copy
"""),
    ]))

    parts.append(join([
        h(2, "12. Testing"),
        "See `demo.py`. It offers:",
        "\n".join([
            "- **Auto tests** — no interaction, good for CI",
            "- **Manual tests** — step-by-step, interactive",
            "- **Language menu** — list / switch / inspect",
            "- **Partition viewer**",
            "- **Debug viewer** + live `ts.txt` reload",
        ]),
        code("bash", """
python demo.py             # interactive menu
python demo.py --auto      # auto only
python demo.py --ui en     # UI in English
python demo.py --list-langs
"""),
    ]))

    parts.append(join([
        h(2, "13. Release Checklist"),
        "\n".join([
            "1. Bump `LIB_VERSION` in `cfdialog.py`.",
            "2. Update `_BUILTIN_STRINGS` if new keys were added.",
            "3. Regenerate language packs with `gen_lang_packs.py`.",
            "4. Regenerate docs with `gen_docs.py`.",
            "5. Exclude dev-only files from the release:",
            "   - `gen_lang_packs.py`",
            "   - `make_custom_lang.py`",
            "   - `gen_docs.py`",
            "   - `demo.py` (optional)",
            "6. Verify `python cfdialog.py` opens the file manager.",
            "7. Verify `ts.txt` still works (log on, force a language).",
        ]),
    ]))

    parts.append(join([
        h(2, "14. FAQ"),
        h(3, "Q1. Why is the whole library in one file?"),
        "Distribution simplicity. Android/Termux, PyInstaller onefile, and CI "
        "runners all benefit from a single drop-in file.",
        h(3, "Q2. Why are language packs plain text?"),
        "So users can add a language without forking the library. A plain text "
        "pack is diffable, mergeable, and trivially editable on a phone.",
        h(3, "Q3. Why do I get `relaunched` and the process dies?"),
        "That is by design on Android and Windows. When `request_elevation` "
        "returns `relaunched`, the parent should call `sys.exit(0)`.",
        h(3, "Q4. Why is the extension filter not applied to directories?"),
        "So users can navigate. Filtering dirs would break navigation.",
        h(3, "Q5. Why does `file_manager` in read-only mode allow `cp`?"),
        "`cp` only stores picks in an in-memory clipboard. `ps` writes to disk "
        "and is therefore disabled.",
    ]))

    parts.append(join([
        h(2, "15. Acknowledgements"),
        "- This project was developed with assistance from **DeepSeek** "
        "(code generation, documentation writing, test design, and language "
        "pack drafting). Sincere thanks.",
        "- Thanks to everyone who tested cfdialog and sent feedback.",
        "- The library depends on the Python standard library only; there are "
        "no third-party runtime dependencies.",
    ]))

    parts.append("---")
    parts.append(f"*Generated by `gen_docs.py` · {LIB_NAME} v{LIB_VERSION}*")

    return join(parts) + "\n"


# =========================================================================== #
#                        开发文档.md （中文）                                  #
# =========================================================================== #

def build_dev_zh() -> str:
    parts: List[str] = []

    parts.append(h(1, f"{LIB_NAME} — 开发文档"))
    parts.append(quote(
        f"版本 {LIB_VERSION} | Python {PYTHON_MIN}\n"
        "读者：贡献者、集成方、审阅者"
    ))

    parts.append(join([
        h(2, "目录"),
        "\n".join([
            "1. [设计目标](#1-设计目标)",
            "2. [架构](#2-架构)",
            "3. [公共 API](#3-公共-api)",
            "4. [浏览器引擎](#4-浏览器引擎)",
            "5. [文件管理器](#5-文件管理器)",
            "6. [多语言系统](#6-多语言系统)",
            "7. [调试系统](#7-调试系统)",
            "8. [权限提升](#8-权限提升)",
            "9. [Windows 分区](#9-windows-分区)",
            "10. [复制 / 移动语义](#10-复制--移动语义)",
            "11. [扩展开发](#11-扩展开发)",
            "12. [测试](#12-测试)",
            "13. [发布清单](#13-发布清单)",
            "14. [FAQ](#14-faq)",
            "15. [致谢](#15-致谢)",
        ]),
    ]))

    parts.append(join([
        h(2, "1. 设计目标"),
        "\n".join([
            "- **单文件**：运行时只依赖 `cfdialog.py`。便于分发到 Android、CI、嵌入式环境。",
            "- **零第三方依赖**：只用 Python 标准库。",
            "- **终端优先**：兼容 SSH、Termux、Pydroid、CI 日志。",
            "- **无需 fork 即可扩展**：语言与调试选项由库旁边的纯文本文件驱动。",
            "- **函数式 API**：`pick_*` / `save_*` / `file_manager` 都是模块级函数，无需实例化。",
        ]),
    ]))

    parts.append(join([
        h(2, "2. 架构"),
        h(3, "2.1 分层"),
        code("text", """
┌────────────────────────────────────────────┐
│             用户代码 (your_app.py)          │
└────────────────────────────────────────────┘
              ↓ 调用
┌────────────────────────────────────────────┐
│ 公共 API                                    │
│   pick / pick_file / pick_folder            │
│   save / save_folder                        │
│   file_manager                              │
│   request_elevation / set_language ...      │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│ 核心引擎                                    │
│   _browse()        交互式主循环             │
│   _list_dir()      列举 + 扩展名过滤        │
│   _render_browse() 终端渲染                 │
│   _browse_partitions() 分区选择器           │
│   copy_into / _move_into                    │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│ 基础支持                                    │
│   _STRINGS / _t()           i18n            │
│   _load_lang_pack()         lg/*.txt        │
│   _normalize_lang_code()    语言归一化      │
│   _normalize_extensions()   扩展名归一化    │
│   reload_debug_config()     ts.txt          │
│   list_partitions()         分区探测        │
└────────────────────────────────────────────┘
"""),
        h(3, "2.2 单文件内部结构"),
        table(
            ["区块", "内容"],
            [
                ["常量", "`LIB_DIR`、`LG_DIR`、`LOG_DIR`、`TS_FILE`、`SUPPORTED_LANGUAGES`、`BUILTIN_LANGUAGES`"],
                ["异常", "`BrowserCancelled`"],
                ["调试", "`reload_debug_config`、`get_debug_config`、`_debug_log`"],
                ["i18n", "`_BUILTIN_STRINGS`、`_STRINGS`、`_LANG_META`、`_load_lang_pack`、`_t` 及语言公开 API"],
                ["提权", "`request_elevation`、`_relaunch_windows`、`_relaunch_root`、`_maybe_elevate`"],
                ["分区", "`list_partitions`、`_list_windows_partitions`、`_win_enumerate_volumes`"],
                ["扩展名", "`_normalize_extensions`、`_match_extension`"],
                ["文件操作", "`copy_into`、`_move_into`、`_unique_path`、`_remove_path`"],
                ["浏览器", "`_browse`、`_list_dir`、`_render_browse`、`_browse_partitions`"],
                ["选择器", "`pick`、`pick_file`、`pick_folder`"],
                ["保存器", "`save`、`save_folder`、`_prompt_free_name`"],
                ["管理器", "`file_manager`、`_open_path`、`_is_readonly`、`_set_readonly`、`_is_hidden`、`_set_hidden`"],
                ["入口", "`_main`（直接运行 `file_manager(access='readwrite')`）"],
            ],
        ),
    ]))

    parts.append(join([
        h(2, "3. 公共 API"),
        h(3, "3.1 签名一览"),
        code("python", """
def pick(select="file", multiple=False, mode="path",
         work_dir=None, start_dir=None, extensions=None,
         overwrite=False, show_hidden=False,
         prompt=None, lang=None): ...

def pick_file(multiple=False, mode="copy", work_dir=None,
              start_dir=None, extensions=None, overwrite=False,
              show_hidden=False, prompt=None, lang=None): ...

def pick_folder(multiple=False, mode="path", work_dir=None,
                start_dir=None, show_hidden=False,
                prompt=None, lang=None): ...

def save(sources=None, target_dir=None, mode="path",
         work_dir=None, free_name=False, default_name=None,
         overwrite=False, on_progress=None,
         start_dir=None, show_hidden=False,
         prompt=None, lang=None): ...

def save_folder(start_dir=None, show_hidden=False,
                prompt=None, lang=None): ...

def file_manager(start_dir=None, access="readwrite",
                 show_hidden=False, prompt=None, lang=None): ...

def list_partitions() -> list[dict]: ...

def request_elevation(interactive=True, ask=None, lang=None) -> str: ...
def set_auto_elevate(enabled: bool) -> None: ...
def is_elevated() -> bool: ...
def is_windows() -> bool: ...
def is_android() -> bool: ...
def has_root_available() -> bool: ...

def get_language() -> str: ...
def set_language(lang) -> str: ...
def detect_language() -> str: ...
def register_language(code, strings=None, base=None, meta=None, **kw) -> str: ...
def unregister_language(code) -> bool: ...
def list_languages() -> list[str]: ...
def get_language_meta(code) -> dict: ...

def reload_debug_config() -> dict: ...
def get_debug_config() -> dict: ...

def copy_into(src, dst_dir, overwrite=False) -> Path: ...
"""),
        h(3, "3.2 返回值约定"),
        table(
            ["函数", "单选", "多选", "取消"],
            [
                ["`pick_file(mode='path')`", "`Path`", "`List[Path]`", "`BrowserCancelled`"],
                ["`pick_file(mode='copy')`", "`Path`（副本）", "`List[Path]`", "`BrowserCancelled`"],
                ["`pick_folder()`", "`Path`", "`List[Path]`", "`BrowserCancelled`"],
                ["`save(mode='path')`", "`Path`（目录）", "—", "`None`"],
                ["`save(mode='copy')`", "`Path`（副本）", "`List[Path]`", "`None`"],
                ["`save(free_name=True)`", "`Path`（目标文件）", "—", "`None`"],
                ["`file_manager()`", "`None`", "—", "—"],
            ],
        ),
    ]))

    parts.append(join([
        h(2, "4. 浏览器引擎"),
        h(3, "4.1 主循环"),
        code("text", """
while True:
    items = _list_dir(cur, show_hidden, exts, t)
    _render_browse(...)
    raw = input("> ").strip()
    dispatch(raw)
"""),
        h(3, "4.2 输入分派"),
        table(
            ["输入", "处理"],
            [
                ["`q` / `quit` / `exit`", "抛 `BrowserCancelled`"],
                ["`g`", "打开 `_browse_partitions` 并切换 `cur`"],
                ["`b` / `back` / `..`", "`cur = cur.parent`"],
                ["`r` / `~`", "`cur = origin`"],
                ["`h`", "翻转 `show_hidden`"],
                ["`c` / `a` / `d`", "多选：清空 / 全选 / 完成"],
                ["`s`", "选中当前目录"],
                ["`s<数字>`", "切换编号条目"],
                ["`<数字>`", "进入目录或选中文件"],
                ["路径字符串", "解析并跳转 / 选中"],
            ],
        ),
        h(3, "4.3 渲染"),
        "`_render_browse` 打印固定宽度（72 列）的横幅、当前目录、可选格式限制、"
        "可选隐藏标记、可选已选计数、条目列表和按键提示。",
        "`_format_size` 生成紧凑尺寸（`1.2K`、`3.4M`、`5.6G`）。",
    ]))

    parts.append(join([
        h(2, "5. 文件管理器"),
        h(3, "5.1 状态"),
        code("python", """
cur            # 当前目录
origin         # 启动时传入的 start_dir
picked         # list[Path] 已选
clipboard      # list[Path]
clipboard_mode # None | "copy" | "cut"
allow_write    # access == "readwrite"
"""),
        h(3, "5.2 只读限制"),
        table(
            ["命令", "只读模式", "原因"],
            [
                ["`rm`", "禁用", "修改磁盘"],
                ["`ct`", "禁用", "粘贴时会破坏源文件"],
                ["`ps`", "禁用", "写入磁盘"],
                ["`rn`", "禁用", "修改磁盘"],
                ["`at`", "禁用", "修改文件属性"],
                ["`cp`", "允许", "仅写入内存剪贴板"],
                ["`op`", "允许", "只打开，不修改"],
                ["`info` / `ls`", "允许", "只读查看"],
            ],
        ),
        h(3, "5.3 属性"),
        "Windows 上通过 `GetFileAttributesW` / `SetFileAttributesW` 切换真正的"
        "**只读**和**隐藏**位。",
        "POSIX 上通过 `os.chmod` 切换只读；隐藏位是 no-op（POSIX 只有"
        "点号前缀隐藏）。",
    ]))

    parts.append(join([
        h(2, "6. 多语言系统"),
        h(3, "6.1 加载顺序"),
        code("text", """
1. 内置 _BUILTIN_STRINGS（zh_CN、en）
2. _load_lang_pack(code)   → lg/<code>.txt
3. _normalize_lang_code()  → 别名映射
4. 回退 en
"""),
        h(3, "6.2 语言包格式"),
        code("text", """
# 注释行是元数据（# 开头）
# code=de
# name=Deutsch
# name_en=German
# native_name=Deutsch

prompt_folder=Ordner auswählen
prompt_file=Datei auswählen
...
"""),
        "语言包未提供的键在运行时回退到英语。",
        h(3, "6.3 语言优先级"),
        code("text", """
ts.txt  force_language         ← 最高
   ↓ none
单次调用 lang= 参数
   ↓ None
全局 set_language()
   ↓ 未调用
detect_language()
   ↓ 无匹配
en
"""),
    ]))

    parts.append(join([
        h(2, "7. 调试系统"),
        h(3, "7.1 ts.txt"),
        _ts_example(),
        h(3, "7.2 全局状态"),
        code("python", """
_DEBUG = {
    "log": False,
    "log_dir": "log",
    "force_language": None,
}
"""),
        "`reload_debug_config()` 会重新读取文件。编辑 `ts.txt` 后调用即可生效。",
        "`_debug_log(msg)` 在 `log=true` 时追加到 `log/YYYYMMDD.txt`。",
    ]))

    parts.append(join([
        h(2, "8. 权限提升"),
        h(3, "8.1 触发时机"),
        "提权**不是在 import 时**触发。`_maybe_elevate()` 在**首次调用**"
        "`pick_*`、`save_*`、`file_manager` 时执行。",
        "模块级 `_ELEVATION_DONE` 保证只问一次。",
        h(3, "8.2 各平台策略"),
        table(
            ["平台", "检测", "提权方式"],
            [
                ["Windows", "`IsUserAnAdmin()`", "`ShellExecuteW(\"runas\", ...)`（UAC）"],
                ["Android", "`os.geteuid() == 0`", "`su -c \"<cmd>\"`"],
                ["Linux / macOS", "`os.geteuid() == 0`", "优先 `sudo`，其次 `su`"],
            ],
        ),
        h(3, "8.3 返回值"),
        table(
            ["值", "含义"],
            [
                ["`already`", "已具权限"],
                ["`relaunched`", "已启动提权进程；调用方应立即 `sys.exit(0)`"],
                ["`denied`", "用户拒绝或提权失败"],
                ["`unavailable`", "无可用途径（如未 root 的 Android）"],
                ["`not_needed`", "平台无需提权"],
            ],
        ),
        h(3, "8.4 Android 特别注意"),
        "`su -c` 会新开 root 进程且丢失终端会话。父进程在看到 `relaunched` 后"
        "**必须立即退出**。因此 demo 在 Android 上默认关闭自动提权。",
    ]))

    parts.append(join([
        h(2, "9. Windows 分区"),
        h(3, "9.1 数据来源"),
        "\n".join([
            "- `GetLogicalDrives()` → 盘符（C:、D:…）",
            "- `FindFirstVolumeW` / `FindNextVolumeW` → 全部卷（**含无盘符卷**）",
            "- `GetVolumePathNamesForVolumeNameW` → 每个卷的挂载点",
            "- `GetVolumeInformationW` → 卷标",
        ]),
        h(3, "9.2 卷过滤"),
        "如果某个卷的挂载点已经出现在 `GetLogicalDrives()` 返回的盘符里，就跳过。"
        "无盘符卷会以 `\\\\?\\Volume{...}\\` 形式列出，`os.listdir` 可直接访问。",
    ]))

    parts.append(join([
        h(2, "10. 复制 / 移动语义"),
        h(3, "10.1 同名策略"),
        code("python", """
def _unique_path(target: Path) -> Path:
    # a.txt -> a_1.txt -> a_2.txt
    # dir/  -> dir_1/ -> dir_2/
"""),
        "`overwrite=True` 会先删除已存在的目标；`False` 自动生成不冲突的名字。",
        h(3, "10.2 目录复制"),
        "目录用 `shutil.copytree` 递归复制。文件用 `shutil.copy2` 保留元数据。",
        h(3, "10.3 移动"),
        "`_move_into` 使用 `shutil.move`，重名策略相同。",
    ]))

    parts.append(join([
        h(2, "11. 扩展开发"),
        h(3, "11.1 新增语言包"),
        "放一个 `lg/<code>.txt`，或在运行时调用 `register_language()`。",
        h(3, "11.2 新增选择模式"),
        code("python", """
if select not in ("file", "dir", "any", "executable"):
    ...

def accepts(p, is_dir):
    if select == "executable":
        return not is_dir and os.access(p, os.X_OK)
    ...
"""),
        h(3, "11.3 自定义渲染"),
        code("python", """
import cfdialog, os

def my_render(cur, items, picked, multiple, prompt,
              show_hidden, exts, access, manager, t):
    os.system("clear")
    print(f"📁 {cur}")
    for i, (name, p, is_dir) in enumerate(items, 1):
        icon = "📂" if is_dir else "📄"
        print(f"  {i:>3}. {icon} {name}")

cfdialog._render_browse = my_render
"""),
        h(3, "11.4 自定义复制"),
        code("python", """
import cfdialog
from pathlib import Path

_orig = cfdialog.copy_into

def my_copy(src, dst, overwrite=False):
    # 例如保留软链接等
    return _orig(src, dst, overwrite)

cfdialog.copy_into = my_copy
"""),
    ]))

    parts.append(join([
        h(2, "12. 测试"),
        "见 `demo.py`，提供：",
        "\n".join([
            "- **自动测试** —— 无需交互，适合 CI",
            "- **手动测试** —— 逐项交互",
            "- **语言菜单** —— 列出 / 切换 / 查看",
            "- **分区查看器**",
            "- **调试查看器** + 实时重载 `ts.txt`",
        ]),
        code("bash", """
python demo.py             # 交互菜单
python demo.py --auto      # 只跑自动测试
python demo.py --ui en     # 界面英文
python demo.py --list-langs
"""),
    ]))

    parts.append(join([
        h(2, "13. 发布清单"),
        "\n".join([
            "1. 更新 `cfdialog.py` 中的 `LIB_VERSION`。",
            "2. 若新增了文案键，同步更新 `_BUILTIN_STRINGS`。",
            "3. 用 `gen_lang_packs.py` 重新生成语言包。",
            "4. 用 `gen_docs.py` 重新生成文档。",
            "5. 从发布版中剔除开发辅助文件：",
            "   - `gen_lang_packs.py`",
            "   - `make_custom_lang.py`",
            "   - `gen_docs.py`",
            "   - `demo.py`（可选）",
            "6. 验证 `python cfdialog.py` 能打开文件管理器。",
            "7. 验证 `ts.txt` 仍生效（log 开、强制语言）。",
        ]),
    ]))

    parts.append(join([
        h(2, "14. FAQ"),
        h(3, "Q1. 为什么整个库就一个文件？"),
        "分发简单。Android/Termux、PyInstaller 单文件、CI runner 都受益于"
        "一个可以直接拖进去的文件。",
        h(3, "Q2. 为什么语言包是纯文本？"),
        "让用户不用 fork 库就能加语言。纯文本可 diff、可 merge、手机上就能编辑。",
        h(3, "Q3. 为什么返回 `relaunched` 时进程会死？"),
        "Android 和 Windows 上这是设计如此。`request_elevation` 返回 "
        "`relaunched` 时父进程应该调用 `sys.exit(0)`。",
        h(3, "Q4. 为什么扩展名过滤对目录不生效？"),
        "让用户能进入子目录。过滤目录会破坏导航。",
        h(3, "Q5. 为什么只读模式允许 `cp`？"),
        "`cp` 只把选中项放进内存剪贴板。`ps` 才真正写磁盘，所以被禁用。",
    ]))

    parts.append(join([
        h(2, "15. 致谢"),
        "- 本程序在开发过程中使用了 **DeepSeek** 提供的辅助（代码生成、文档撰写、"
        "测试用例设计、语言包翻译整理等），在此致谢。",
        "- 感谢所有测试与反馈过 cfdialog 的用户。",
        "- 本项目只依赖 Python 标准库，不含任何第三方运行时依赖。",
    ]))

    parts.append("---")
    parts.append(f"*由 `gen_docs.py` 生成 · {LIB_NAME} v{LIB_VERSION}*")

    return join(parts) + "\n"


# =========================================================================== #
#                        生成入口                                              #
# =========================================================================== #

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def generate(out_dir: Path, only: str = "all") -> List[Path]:
    written: List[Path] = []

    if only in ("all", "readme"):
        p = out_dir / README_FILE
        _write(p, build_readme())
        written.append(p)

    if only in ("all", "dev", "dev-en"):
        p = out_dir / DEV_EN_FILE
        _write(p, build_dev_en())
        written.append(p)

    if only in ("all", "dev", "dev-zh"):
        p = out_dir / DEV_ZH_FILE
        _write(p, build_dev_zh())
        written.append(p)

    return written


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate cfdialog README and developer docs."
    )
    parser.add_argument("--out", default=".", help="Output directory")
    parser.add_argument(
        "--only",
        choices=("all", "readme", "dev", "dev-en", "dev-zh"),
        default="all",
        help="Generate only a subset",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out).expanduser().resolve()
    written = generate(out_dir, only=args.only)

    print(f"Generated {len(written)} file(s) in {out_dir}:")
    for p in written:
        size = p.stat().st_size
        lines = len(p.read_text(encoding="utf-8").splitlines())
        print(f"  - {p.name}  ({size} bytes, {lines} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())