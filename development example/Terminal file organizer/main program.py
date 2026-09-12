#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cfdialog 实用示范程序 —— 终端文件整理助手
A practical demo for cfdialog —— Terminal File Organizer

功能 / Features
    1) 多选文件 → 复制到指定文件夹      Copy picked files into a folder
    2) 多选文件 → 移动到指定文件夹      Move picked files into a folder
    3) 按文件类型自动分类整理            Auto-organize files by extension
    4) 打开 cfdialog 内置文件管理器      Open the built-in file manager
    5) 查看磁盘分区                      Inspect partitions
    6) 查看 / 重载调试配置 (ts.txt)      Inspect & reload debug config
    7) 切换语言                          Switch language

用法 / Usage
    python demo.py

依赖 / Requirements
    cfdialog.py  与 Python 3.8+（仅标准库 / stdlib only）
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# 载入 cfdialog / Import cfdialog
# --------------------------------------------------------------------------
try:
    import cfdialog
except ImportError:
    sys.stderr.write(
        "找不到 cfdialog.py，请把它放到本文件旁边。\n"
        "cfdialog.py not found — put it next to this file.\n"
    )
    raise SystemExit(1)

try:
    BrowserCancelled = cfdialog.BrowserCancelled
except AttributeError:                      # 兼容旧版本
    class BrowserCancelled(Exception):
        pass


# --------------------------------------------------------------------------
# 界面文案 / UI strings
# --------------------------------------------------------------------------
UI = {
    "zh": {
        "app_title":     "cfdialog 文件整理助手",
        "subtitle":      "选择 · 复制 · 移动 · 分类，全部在终端里完成",
        "menu_1":        "选择文件 → 复制到目标文件夹",
        "menu_2":        "选择文件 → 移动到目标文件夹",
        "menu_3":        "按文件类型自动分类整理",
        "menu_4":        "打开文件管理器",
        "menu_5":        "查看磁盘分区",
        "menu_6":        "查看 / 重载调试配置 (ts.txt)",
        "menu_7":        "切换语言 / Switch language",
        "menu_0":        "退出",
        "choose":        "请选择",
        "invalid":       "无效的输入，请重试。",
        "bye":           "再见！",
        "cancelled":     "已取消。",
        "no_files":      "没有选择任何文件。",
        "no_parts":      "未检测到分区信息。",
        "prompt_files":  "请选择要处理的文件（可多选）",
        "prompt_target": "请选择目标文件夹",
        "prompt_root":   "请选择分类整理的根目录",
        "prompt_mgr":    "文件管理器",
        "preview":       "预览：",
        "confirm":       "确认执行？输入 y 继续，其他键取消：",
        "summary":       "完成：成功 {ok} 项，失败 {fail} 项。",
        "all_good":      "全部成功 ✅",
        "fail_line":     "  ✘ {name}: {err}",
        "parts_header":  "磁盘分区：",
        "dbg_header":    "当前调试配置：",
        "dbg_hint":      "（编辑 ts.txt 后再次进入本菜单即可重新加载）",
        "lang_header":   "请选择语言 / Choose language:",
        "lang_back":     "返回 / Back",
        "lang_now":      "当前语言：{name}",
        "mode_prompt":   "选择操作方式：1) 移动   2) 复制   [默认 1]",
        "mode_move":     "移动",
        "mode_copy":     "复制",
    },
    "en": {
        "app_title":     "cfdialog File Organizer",
        "subtitle":      "Pick · copy · move · organize — all in your terminal",
        "menu_1":        "Pick files  →  copy into a folder",
        "menu_2":        "Pick files  →  move into a folder",
        "menu_3":        "Auto-organize files by type",
        "menu_4":        "Open the file manager",
        "menu_5":        "Inspect disk partitions",
        "menu_6":        "Inspect / reload debug config (ts.txt)",
        "menu_7":        "Switch language / 切换语言",
        "menu_0":        "Quit",
        "choose":        "Your choice",
        "invalid":       "Invalid input, please try again.",
        "bye":           "Bye!",
        "cancelled":     "Cancelled.",
        "no_files":      "No file selected.",
        "no_parts":      "No partition information detected.",
        "prompt_files":  "Pick the files to process (multiple selection)",
        "prompt_target": "Pick the destination folder",
        "prompt_root":   "Pick the root folder for organizing",
        "prompt_mgr":    "File manager",
        "preview":       "Preview:",
        "confirm":       "Proceed? Type y to continue, any other key to cancel:",
        "summary":       "Done: {ok} succeeded, {fail} failed.",
        "all_good":      "All succeeded ✅",
        "fail_line":     "  ✘ {name}: {err}",
        "parts_header":  "Disk partitions:",
        "dbg_header":    "Current debug config:",
        "dbg_hint":      "(edit ts.txt then re-enter this menu to reload)",
        "lang_header":   "Choose language / 请选择语言:",
        "lang_back":     "Back / 返回",
        "lang_now":      "Current language: {name}",
        "mode_prompt":   "Operation mode: 1) move   2) copy   [default 1]",
        "mode_move":     "Move",
        "mode_copy":     "Copy",
    },
}

