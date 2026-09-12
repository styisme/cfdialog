#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cfnotepad — 基于 cfdialog 的终端记事本

特性
  · 新建 / 打开 / 保存 / 另存为 / 编辑 / 查看
  · 简体中文 + English 双语
  · 启动时自动检测系统语言
  · 设置菜单中可手动切换语言，选择被持久化到 ~/.cfnotepad.conf

依赖
  · cfdialog.py（放在同目录或 PYTHONPATH 中）
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import cfdialog
except ImportError:
    sys.stderr.write(
        "Error: cfdialog.py not found.\n"
        "Place cfdialog.py next to cfnotepad.py, or add it to PYTHONPATH.\n"
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# 多语言
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES = ("zh_CN", "en")

LANG_NAMES = {
    "zh_CN": "简体中文",
    "en": "English",
}

_STRINGS = {
    "zh_CN": {
        "title":           "记事本",
        "untitled":        "未命名",
        "new":             "新建",
        "open":            "打开",
        "save":            "保存",
        "save_as":         "另存为",
        "edit":            "编辑",
        "view":            "查看",
        "language":        "语言 / Language",
        "quit":            "退出",
        "prompt_choice":   "请选择",
        "prompt_edit":     "编辑命令",
        "pick_open":       "选择要打开的文件",
        "pick_save":       "选择保存位置与文件名",
        "opened":          "已打开：{name}",
        "saved":           "已保存：{name}",
        "cancelled":       "已取消",
        "empty_doc":       "（空文档）",
        "new_done":        "已新建空文档。",
        "edit_help":       "命令：a=追加  d N=删除第N行  e N=编辑第N行  i N=在第N行后插入  c=清空  q=返回",
        "old":             "原内容",
        "new_text":        "新内容",
        "bad_line":        "无效的行号。",
        "unknown_cmd":     "未知命令。",
        "confirm_clear":   "确定清空全部内容吗？",
        "confirm_quit":    "有未保存的修改，确定退出吗？",
        "confirm_discard": "有未保存的修改，继续将丢失修改，确定吗？",
        "yes_no":          "[y/N]",
        "view_total":      "共 {n} 行",
        "language_menu":   "可选语言：",
        "language_auto":   "自动检测",
        "language_set":    "语言已切换为：{name}",
        "error":           "错误：{msg}",
        "goodbye":         "再见。",
    },
    "en": {
        "title":           "Notepad",
        "untitled":        "Untitled",
        "new":             "New",
        "open":            "Open",
        "save":            "Save",
        "save_as":         "Save As",
        "edit":            "Edit",
        "view":            "View",
        "language":        "Language / 语言",
        "quit":            "Quit",
        "prompt_choice":   "Choose",
        "prompt_edit":     "Edit command",
        "pick_open":       "Select a file to open",
        "pick_save":       "Choose destination and file name",
        "opened":          "Opened: {name}",
        "saved":           "Saved: {name}",
        "cancelled":       "Cancelled",
        "empty_doc":       "(empty document)",
        "new_done":        "New empty document.",
        "edit_help":       "Commands: a=append  d N=delete line N  e N=edit line N  i N=insert after N  c=clear  q=back",
        "old":             "old",
        "new_text":        "new",
        "bad_line":        "Invalid line number.",
        "unknown_cmd":     "Unknown command.",
        "confirm_clear":   "Clear all content?",
        "confirm_quit":    "Unsaved changes. Quit anyway?",
        "confirm_discard": "Unsaved changes will be lost. Continue?",
        "yes_no":          "[y/N]",
        "view_total":      "{n} line(s)",
        "language_menu":   "Available languages:",
        "language_auto":   "Auto detect",
        "language_set":    "Language switched to: {name}",
        "error":           "Error: {msg}",
        "goodbye":         "Bye.",
    },
}

_LANG = "en"


def _normalize_lang(code):
    """把任意语言代码归一到 SUPPORTED_LANGUAGES 中的一种。"""
    if not code:
        return "en"
    s = str(code).strip().replace("-", "_")
    low = s.lower()
    if low.startswith("zh"):
        return "zh_CN"
    if low.startswith("en"):
        return "en"
    return "en"


def _detect_lang():
    """借助 cfdialog 检测系统语言，并归一化到我们支持的语言。"""
    try:
        code = cfdialog.detect_language()
    except Exception:
        code = None
    return _normalize_lang(code)


def t(key, **kw):
    """翻译函数。缺失的键回退到英文，再回退到键本身。"""
    table = _STRINGS.get(_LANG, _STRINGS["en"])
    text = table.get(key) or _STRINGS["en"].get(key, key)
    if kw:
        try:
            return text.format(**kw)
        except Exception:
            return text
    return text


def _sync_cfdialog_language():
    """把当前语言同步给 cfdialog，让它的文件选择器也用同一种语言。"""
    try:
        cfdialog.set_language(_LANG)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 语言持久化
# ---------------------------------------------------------------------------

CONFIG_PATH = Path.home() / ".cfnotepad.conf"


def read_config_language():
    """从配置文件里读出用户上次选择的语言，没有则返回 None。"""
    try:
        if not CONFIG_PATH.is_file():
            return None
        for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "language":
                value = value.strip()
                return value or None
    except Exception:
        return None
    return None


def write_config_language(lang):
    try:
        CONFIG_PATH.write_text(
            "# cfnotepad configuration\nlanguage={}\n".format(lang),
            encoding="utf-8",
        )
    except Exception:
        pass


def clear_config_language():
    try:
        if CONFIG_PATH.is_file():
            CONFIG_PATH.unlink()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

def _line(ch="=", n=58):
    print(ch * n)


def _confirm(message):
    try:
        answer = input("{} {} ".format(message, t("yes_no"))).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


# ---------------------------------------------------------------------------
# 文档模型
# ---------------------------------------------------------------------------

class Notepad:
    """内存中的文本文档。"""

    def __init__(self):
        self.path = None      # 当前文件 Path，None 表示未命名
        self.lines = []       # list[str]
        self.dirty = False    # 是否有未保存的修改

    def reset(self):
        self.path = None
        self.lines = []
        self.dirty = False

    def load(self, path):
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="replace")
        self.lines = text.splitlines()
        self.path = p
        self.dirty = False

    def dump(self):
        text = "\n".join(self.lines)
        if self.lines:
            text += "\n"
        return text

    def save_to(self, path):
        p = Path(path)
        p.write_text(self.dump(), encoding="utf-8")
        self.path = p
        self.dirty = False

    @property
    def display_name(self):
        return self.path.name if self.path else t("untitled")