LANG_NAMES = {
    "zh": {"zh": "中文", "en": "English"},
    "en": {"zh": "Chinese", "en": "English"},
}

_lang = "en"
_last_dir = None          # 记住上次浏览位置，下次打开更顺手


# --------------------------------------------------------------------------
# 文案辅助 / i18n helper
# --------------------------------------------------------------------------
def tr(key: str, **kw) -> str:
    table = UI.get(_lang) or UI["en"]
    text = table.get(key) or UI["en"].get(key, key)
    return text.format(**kw) if kw else text


def cf_lang() -> str:
    """传给 cfdialog 的语言代码。"""
    return "zh_CN" if _lang == "zh" else "en"


def safe_input(prompt: str = "") -> str:
    try:
        return input(prompt)
    except EOFError:               # 管道输入结束时优雅退出
        print()
        return "0"


def confirm() -> bool:
    try:
        ans = input(tr("confirm")).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return ans in ("y", "yes", "是")


# --------------------------------------------------------------------------
# 语言 / Language
# --------------------------------------------------------------------------
def init_language() -> None:
    """优先跟随 cfdialog 的当前语言（含 ts.txt 的 force_language）。"""
    global _lang
    code = ""
    for getter in (
        lambda: cfdialog.get_language(),
        lambda: cfdialog.detect_language(),
    ):
        try:
            code = getter() or ""
        except Exception:
            code = ""
        if code:
            break

    _lang = "zh" if str(code).lower().startswith("zh") else "en"
    _apply_language()


def switch_language(code: str) -> None:
    global _lang
    if code not in ("zh", "en"):
        return
    _lang = code
    _apply_language()


def _apply_language() -> None:
    try:
        cfdialog.set_language(cf_lang())
    except Exception as exc:                       # 设置失败不影响主流程
        print(tr("fail_line", name="set_language", err=exc))


def cmd_language() -> None:
    print()
    print(tr("lang_header"))
    print(f"  1) {LANG_NAMES[_lang]['zh']}")
    print(f"  2) {LANG_NAMES[_lang]['en']}")
    print(f"  3) {tr('lang_back')}")

    ans = safe_input("> ").strip()
    if ans == "1":
        switch_language("zh")
    elif ans == "2":
        switch_language("en")
    else:
        return

    print(tr("lang_now", name=LANG_NAMES[_lang][_lang]))


# --------------------------------------------------------------------------
# 小工具 / Helpers
# --------------------------------------------------------------------------
def unique_path(path: Path) -> Path:
    """a.txt → a_1.txt → a_2.txt；目录同理。"""
    if not path.exists():
        return path
    stem, suffix, parent = path.stem, path.suffix, path.parent
    n = 1
    while True:
        candidate = parent / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def _as_path_list(res) -> list:
    if res is None:
        return []
    if isinstance(res, (list, tuple)):
        return [Path(p) for p in res if p]
    return [Path(res)]


def _remember(path: Path) -> None:
    global _last_dir
    try:
        _last_dir = str(path)
    except Exception:
        pass