# ---------------------------------------------------------------------------
# 动作
# ---------------------------------------------------------------------------

def action_open(app):
    if app.dirty and not _confirm(t("confirm_discard")):
        return

    start_dir = str(app.path.parent) if app.path else None

    try:
        picked = cfdialog.pick_file(
            multiple=False,
            mode="path",
            start_dir=start_dir,
            show_hidden=False,
            prompt=t("pick_open"),
            lang=_LANG,
        )
    except cfdialog.BrowserCancelled:
        print(t("cancelled"))
        return
    except Exception as exc:
        print(t("error", msg=str(exc)))
        return

    if not picked:
        print(t("cancelled"))
        return

    try:
        app.load(Path(picked))
    except Exception as exc:
        print(t("error", msg=str(exc)))
        return

    print(t("opened", name=Path(picked).name))


def action_save(app, force_as=False):
    if app.path is not None and not force_as:
        try:
            app.save_to(app.path)
        except Exception as exc:
            print(t("error", msg=str(exc)))
            return
        print(t("saved", name=app.path.name))
        return

    start_dir = str(app.path.parent) if app.path else None
    default_name = app.path.name if app.path else "untitled.txt"

    try:
        target = cfdialog.save(
            mode="path",
            free_name=True,
            default_name=default_name,
            overwrite=False,
            start_dir=start_dir,
            show_hidden=False,
            prompt=t("pick_save"),
            lang=_LANG,
        )
    except cfdialog.BrowserCancelled:
        print(t("cancelled"))
        return
    except Exception as exc:
        print(t("error", msg=str(exc)))
        return

    if not target:
        print(t("cancelled"))
        return

    try:
        app.save_to(Path(target))
    except Exception as exc:
        print(t("error", msg=str(exc)))
        return

    print(t("saved", name=Path(target).name))


def action_view(app):
    print()
    _line("-")
    if app.lines:
        for i, line in enumerate(app.lines, 1):
            print("  {:>4} | {}".format(i, line))
    else:
        print("       " + t("empty_doc"))
    _line("-")
    print("  " + t("view_total", n=len(app.lines)))


def action_edit(app):
    """逐行编辑模式。"""
    while True:
        print()
        _line("-")
        if app.lines:
            for i, line in enumerate(app.lines, 1):
                print("  {:>4} | {}".format(i, line))
        else:
            print("       " + t("empty_doc"))
        _line("-")
        print("  " + t("edit_help"))

        try:
            raw = input(t("prompt_edit") + "> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue
        if raw in ("q", "quit", ":q"):
            break

        # 直接输入数字 → 编辑那一行
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(app.lines):
                print("  {}: {}".format(t("old"), app.lines[idx]))
                try:
                    text = input("  {}: ".format(t("new_text")))
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                app.lines[idx] = text
                app.dirty = True
            else:
                print("  " + t("bad_line"))
            continue

        parts = raw.split(maxsplit=1)
        op = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if op in ("a", "append", "+"):
            try:
                text = input("  + ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            app.lines.append(text)
            app.dirty = True

        elif op in ("d", "del", "delete", "-"):
            if arg.isdigit():
                idx = int(arg) - 1
                if 0 <= idx < len(app.lines):
                    del app.lines[idx]
                    app.dirty = True
                else:
                    print("  " + t("bad_line"))
            else:
                print("  " + t("bad_line"))

        elif op in ("e", "edit"):
            if arg.isdigit():
                idx = int(arg) - 1
                if 0 <= idx < len(app.lines):
                    print("  {}: {}".format(t("old"), app.lines[idx]))
                    try:
                        text = input("  {}: ".format(t("new_text")))
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    app.lines[idx] = text
                    app.dirty = True
                else:
                    print("  " + t("bad_line"))
            else:
                print("  " + t("bad_line"))

        elif op in ("i", "insert"):
            if arg.isdigit():
                idx = int(arg)                      # 在第 N 行之后插入
                if 0 <= idx <= len(app.lines):
                    try:
                        text = input("  + ")
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    app.lines.insert(idx, text)
                    app.dirty = True
                else:
                    print("  " + t("bad_line"))
            else:
                print("  " + t("bad_line"))

        elif op in ("c", "clear"):
            if _confirm(t("confirm_clear")):
                app.lines.clear()
                app.dirty = True

        else:
            print("  " + t("unknown_cmd"))


def action_language():
    """语言设置：自动检测 + 手动指定。"""
    global _LANG

    detected = _detect_lang()

    print()
    print("  " + t("language_menu"))
    print("  0. {} ({})".format(t("language_auto"), LANG_NAMES.get(detected, detected)))
    for i, code in enumerate(SUPPORTED_LANGUAGES, 1):
        mark = " *" if code == _LANG else ""
        print("  {}. {}{}".format(i, LANG_NAMES.get(code, code), mark))

    try:
        choice = input(t("prompt_choice") + "> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if not choice.isdigit():
        print(t("cancelled"))
        return

    n = int(choice)
    if n == 0:
        new_lang = detected
        clear_config_language()          # 下次启动重新检测
    elif 1 <= n <= len(SUPPORTED_LANGUAGES):
        new_lang = SUPPORTED_LANGUAGES[n - 1]
        write_config_language(new_lang)
    else:
        print(t("cancelled"))
        return

    _LANG = new_lang
    _sync_cfdialog_language()
    print(t("language_set", name=LANG_NAMES.get(_LANG, _LANG)))


# ---------------------------------------------------------------------------
# 主菜单
# ---------------------------------------------------------------------------

def main_menu(app):
    while True:
        print()
        _line("=")
        flag = " *" if app.dirty else ""
        print("  {}  —  {}{}".format(t("title"), app.display_name, flag))
        if app.path:
            print("  {}".format(app.path))
        _line("=")
        print("  n. {}".format(t("new")))
        print("  o. {}".format(t("open")))
        print("  s. {}".format(t("save")))
        print("  a. {}".format(t("save_as")))
        print("  e. {}".format(t("edit")))
        print("  v. {}".format(t("view")))
        print("  l. {}".format(t("language")))
        print("  q. {}".format(t("quit")))
        _line("-")

        try:
            choice = input(t("prompt_choice") + "> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            if _confirm(t("confirm_quit")):
                break
            continue

        if choice in ("q", "quit", "exit"):
            if app.dirty and not _confirm(t("confirm_quit")):
                continue
            break

        elif choice in ("n", "new"):
            if app.dirty and not _confirm(t("confirm_discard")):
                continue
            app.reset()
            print(t("new_done"))

        elif choice in ("o", "open"):
            action_open(app)

        elif choice in ("s", "save"):
            action_save(app, force_as=False)

        elif choice in ("a", "save_as", "save-as"):
            action_save(app, force_as=True)

        elif choice in ("e", "edit"):
            action_edit(app)

        elif choice in ("v", "view"):
            action_view(app)

        elif choice in ("l", "lang", "language"):
            action_language()

        else:
            print("  " + t("unknown_cmd"))


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    global _LANG

    # 1) 决定初始语言：配置文件 > 系统检测
    configured = read_config_language()
    if configured:
        _LANG = _normalize_lang(configured)
    else:
        _LANG = _detect_lang()
    _sync_cfdialog_language()

    # 2) Android 上不自动提权（su 会脱离终端）
    try:
        if cfdialog.is_android():
            cfdialog.set_auto_elevate(False)
    except Exception:
        pass

    app = Notepad()

    # 3) 支持命令行直接打开文件
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if target.is_file():
            try:
                app.load(target)
                print(t("opened", name=target.name))
            except Exception as exc:
                print(t("error", msg=str(exc)))
        else:
            print(t("error", msg="file not found: {}".format(target)))

    main_menu(app)
    print(t("goodbye"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)