def fmt_size(n: float) -> str:
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def report(ok: int, fails: list) -> None:
    print()
    print(tr("summary", ok=ok, fail=len(fails)))
    for src, err in fails:
        print(tr("fail_line", name=src.name, err=err))
    if ok and not fails:
        print(tr("all_good"))


# --------------------------------------------------------------------------
# 选择文件 / 选择文件夹
# --------------------------------------------------------------------------
def collect_files() -> list:
    """多选文件，取消返回空列表。"""
    try:
        res = cfdialog.pick_file(
            multiple=True,
            mode="path",                 # 只要原始路径，不要副本
            start_dir=_last_dir,
            show_hidden=False,
            prompt=tr("prompt_files"),
            lang=cf_lang(),
        )
    except BrowserCancelled:
        print(tr("cancelled"))
        return []

    files = _as_path_list(res)
    if not files:
        print(tr("no_files"))
        return []

    _remember(files[0].parent)
    return files


def choose_folder(prompt_key: str):
    """选择单个文件夹，取消返回 None。"""
    try:
        res = cfdialog.pick_folder(
            multiple=False,
            mode="path",
            start_dir=_last_dir,
            show_hidden=False,
            prompt=tr(prompt_key),
            lang=cf_lang(),
        )
    except BrowserCancelled:
        print(tr("cancelled"))
        return None

    paths = _as_path_list(res)
    if not paths:
        print(tr("cancelled"))
        return None

    folder = paths[0]
    _remember(folder)
    return folder


# --------------------------------------------------------------------------
# 功能 1 / 2：复制、移动到目标文件夹
# --------------------------------------------------------------------------
def cmd_transfer(move: bool) -> None:
    files = collect_files()
    if not files:
        return

    target = choose_folder("prompt_target")
    if target is None:
        return

    print()
    print(tr("preview"))
    for i, f in enumerate(files, 1):
        print(f"  {i:>3}. {f}  →  {target / f.name}")
    print()

    if not confirm():
        print(tr("cancelled"))
        return

    ok, fails = 0, []
    for src in files:
        try:
            if move:
                target.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(unique_path(target / src.name)))
            else:
                # 直接用库里的 copy_into，重名自动加 _1 / _2
                cfdialog.copy_into(src, target, overwrite=False)
            ok += 1
        except Exception as exc:
            fails.append((src, exc))

    report(ok, fails)


# --------------------------------------------------------------------------
# 功能 3：按类型自动分类
# --------------------------------------------------------------------------
CATEGORY_EXTS = {
    "images":    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
                  ".ico", ".tif", ".tiff", ".heic", ".raw"},
    "documents": {".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md",
                  ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".odp",
                  ".csv", ".epub", ".mobi"},
    "audio":     {".mp3", ".wav", ".flac", ".aac", ".ogg", ".oga", ".m4a",
                  ".wma", ".opus", ".aiff"},
    "video":     {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
                  ".m4v", ".mpg", ".mpeg", ".3gp"},
    "archives":  {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
                  ".tgz", ".tbz2", ".iso", ".cab"},
    "code":      {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp",
                  ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".sh",
                  ".bat", ".ps1", ".json", ".xml", ".yml", ".yaml", ".toml",
                  ".ini", ".html", ".css", ".scss", ".sql"},
}
CATEGORY_OTHER = "other"


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    for name, exts in CATEGORY_EXTS.items():
        if ext in exts:
            return name
    return CATEGORY_OTHER


def cmd_organize() -> None:
    files = collect_files()
    if not files:
        return

    root = choose_folder("prompt_root")
    if root is None:
        return

    print(tr("mode_prompt"))
    answer = safe_input("> ").strip()
    move = (answer != "2")

    plan = []
    for f in files:
        bucket = root / classify(f)
        plan.append((f, bucket / f.name))

    print()
    print(tr("preview"))
    for i, (src, dst) in enumerate(plan, 1):
        print(f"  {i:>3}. {src.name}   →   {dst.parent.name}/{dst.name}")
    print()

    if not confirm():
        print(tr("cancelled"))
        return

    ok, fails = 0, []
    for src, dst in plan:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            target = unique_path(dst)
            if move:
                shutil.move(str(src), str(target))
            else:
                shutil.copy2(str(src), str(target))
            ok += 1
        except Exception as exc:
            fails.append((src, exc))

    report(ok, fails)


# --------------------------------------------------------------------------
# 功能 4：文件管理器
# --------------------------------------------------------------------------
def cmd_manager() -> None:
    try:
        cfdialog.file_manager(
            start_dir=_last_dir,
            access="readwrite",
            show_hidden=False,
            prompt=tr("prompt_mgr"),
            lang=cf_lang(),
        )
    except BrowserCancelled:
        print(tr("cancelled"))


# --------------------------------------------------------------------------
# 功能 5：磁盘分区
# --------------------------------------------------------------------------
def partition_line(part) -> str:
    if not isinstance(part, dict):
        return str(part)

    mount = (part.get("mount") or part.get("mountpoint") or
             part.get("path") or part.get("device") or "?")
    label = part.get("label") or part.get("name") or ""

    line = str(mount)
    if label and str(label) != str(mount):
        line += f"  [{label}]"

    try:                                        # 容量信息（失败就跳过）
        usage = shutil.disk_usage(str(mount))
        line += f"   {fmt_size(usage.free)} free / {fmt_size(usage.total)}"
    except Exception:
        pass

    return line


def cmd_partitions() -> None:
    try:
        parts = cfdialog.list_partitions()
    except Exception as exc:
        print(tr("fail_line", name="list_partitions", err=exc))
        return

    if not parts:
        print(tr("no_parts"))
        return

    print()
    print(tr("parts_header"))
    for i, p in enumerate(parts, 1):
        print(f"  {i:>2}. {partition_line(p)}")


# --------------------------------------------------------------------------
# 功能 6：调试配置
# --------------------------------------------------------------------------
def cmd_debug() -> None:
    try:
        cfg = cfdialog.reload_debug_config()
    except Exception as exc:
        print(tr("fail_line", name="reload_debug_config", err=exc))
        return

    print()
    print(tr("dbg_header"))
    if isinstance(cfg, dict):
        if not cfg:
            print("    (empty)")
        for key, value in cfg.items():
            print(f"    {key} = {value!r}")
    else:
        print(f"    {cfg!r}")
    print(tr("dbg_hint"))


# --------------------------------------------------------------------------
# 主程序 / Main
# --------------------------------------------------------------------------
def print_banner() -> None:
    version = getattr(cfdialog, "LIB_VERSION", "?")
    print()
    print("=" * 62)
    print(f"  cfdialog 实用示范 / Practical Demo      (cfdialog v{version})")
    print("=" * 62)


def print_menu() -> None:
    print()
    print("─" * 62)
    print(f"  {tr('app_title')}")
    print(f"  {tr('subtitle')}")
    print("─" * 62)
    for i in range(1, 8):
        print(f"  {i}) {tr('menu_' + str(i))}")
    print(f"  0) {tr('menu_0')}")
    print("─" * 62)


def main() -> int:
    init_language()
    print_banner()

    while True:
        print_menu()
        choice = safe_input(f"{tr('choose')} > ").strip().lower()

        try:
            if choice == "1":
                cmd_transfer(move=False)
            elif choice == "2":
                cmd_transfer(move=True)
            elif choice == "3":
                cmd_organize()
            elif choice == "4":
                cmd_manager()
            elif choice == "5":
                cmd_partitions()
            elif choice == "6":
                cmd_debug()
            elif choice == "7":
                cmd_language()
            elif choice in ("0", "q", "quit", "exit"):
                print(tr("bye"))
                return 0
            else:
                print(tr("invalid"))
        except BrowserCancelled:
            print(tr("cancelled"))
        except KeyboardInterrupt:
            print()
            print(tr("cancelled"))
        except Exception as exc:                # 兜底，避免整个程序崩掉
            print(tr("fail_line", name="error", err=exc))


if __name__ == "__main__":
    raise SystemExit(main())