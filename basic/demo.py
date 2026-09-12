#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo.py — cfdialog v0.3.0 可用性测试

用法:
    python demo.py                  进入主菜单
    python demo.py --auto           直接进入全自动测试
    python demo.py --ui en          界面强制英文
    python demo.py --ui zh          界面强制中文
    python demo.py --lang ja        测试时切到日语（ts.txt 未强制时生效）
    python demo.py --list-langs     列出可用的语言后退出

覆盖范围:
    * 语言系统: 探测、切换、别名归一化、注册/移除、元数据、lg 外部包
    * 提权: 状态检测、手动请求、自动开关
    * 分区: 列举、进入分区选择器
    * 选择器: pick / pick_file / pick_folder，path/copy、单选/多选、扩展名过滤
    * 保存器: save / save_folder，path/copy、free_name、批量、进度回调
    * 文件管理器: readonly / readwrite 模式全按键
    * 工具: copy_into、扩展名归一化、异常处理
    * 调试: ts.txt 读取、log 保存、强制语言

每个测试会依次展示:
    - 目的
    - 涉及 API
    - 期望结果
    - 需要用户输入的参数
"""

from __future__ import annotations

import argparse
import inspect
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, List, Optional

# ---------------------------------------------------------------------------
# 定位并导入 cfdialog
# ---------------------------------------------------------------------------

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

try:
    import cfdialog
    from cfdialog import (
        BrowserCancelled,
        BUILTIN_LANGUAGES,
        LIB_DIR,
        LG_DIR,
        LOG_DIR,
        TS_FILE,
        copy_into,
        detect_language,
        file_manager,
        get_debug_config,
        get_language,
        get_language_meta,
        has_root_available,
        is_android,
        is_elevated,
        is_windows,
        list_languages,
        list_partitions,
        pick,
        pick_file,
        pick_folder,
        register_language,
        reload_debug_config,
        request_elevation,
        save,
        save_folder,
        set_auto_elevate,
        set_language,
        unregister_language,
    )
except ImportError as exc:
    print(f"无法导入 cfdialog: {exc}")
    print(f"请确保 cfdialog.py 与 demo.py 在同一目录，或已在 sys.path 中。")
    print(f"当前查找目录: {THIS_DIR}")
    sys.exit(1)


# ===========================================================================
# DEMO 自己的界面文案（不是库的语言包）
# ===========================================================================

UI = {
    "zh_CN": {
        "banner": "cfdialog v{ver} 可用性测试",
        "lib_dir": "库目录",
        "run_dir": "运行目录",
        "work_dir": "工作区",
        "lib_lang": "库当前语言",
        "force_lang": "强制语言 (ts.txt)",
        "no_force": "(无)",
        "platform": "平台",
        "android": "Android",
        "windows": "Windows",
        "unix": "Unix",
        "lg_packs": "外部语言包",
        "lang_pick": "请选择界面语言 / Choose UI language",
        "lang_pick_hint": "1) 中文  2) English",
        "menu_title": "主菜单",
        "menu_1": "快速自动测试（不需要交互）",
        "menu_2": "手动测试（含自动项，逐项进行）",
        "menu_3": "语言设置 / 展示",
        "menu_4": "查看分区",
        "menu_5": "调试信息",
        "menu_6": "重新加载 ts.txt",
        "menu_h": "帮助 / 关于",
        "menu_q": "退出",
        "choice": "请选择",
        "pause": "  按 Enter 继续...",
        "back": "  按 Enter 返回菜单...",
        "enter": "  按 Enter 继续，或输入 s 跳过: ",
        "yes_no": "(y/N): ",
        "cancel": "用户取消",
        "input_end": "输入结束",
        "ok": "✔",
        "fail": "✘",
        "warn": "⚠",
        "info": "·",
        "section": "▶",
        "line": "─",
        "heavy": "═",
        "auto_done": "全自动测试完成",
        "auto_summary": "共 {total} 项，通过 {ok}，失败 {fail}，跳过 {skip}",
        "test_start": "[{n}/{total}] {name}",
        "test_purpose": "目的",
        "test_apis": "涉及 API",
        "test_expect": "期望",
        "test_inputs": "输入",
        "test_manual": "需要用户交互",
        "test_auto": "自动执行",
        "test_ok": "通过",
        "test_fail": "失败",
        "test_skip": "跳过",
        "confirm_run": "要运行这项测试吗？",
        "lang_hdr": "已注册 / 可用语言",
        "lang_cur": "当前",
        "lang_force": "强制",
        "lang_builtin": "内置",
        "lang_external": "外部",
        "lang_runtime": "运行时",
        "lang_meta": "元数据",
        "lang_pick_new": "输入要切换的语言代码（q 取消）",
        "lang_now": "已切换到",
        "lang_alias_hint": "可输入别名: zh-Hans / zh-Hant / ja_JP / kr / C / POSIX ...",
        "no_partition": "未发现分区",
        "part_hdr": "分区列表",
        "no_lg_packs": "(无外部语言包，请运行 gen_lang_packs.py)",
        "no_test_yet": "还没有运行任何测试。",
        "confirm_quit": "确定要退出吗？",
        "help_body": (
            "本 demo 用于验证 cfdialog 库的各项功能。\n"
            "  · 自动测试：只跑不依赖用户输入的项目，适合放到 CI。\n"
            "  · 手动测试：逐项运行，每项都会显示目的和期望，\n"
            "    需要用户配合完成浏览器交互的测试。\n"
            "  · 若 ts.txt 中设置了 force_language，它会覆盖一切语言选择。\n"
            "  · Android 上 su 重启会另开进程，本 demo 默认关闭自动提权。\n"
        ),
        "lg_packs_list": "外部语言包列表",
        "ts_file": "调试配置文件 ts.txt",
        "ts_exists": "存在",
        "ts_missing": "不存在（使用默认值）",
        "debug_config": "调试配置",
        "log_enabled": "log 保存",
        "log_dir_cfg": "log 目录",
        "disabled": "已禁用",
        "enabled": "已启用",
        "write_test_log": "写入一条测试日志？",
        "log_written": "已写入，可查看",
        "log_dir_missing": "log 目录尚不存在，运行库的某些操作后会自动创建",
    },
    "en": {
        "banner": "cfdialog v{ver} usability test",
        "lib_dir": "Library dir",
        "run_dir": "Run dir",
        "work_dir": "Workspace",
        "lib_lang": "Library language",
        "force_lang": "Force language (ts.txt)",
        "no_force": "(none)",
        "platform": "Platform",
        "android": "Android",
        "windows": "Windows",
        "unix": "Unix",
        "lg_packs": "External language packs",
        "lang_pick": "请选择界面语言 / Choose UI language",
        "lang_pick_hint": "1) 中文  2) English",
        "menu_title": "Main menu",
        "menu_1": "Quick auto tests (no interaction)",
        "menu_2": "Manual tests (includes auto; step by step)",
        "menu_3": "Language setup / info",
        "menu_4": "View partitions",
        "menu_5": "Debug info",
        "menu_6": "Reload ts.txt",
        "menu_h": "Help / About",
        "menu_q": "Quit",
        "choice": "Choose",
        "pause": "  Press Enter to continue...",
        "back": "  Press Enter to return to menu...",
        "enter": "  Press Enter to continue, or 's' to skip: ",
        "yes_no": "(y/N): ",
        "cancel": "cancelled by user",
        "input_end": "input ended",
        "ok": "OK ",
        "fail": "ERR",
        "warn": "WRN",
        "info": " ·",
        "section": "▶",
        "line": "─",
        "heavy": "═",
        "auto_done": "Auto tests finished",
        "auto_summary": "{total} tests, {ok} ok, {fail} failed, {skip} skipped",
        "test_start": "[{n}/{total}] {name}",
        "test_purpose": "Purpose",
        "test_apis": "APIs",
        "test_expect": "Expected",
        "test_inputs": "Inputs",
        "test_manual": "requires interaction",
        "test_auto": "runs automatically",
        "test_ok": "PASS",
        "test_fail": "FAIL",
        "test_skip": "SKIP",
        "confirm_run": "Run this test?",
        "lang_hdr": "Registered / available languages",
        "lang_cur": "current",
        "lang_force": "forced",
        "lang_builtin": "builtin",
        "lang_external": "external",
        "lang_runtime": "runtime",
        "lang_meta": "metadata",
        "lang_pick_new": "Enter a language code to switch (q to cancel)",
        "lang_now": "Switched to",
        "lang_alias_hint": "Aliases: zh-Hans / zh-Hant / ja_JP / kr / C / POSIX ...",
        "no_partition": "No partitions found",
        "part_hdr": "Partitions",
        "no_lg_packs": "(no external language packs; run gen_lang_packs.py)",
        "no_test_yet": "No tests run yet.",
        "confirm_quit": "Quit?",
        "help_body": (
            "This demo validates cfdialog.\n"
            "  * Auto tests: no interaction, good for CI.\n"
            "  * Manual tests: step-by-step, each shows purpose and expected.\n"
            "  * If ts.txt has force_language, it overrides all choices.\n"
            "  * On Android su relaunch opens a new process; auto-elevate is off.\n"
        ),
        "lg_packs_list": "External language packs",
        "ts_file": "Debug config ts.txt",
        "ts_exists": "present",
        "ts_missing": "missing (defaults in use)",
        "debug_config": "Debug config",
        "log_enabled": "log saving",
        "log_dir_cfg": "log dir",
        "disabled": "disabled",
        "enabled": "enabled",
        "write_test_log": "Write a test log line?",
        "log_written": "written, check",
        "log_dir_missing": "log dir not yet created; some library ops will create it",
    },
}


def t(key: str, **fmt) -> str:
    s = UI.get(_CTX.ui_lang, UI["en"]).get(key) or UI["en"].get(key, key)
    if fmt:
        try:
            return s.format(**fmt)
        except Exception:
            return s
    return s


# ===========================================================================
# 全局上下文
# ===========================================================================

class Ctx:
    def __init__(self):
        self.ui_lang: str = "zh_CN"
        self.workspace: Optional[Path] = None
        self.run_dir: Path = Path.cwd()
        self.results: dict = {}          # tid -> "ok"/"fail"/"skip"
        self.lib_lang: Optional[str] = None


_CTX = Ctx()


# ===========================================================================
# 输出辅助
# ===========================================================================

def _line(char: str = "─", n: int = 74) -> None:
    print(char * n)


def title(text: str) -> None:
    print()
    _line("═")
    print(f"  {text}")
    _line("═")


def section(text: str) -> None:
    print()
    _line("─")
    print(f"  {t('section')} {text}")
    _line("─")


def ok(text: str) -> None:
    print(f"  {t('ok')} {text}")


def fail(text: str) -> None:
    print(f"  {t('fail')} {text}")


def warn(text: str) -> None:
    print(f"  {t('warn')} {text}")


def info(text: str) -> None:
    print(f"  {t('info')} {text}")


def pause(msg: Optional[str] = None) -> None:
    try:
        input(msg or t("pause"))
    except EOFError:
        pass


def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    try:
        s = input(f"  {prompt}{hint}\n  > ").strip()
    except EOFError:
        return default
    return s if s else default


def ask_yes(prompt: str, default: bool = False) -> bool:
    hint = "(y/N)" if not default else "(Y/n)"
    try:
        s = input(f"  {prompt} {hint}: ").strip().lower()
    except EOFError:
        return False
    if not s:
        return default
    return s in ("y", "yes", "是", "1")


def ask_enter_or_skip() -> str:
    """返回 'go' / 'skip'。"""
    try:
        s = input(t("enter")).strip().lower()
    except EOFError:
        return "skip"
    return "skip" if s in ("s", "skip", "跳过") else "go"


# ===========================================================================
# 工作区
# ===========================================================================

def make_workspace() -> Path:
    ws = Path(tempfile.mkdtemp(prefix="cfdialog_demo_"))
    samples = ws / "samples"
    samples.mkdir()
    (samples / "hello.txt").write_text("Hello from cfdialog demo\n", encoding="utf-8")
    (samples / "notes.md").write_text("# Notes\n\n- item 1\n- item 2\n", encoding="utf-8")
    (samples / "data.csv").write_text("id,name\n1,alice\n2,bob\n", encoding="utf-8")
    (samples / "image.jpg").write_text("not a jpeg\n", encoding="utf-8")
    (samples / "script.py").write_text("print('hi')\n", encoding="utf-8")
    (samples / "archive.tar.gz").write_text("gz\n", encoding="utf-8")
    (samples / ".hidden.txt").write_text("hidden\n", encoding="utf-8")
    sub = samples / "subdir"
    sub.mkdir()
    (sub / "nested.txt").write_text("nested\n", encoding="utf-8")

    (ws / "out").mkdir()
    (ws / "incoming").mkdir()
    return ws


# ===========================================================================
# 测试注册
# ===========================================================================

# 每条: (id, name, auto, func)
# id 用于结果记录
_REGISTRY: List[tuple] = []


def reg(tid: str, name: str, auto: bool):
    def deco(fn):
        _REGISTRY.append((tid, name, auto, fn))
        return fn
    return deco


# ---------------------------------------------------------------------------
# 1) 语言信息
# ---------------------------------------------------------------------------

@reg("T01", "语言信息 / detect / list", True)
def test_lang_info(ctx: Ctx) -> str:
    section("T01 语言信息")
    info(f"detect_language()  = {detect_language()!r}")
    info(f"get_language()     = {get_language()!r}")
    info(f"BUILTIN_LANGUAGES  = {BUILTIN_LANGUAGES}")
    info(f"list_languages()   = {list_languages()}")
    lg_files = sorted(p.stem for p in LG_DIR.glob("*.txt")) if LG_DIR.is_dir() else []
    info(f"lg/*.txt 外部包     = {lg_files or t('no_lg_packs')}")
    ok("完成")
    return "ok"


@reg("T02", "语言切换 / 别名归一化", True)
def test_lang_switch(ctx: Ctx) -> str:
    section("T02 语言切换（含别名归一化）")
    original = get_language()
    cases = [
        ("zh-CN", "zh_CN"), ("zh-Hans", "zh_CN"), ("zh_SG", "zh_CN"),
        ("zh-TW", "zh_TW"), ("zh-Hant", "zh_TW"), ("zh_HK", "zh_TW"),
        ("ja", "ja"), ("ja_JP", "ja"), ("jp", "ja"),
        ("ko", "ko"), ("kr", "ko"),
        ("fr", "fr"), ("fr_CA", "fr"),
        ("ru", "ru"),
        ("es", "es"),
        ("ar", "ar"),
        ("en", "en"), ("en_US", "en"),
        ("C", "en"), ("POSIX", "en"),
        ("", "en"),
    ]
    all_ok = True
    for alias, expected in cases:
        got = set_language(alias)
        same = (got == expected)
        if not same:
            all_ok = False
        mark = t("ok") if same else t("fail")
        print(f"    {mark} set_language({alias!r}) -> {got!r}  (expect {expected!r})")
    set_language(original)
    ok(f"恢复到 {original!r}")
    return "ok" if all_ok else "fail"


@reg("T03", "注册/覆盖/移除自定义语言", True)
def test_lang_register(ctx: Ctx) -> str:
    section("T03 注册 / 覆盖 / 移除自定义语言")
    # 注册
    try:
        code = register_language("de_demo", {
            "prompt_folder": "Ordner auswählen",
            "prompt_file":   "Datei auswählen",
            "prompt_save":   "Speichern unter",
        })
        ok(f"register_language('de_demo', {{...}}) -> {code!r}")
    except Exception as exc:
        fail(f"register 失败: {exc}")
        return "fail"

    # 切换
    got = set_language("de_demo")
    if got == "de_demo":
        ok("set_language('de_demo') 生效")
    else:
        fail(f"set_language 返回 {got!r}")

    # 元数据
    meta = get_language_meta("de_demo")
    info(f"meta: {meta}")

    # 部分覆盖
    try:
        register_language("en", {"prompt_save": "Where to save?"})
        ok("register_language('en', {...}) 覆盖成功")
    except Exception as exc:
        fail(f"覆盖失败: {exc}")

    # 关键字形式
    try:
        register_language("es_demo", prompt_save="Guardar en")
        ok("register_language('es_demo', prompt_save=...) 关键字形式成功")
    except Exception as exc:
        fail(f"关键字注册失败: {exc}")

    # 移除
    try:
        r = unregister_language("de_demo")
        ok(f"unregister_language('de_demo') -> {r}")
    except Exception as exc:
        fail(f"unregister 失败: {exc}")
    try:
        r = unregister_language("es_demo")
        ok(f"unregister_language('es_demo') -> {r}")
    except Exception as exc:
        fail(f"unregister 失败: {exc}")

    # 尝试移除内置
    try:
        unregister_language("en")
        fail("应拒绝移除内置语言")
        return "fail"
    except ValueError as exc:
        ok(f"移除内置被拒绝: {exc}")

    set_language(None)
    return "ok"


@reg("T04", "语言元数据 / 外部包加载", True)
def test_lang_meta(ctx: Ctx) -> str:
    section("T04 语言元数据 + 外部包")
    for code in list_languages():
        meta = get_language_meta(code)
        origin = "builtin" if code in BUILTIN_LANGUAGES else (
            "external" if (LG_DIR / f"{code}.txt").is_file() else "runtime")
        native = meta.get("native_name", code)
        name_en = meta.get("name_en", code)
        print(f"    {code:<8} {native:<14} {name_en:<22} ({origin})")
    ok("完成")
    return "ok"


# ---------------------------------------------------------------------------
# 2) 提权
# ---------------------------------------------------------------------------

@reg("T10", "提权状态（只读）", True)
def test_elevation_info(ctx: Ctx) -> str:
    section("T10 提权状态")
    info(f"is_windows()         = {is_windows()}")
    info(f"is_android()         = {is_android()}")
    info(f"is_elevated()        = {is_elevated()}")
    info(f"has_root_available() = {has_root_available()}")
    ok("完成")
    return "ok"


@reg("T11", "提权开关", True)
def test_elevation_toggle(ctx: Ctx) -> str:
    section("T11 自动提权开关")
    set_auto_elevate(False)
    ok("set_auto_elevate(False)")
    set_auto_elevate(True)
    ok("set_auto_elevate(True)")
    # Android 上建议保持关闭
    if is_android():
        set_auto_elevate(False)
        info("检测到 Android，已再次关闭自动提权（避免 su 重启丢终端）")
    return "ok"


@reg("T12", "手动请求提权（可选）", False)
def test_elevation_manual(ctx: Ctx) -> str:
    section("T12 手动请求提权")
    info("将调用 request_elevation(interactive=True)")
    info("返回 'relaunched' 时新进程会启动，本进程会立即退出")
    if not ask_yes("确认请求提权？", False):
        info("已跳过")
        return "skip"

    # 使用一个可控的 ask，避免 Windows 上弹 UAC
    status = request_elevation(interactive=True,
                               ask=lambda q: ask_yes(q, False))
    print(f"    request_elevation() -> {status!r}")
    if status == "relaunched":
        info("提权进程已启动，本进程退出。")
        sys.exit(0)
    ok("完成")
    return "ok"


# ---------------------------------------------------------------------------
# 3) 分区
# ---------------------------------------------------------------------------

@reg("T20", "列出分区", True)
def test_partitions_list(ctx: Ctx) -> str:
    section("T20 分区列举")
    parts = list_partitions()
    if not parts:
        warn(t("no_partition"))
        return "skip"
    for p in parts:
        label = p.get("label", "")
        typ = p.get("type", "")
        extra = f"  ({label} {typ})".rstrip()
        print(f"    {p['name']:<28}{extra}")
        print(f"    {'':<28}{p['path']}")
    ok(f"共 {len(parts)} 个分区")
    return "ok"


@reg("T21", "进入分区选择器（手动）", False)
def test_partitions_browse(ctx: Ctx) -> str:
    section("T21 分区选择器")
    info("将打开文件夹选择器，你可以按 'g' 切换分区")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        d = pick_folder(start_dir=ctx.workspace, prompt="按 g 切换分区")
        if d:
            ok(f"选中: {d}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


# ---------------------------------------------------------------------------
# 4) 选择器
# ---------------------------------------------------------------------------

@reg("T30", "pick_file: path 模式，单选", False)
def test_pick_file_path_single(ctx: Ctx) -> str:
    section("T30 pick_file(mode='path')  单选")
    info("返回选中文件的 Path，不会复制")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        p = pick_file(mode="path", start_dir=ctx.workspace / "samples")
        if p:
            ok(f"选中: {p}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T31", "pick_file: path 模式，多选", False)
def test_pick_file_path_multi(ctx: Ctx) -> str:
    section("T31 pick_file(mode='path', multiple=True)")
    info("多选按键: 数字=切换选中, a=全选, c=清空, d=完成")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        ps = pick_file(mode="path", multiple=True,
                       start_dir=ctx.workspace / "samples")
        ok(f"共 {len(ps)} 个:")
        for p in ps:
            print(f"    - {p}")
        return "ok"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T32", "pick_file: copy 模式，单选", False)
def test_pick_file_copy_single(ctx: Ctx) -> str:
    section("T32 pick_file(mode='copy')  单选")
    info(f"选中文件会复制到 {ctx.workspace / 'incoming'}")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        p = pick_file(mode="copy",
                      start_dir=ctx.workspace / "samples",
                      work_dir=ctx.workspace / "incoming")
        if p:
            exists = Path(p).exists()
            ok(f"副本: {p}  (存在: {exists})")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T33", "pick_file: copy 模式，多选", False)
def test_pick_file_copy_multi(ctx: Ctx) -> str:
    section("T33 pick_file(mode='copy', multiple=True)")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        ps = pick_file(mode="copy", multiple=True,
                       start_dir=ctx.workspace / "samples",
                       work_dir=ctx.workspace / "incoming")
        ok(f"共 {len(ps)} 个副本:")
        for p in ps:
            print(f"    - {p}")
        return "ok"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T34", "pick_file: 单个后缀", False)
def test_pick_file_ext_single(ctx: Ctx) -> str:
    section("T34 pick_file(extensions='.txt')")
    info("只会显示 .txt 文件；目录始终可见用于导航")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        p = pick_file(mode="path", start_dir=ctx.workspace / "samples",
                      extensions=".txt")
        if p:
            ok(f"选中: {p}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T35", "pick_file: 多个后缀", False)
def test_pick_file_ext_multi(ctx: Ctx) -> str:
    section("T35 pick_file(extensions=['.md', '.csv', '.py'])")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        p = pick_file(mode="path", start_dir=ctx.workspace / "samples",
                      extensions=[".md", ".csv", ".py"])
        if p:
            ok(f"选中: {p}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T36", "pick_file: 单次调用指定语言", False)
def test_pick_file_lang(ctx: Ctx) -> str:
    section("T36 pick_file(lang='ja')")
    info("本次调用临时使用日语，不影响全局语言")
    info("提示: 若 ts.txt 里设置了 force_language，本项会被覆盖")
    if ask_enter_or_skip() == "skip":
        return "skip"
    before = get_language()
    try:
        p = pick_file(mode="path", start_dir=ctx.workspace / "samples",
                      lang="ja")
        after = get_language()
        if before == after:
            ok(f"全局语言不变: {before!r}")
        else:
            fail(f"全局语言被改: {before!r} -> {after!r}")
        if p:
            ok(f"选中: {p}")
        return "ok"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T37", "pick_folder: 单选", False)
def test_pick_folder_single(ctx: Ctx) -> str:
    section("T37 pick_folder()  单选")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        d = pick_folder(start_dir=ctx.workspace)
        if d:
            ok(f"选中: {d}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T38", "pick_folder: 多选", False)
def test_pick_folder_multi(ctx: Ctx) -> str:
    section("T38 pick_folder(multiple=True)")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        ds = pick_folder(multiple=True, start_dir=ctx.workspace)
        ok(f"共 {len(ds)} 个:")
        for d in ds:
            print(f"    - {d}")
        return "ok"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T39", "pick: select='any'", False)
def test_pick_any(ctx: Ctx) -> str:
    section("T39 pick(select='any')")
    info("文件或文件夹都可以选")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        p = pick(select="any", mode="path",
                 start_dir=ctx.workspace / "samples")
        if p:
            ok(f"选中: {p}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


# ---------------------------------------------------------------------------
# 5) 保存器
# ---------------------------------------------------------------------------

@reg("T50", "save: mode='path' 只给目录", False)
def test_save_path(ctx: Ctx) -> str:
    section("T50 save(mode='path')")
    info("只返回用户选的目录，由调用方自己写文件")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        d = save(target_dir=None, mode="path", start_dir=ctx.workspace)
        if not d:
            return "skip"
        f = d / "demo_output.txt"
        try:
            f.write_text("written by demo save() test\n", encoding="utf-8")
            ok(f"写入 {f}")
        except Exception as exc:
            warn(f"无法写入 {f}: {exc}")
        return "ok"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T51", "save: mode='copy' 复制到目标目录", False)
def test_save_copy(ctx: Ctx) -> str:
    section("T51 save(mode='copy')")
    src = ctx.workspace / "samples" / "hello.txt"
    info(f"源: {src}")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        out = save(sources=src, mode="copy", start_dir=ctx.workspace)
        if out:
            ok(f"已保存: {out}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T52", "save: 批量复制", False)
def test_save_copy_multi(ctx: Ctx) -> str:
    section("T52 save(multiple sources, mode='copy')")
    files = [
        ctx.workspace / "samples" / "hello.txt",
        ctx.workspace / "samples" / "notes.md",
        ctx.workspace / "samples" / "data.csv",
    ]
    info(f"源文件: {[f.name for f in files]}")
    if ask_enter_or_skip() == "skip":
        return "skip"

    def progress(i, total, src):
        print(f"    [{i}/{total}] {src.name}")

    try:
        outs = save(sources=files, mode="copy", start_dir=ctx.workspace,
                    on_progress=progress)
        ok(f"共 {len(outs)} 个:")
        for o in outs:
            print(f"    - {o}")
        return "ok"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T53", "save: free_name 自定义文件名", False)
def test_save_free_name(ctx: Ctx) -> str:
    section("T53 save(free_name=True)")
    src = ctx.workspace / "samples" / "hello.txt"
    info("选完目标目录后，会提示输入新文件名（留空用默认）")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        out = save(sources=src, mode="copy", free_name=True,
                   default_name="renamed_by_demo.txt",
                   start_dir=ctx.workspace)
        if out:
            ok(f"目标: {out}")
            ok(f"文件已存在: {out.exists()}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T54", "save: target_dir 已给出（不弹窗）", True)
def test_save_with_target(ctx: Ctx) -> str:
    section("T54 save(target_dir=...)  不弹窗")
    src = ctx.workspace / "samples" / "hello.txt"
    target = ctx.workspace / "out"
    try:
        out = save(sources=src, target_dir=target, mode="copy",
                   overwrite=False)
        ok(f"直接复制到 {out}")
        if out.exists():
            ok("文件存在")
            return "ok"
        fail("文件未生成")
        return "fail"
    except Exception as exc:
        fail(f"异常: {exc}")
        return "fail"


@reg("T55", "save_folder: 便捷包装", False)
def test_save_folder(ctx: Ctx) -> str:
    section("T55 save_folder()")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        d = save_folder(start_dir=ctx.workspace)
        if d:
            ok(f"选中: {d}")
            return "ok"
        return "skip"
    except BrowserCancelled as exc:
        warn(f"取消: {exc}")
        return "skip"


@reg("T56", "save: 源不存在应抛 FileNotFoundError", True)
def test_save_missing_source(ctx: Ctx) -> str:
    section("T56 源不存在异常")
    try:
        save(sources="this_does_not_exist_12345.txt",
             target_dir=ctx.workspace / "out", mode="copy")
        fail("没有抛异常")
        return "fail"
    except FileNotFoundError as exc:
        ok(f"FileNotFoundError: {exc}")
        return "ok"
    except Exception as exc:
        fail(f"异常类型错误: {type(exc).__name__}: {exc}")
        return "fail"


# ---------------------------------------------------------------------------
# 6) 文件管理器
# ---------------------------------------------------------------------------

@reg("T60", "file_manager: readonly", False)
def test_file_manager_ro(ctx: Ctx) -> str:
    section("T60 文件管理器 只读")
    info("只读模式禁用 rm / ct / ps / rn / at")
    info("允许: 导航、sa/sc、cp、op、info、ls、g 切分区")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        file_manager(start_dir=ctx.workspace / "samples",
                     access="readonly")
        ok("退出文件管理器")
        return "ok"
    except Exception as exc:
        fail(f"异常: {type(exc).__name__}: {exc}")
        return "fail"


@reg("T61", "file_manager: readwrite", False)
def test_file_manager_rw(ctx: Ctx) -> str:
    section("T61 文件管理器 读写")
    info("所有操作可用: rm / cp / ct / ps / rn / op / at")
    if ask_enter_or_skip() == "skip":
        return "skip"
    try:
        file_manager(start_dir=ctx.workspace / "samples",
                     access="readwrite")
        ok("退出文件管理器")
        return "ok"
    except Exception as exc:
        fail(f"异常: {type(exc).__name__}: {exc}")
        return "fail"


# ---------------------------------------------------------------------------
# 7) 工具函数
# ---------------------------------------------------------------------------

@reg("T70", "copy_into: 复制 / 改名 / 覆盖", True)
def test_copy_into(ctx: Ctx) -> str:
    section("T70 copy_into")
    src = ctx.workspace / "samples" / "hello.txt"
    dst = ctx.workspace / "copy_test"
    dst.mkdir(exist_ok=True)
    try:
        r1 = copy_into(src, dst, overwrite=False)
        ok(f"第一次: {r1.name}")
        r2 = copy_into(src, dst, overwrite=False)
        ok(f"自动改名: {r2.name}")
        r3 = copy_into(src, dst, overwrite=True)
        ok(f"覆盖: {r3.name}")
        r4 = copy_into(ctx.workspace / "samples" / "subdir", dst)
        ok(f"目录复制: {r4.name} (is_dir={r4.is_dir()})")
        return "ok"
    except Exception as exc:
        fail(f"异常: {exc}")
        return "fail"


@reg("T71", "扩展名归一化", True)
def test_ext_norm(ctx: Ctx) -> str:
    section("T71 _normalize_extensions 边界")
    from cfdialog import _normalize_extensions  # type: ignore
    cases = [
        (None, None), ("*", None), ("*.*", None), ("", None), ([], None),
        (".txt", frozenset({".txt"})),
        ("txt", frozenset({".txt"})),
        ("*.txt", frozenset({".txt"})),
        ([".md", "CSV", "*.py"], frozenset({".md", ".csv", ".py"})),
        (["*"], None),
    ]
    all_ok = True
    for inp, exp in cases:
        got = _normalize_extensions(inp)
        same = (got == exp)
        if not same:
            all_ok = False
        mark = t("ok") if same else t("fail")
        print(f"    {mark} {inp!r:<30} -> {got}")
    return "ok" if all_ok else "fail"


@reg("T72", "异常: 非法 select 抛 ValueError", True)
def test_invalid_select(ctx: Ctx) -> str:
    section("T72 非法 select")
    from cfdialog import _browse  # type: ignore
    try:
        _browse(select="invalid")
        fail("未抛异常")
        return "fail"
    except ValueError as exc:
        ok(f"ValueError: {exc}")
        return "ok"
    except BrowserCancelled:
        fail("异常类型不对")
        return "fail"


@reg("T73", "异常: register_language 参数校验", True)
def test_invalid_register(ctx: Ctx) -> str:
    section("T73 register_language 参数校验")
    all_ok = True
    try:
        register_language("")
        fail("空 code 应报错")
        all_ok = False
    except ValueError as exc:
        ok(f"空 code -> ValueError: {exc}")

    try:
        register_language("zz_demo", strings=["not", "a", "dict"])
        fail("非 dict 应报错")
        all_ok = False
    except TypeError as exc:
        ok(f"非 dict -> TypeError: {exc}")
    finally:
        try:
            unregister_language("zz_demo")
        except Exception:
            pass

    try:
        unregister_language("en")
        fail("移除内置应被拒")
        all_ok = False
    except ValueError as exc:
        ok(f"移除内置 -> ValueError: {exc}")

    return "ok" if all_ok else "fail"


# ---------------------------------------------------------------------------
# 8) 调试 / 语言包
# ---------------------------------------------------------------------------

@reg("T80", "读取调试配置 ts.txt", True)
def test_debug_config(ctx: Ctx) -> str:
    section("T80 ts.txt 调试配置")
    reload_debug_config()
    cfg = get_debug_config()
    info(f"ts.txt 位置: {TS_FILE}")
    info(f"存在: {TS_FILE.is_file()}")
    info(f"log: {cfg.get('log')}")
    info(f"log_dir: {cfg.get('log_dir')}")
    info(f"force_language: {cfg.get('force_language')}")
    return "ok"


@reg("T81", "写入测试 log", True)
def test_debug_log(ctx: Ctx) -> str:
    section("T81 写入一条测试 log")
    cfg = get_debug_config()
    if not cfg.get("log"):
        warn("ts.txt 里 log=false，跳过写入")
        return "skip"
    try:
        # 触发一次会被 log 的行为
        set_language(get_language())
        ok("已调用 set_language，检查 log 目录")
        log_dir = LIB_DIR / (cfg.get("log_dir") or "log")
        if log_dir.is_dir():
            logs = sorted(log_dir.glob("*.txt"))
            for f in logs[-3:]:
                info(f"{f}")
        else:
            info(t("log_dir_missing"))
        return "ok"
    except Exception as exc:
        fail(f"异常: {exc}")
        return "fail"


@reg("T82", "language pack 目录检查", True)
def test_lg_dir(ctx: Ctx) -> str:
    section("T82 语言包目录")
    info(f"LG_DIR = {LG_DIR}")
    if not LG_DIR.is_dir():
        warn("目录不存在（首次运行会创建）")
        return "skip"
    files = sorted(LG_DIR.glob("*.txt"))
    if not files:
        warn(t("no_lg_packs"))
        return "skip"
    for f in files:
        size = f.stat().st_size
        info(f"{f.name}  ({size} bytes)")
    ok(f"共 {len(files)} 个语言包")
    return "ok"


# ===========================================================================
# 运行框架
# ===========================================================================

def _needs_input(fn: Callable) -> bool:
    """根据注册表的 auto 标志判断。"""
    return False  # 由 _REGISTRY 决定


def find_by_id(tid: str):
    for t_ in _REGISTRY:
        if t_[0] == tid:
            return t_
    return None


def run_test(tid: str, manual_ok: bool = False) -> str:
    entry = find_by_id(tid)
    if not entry:
        return "skip"
    _, name, auto, fn = entry
    print()
    _line("═")
    print(f"  {tid}  {name}")
    _line("═")

    if not auto and not manual_ok:
        print(f"  [automatic mode] {t('test_skip')}")
        return "skip"

    try:
        result = fn(_CTX)
        if result is None:
            result = "ok"
    except BrowserCancelled as exc:
        warn(f"{t('cancel')}: {exc}")
        result = "skip"
    except KeyboardInterrupt:
        warn("Interrupted")
        result = "skip"
    except Exception as exc:
        fail(f"{type(exc).__name__}: {exc}")
        import traceback
        traceback.print_exc()
        result = "fail"

    _CTX.results[tid] = result
    return result


def run_auto_tests() -> None:
    title("全自动测试 / AUTO TESTS")
    total = len(_REGISTRY)
    counts = {"ok": 0, "fail": 0, "skip": 0}
    for i, (tid, name, auto, fn) in enumerate(_REGISTRY, 1):
        if not auto:
            print()
            _line("─")
            print(f"  [{i}/{total}] {tid} {name}   (skip: needs interaction)")
            counts["skip"] += 1
            _CTX.results[tid] = "skip"
            continue

        print()
        _line("─")
        print(f"  [{i}/{total}] {tid} {name}")

        try:
            r = fn(_CTX)
            if r is None:
                r = "ok"
        except KeyboardInterrupt:
            print()
            print("Interrupted by user.")
            break
        except Exception as exc:
            fail(f"{type(exc).__name__}: {exc}")
            r = "fail"

        counts[r] = counts.get(r, 0) + 1
        _CTX.results[tid] = r

    title("AUTO 测试结果")
    print("  " + t("auto_summary",
                   total=total, ok=counts["ok"],
                   fail=counts["fail"], skip=counts["skip"]))
    for tid, name, auto, fn in _REGISTRY:
        r = _CTX.results.get(tid, "-")
        mark = {"ok": t("ok"), "fail": t("fail"), "skip": t("skip")}.get(r, r)
        print(f"    {mark:<6} {tid}  {name}")


def run_manual_tests() -> None:
    title("手动测试 / MANUAL TESTS")
    total = len(_REGISTRY)
    for i, (tid, name, auto, fn) in enumerate(_REGISTRY, 1):
        print()
        _line("─")
        print(f"  [{i}/{total}] {tid}  {name}  "
              f"({'auto' if auto else 'manual'})")
        _line("─")

        if not auto:
            if ask_enter_or_skip() == "skip":
                _CTX.results[tid] = "skip"
                continue

        try:
            r = fn(_CTX)
            if r is None:
                r = "ok"
        except KeyboardInterrupt:
            print()
            print("Interrupted by user.")
            break
        except Exception as exc:
            fail(f"{type(exc).__name__}: {exc}")
            r = "fail"
        _CTX.results[tid] = r

    title("手动测试结果")
    counts = {"ok": 0, "fail": 0, "skip": 0}
    for tid, name, auto, fn in _REGISTRY:
        r = _CTX.results.get(tid, "-")
        counts[r] = counts.get(r, 0) + (1 if r in counts else 0)
        mark = {"ok": t("ok"), "fail": t("fail"), "skip": t("skip")}.get(r, r)
        print(f"    {mark:<6} {tid}  {name}")
    print()
    print("  " + t("auto_summary",
                   total=total, ok=counts["ok"],
                   fail=counts["fail"], skip=counts["skip"]))


# ===========================================================================
# 语言设置菜单
# ===========================================================================

def menu_language() -> None:
    title("语言设置 / Language setup")
    cur = get_language()
    cfg = get_debug_config()
    force = cfg.get("force_language") or t("no_force")

    print(f"  {t('lib_lang')}: {cur!r}")
    print(f"  {t('force_lang')}: {force!r}")
    if cfg.get("force_language"):
        warn("当前 ts.txt 强制了语言，切换无效（除非修改 ts.txt）")

    print()
    print(f"  {t('lang_hdr')}:")
    for code in list_languages():
        meta = get_language_meta(code)
        marker = " *" if code == cur else "  "
        origin = t("lang_builtin") if code in BUILTIN_LANGUAGES else \
                 (t("lang_external") if (LG_DIR / f"{code}.txt").is_file()
                  else t("lang_runtime"))
        native = meta.get("native_name") or code
        name_en = meta.get("name_en") or ""
        print(f"    {marker} {code:<10} {native:<16} {name_en:<24} ({origin})")

    print()
    info(t("lang_alias_hint"))
    raw = ask(t("lang_pick_new"), "")
    if not raw or raw.lower() in ("q", "quit"):
        return

    got = set_language(raw)
    ok(f"{t('lang_now')} {got!r}")

    # 展示一下新语言的提示
    print()
    print(f"  示例提示: {cfdialog._t('prompt_folder', lang=got)!r}")


def menu_partitions() -> None:
    title(t("part_hdr"))
    parts = list_partitions()
    if not parts:
        warn(t("no_partition"))
        return
    for i, p in enumerate(parts, 1):
        label = p.get("label", "")
        typ = p.get("type", "")
        extra = " ".join(x for x in (label, typ) if x)
        print(f"  {i:>3})  {p['name']:<28}{extra}")
        print(f"        {p['path']}")


def menu_debug() -> None:
    title(t("debug_config"))
    reload_debug_config()
    cfg = get_debug_config()
    print(f"  ts.txt: {TS_FILE}")
    print(f"  {t('ts_exists') if TS_FILE.is_file() else t('ts_missing')}")
    print()
    print(f"  log            : {cfg.get('log')}")
    print(f"  log_dir        : {cfg.get('log_dir')}")
    print(f"  force_language : {cfg.get('force_language')}")
    print()
    print(f"  LIB_DIR = {LIB_DIR}")
    print(f"  LG_DIR  = {LG_DIR}")
    print(f"  LOG_DIR = {LOG_DIR}")
    if LOG_DIR.is_dir():
        logs = sorted(LOG_DIR.glob("*.txt"))
        print(f"  log files: {[f.name for f in logs[-5:]]}")


def menu_help() -> None:
    title(t("menu_h"))
    print(t("help_body"))


# ===========================================================================
# 主菜单
# ===========================================================================

def _print_banner() -> None:
    title(t("banner", ver=cfdialog.__dict__.get("__version__", "0.3.0")))
    print(f"  {t('lib_dir')}: {LIB_DIR}")
    print(f"  {t('run_dir')}: {_CTX.run_dir}")
    print(f"  {t('work_dir')}: {_CTX.workspace}")
    print(f"  {t('lib_lang')}: {get_language()!r}")
    cfg = get_debug_config()
    force = cfg.get("force_language") or t("no_force")
    print(f"  {t('force_lang')}: {force!r}")
    if is_android():
        print(f"  {t('platform')}: {t('android')}")
    elif is_windows():
        print(f"  {t('platform')}: {t('windows')}")
    else:
        print(f"  {t('platform')}: {t('unix')}")

    lg_count = len(list(LG_DIR.glob("*.txt"))) if LG_DIR.is_dir() else 0
    print(f"  {t('lg_packs')}: {lg_count}")


def run_menu() -> None:
    while True:
        _print_banner()
        print()
        _line("═")
        print(f"  {t('menu_title')}")
        _line("═")
        print(f"    1) {t('menu_1')}")
        print(f"    2) {t('menu_2')}")
        print(f"    3) {t('menu_3')}")
        print(f"    4) {t('menu_4')}")
        print(f"    5) {t('menu_5')}")
        print(f"    6) {t('menu_6')}")
        print(f"    h) {t('menu_h')}")
        print(f"    q) {t('menu_q')}")
        print()
        try:
            choice = input(f"  {t('choice')} > ").strip().lower()
        except EOFError:
            return

        if choice in ("q", "quit", "exit"):
            if ask_yes(t("confirm_quit"), True):
                return
            continue

        if choice == "1":
            run_auto_tests()
            pause(t("back"))
        elif choice == "2":
            run_manual_tests()
            pause(t("back"))
        elif choice == "3":
            menu_language()
            pause(t("back"))
        elif choice == "4":
            menu_partitions()
            pause(t("back"))
        elif choice == "5":
            menu_debug()
            pause(t("back"))
        elif choice == "6":
            reload_debug_config()
            ok("已重新加载 ts.txt")
            pause(t("back"))
        elif choice == "h":
            menu_help()
            pause(t("back"))
        else:
            warn("Invalid choice / 无效选择")


# ===========================================================================
# 入口
# ===========================================================================

def parse_args(argv: List[str]):
    parser = argparse.ArgumentParser(description="cfdialog usability test")
    parser.add_argument("--auto", action="store_true",
                        help="直接运行全自动测试")
    parser.add_argument("--ui", choices=("zh_CN", "en", "zh", "cn"),
                        default=None, help="界面语言")
    parser.add_argument("--lang", default=None,
                        help="启动时将库切换到指定语言")
    parser.add_argument("--list-langs", action="store_true",
                        help="列出可用语言后退出")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    # ---- UI 语言选择 ----
    if args.ui:
        _CTX.ui_lang = "zh_CN" if args.ui in ("zh_CN", "zh", "cn") else "en"
    else:
        # 自动匹配系统语言
        try:
            sys_lang = (os.environ.get("LC_ALL")
                        or os.environ.get("LC_MESSAGES")
                        or os.environ.get("LANG") or "")
            _CTX.ui_lang = "zh_CN" if sys_lang.lower().startswith("zh") else "en"
        except Exception:
            _CTX.ui_lang = "zh_CN"

    # ---- list-langs ----
    if args.list_langs:
        print("Available languages:")
        for code in list_languages():
            meta = get_language_meta(code)
            print(f"  {code:<10} {meta.get('native_name', code)}")
        return 0

    # ---- 强制库语言 ----
    if args.lang:
        got = set_language(args.lang)
        print(f"Library language set to: {got!r}")

    # ---- Android 上安全优先 ----
    if is_android():
        set_auto_elevate(False)

    # ---- 准备工作区 ----
    _CTX.workspace = make_workspace()
    _CTX.run_dir = Path.cwd()

    # ---- 首次进入时给一次语言选择机会 ----
    if not args.ui and sys.stdin.isatty():
        print()
        _line("═")
        print(f"  {t('lang_pick')}")
        print(f"  {t('lang_pick_hint')}")
        _line("═")
        try:
            c = input("  > ").strip()
        except EOFError:
            c = "1"
        _CTX.ui_lang = "zh_CN" if c in ("1", "zh", "zh_CN", "中文", "") else "en"

    try:
        if args.auto:
            run_auto_tests()
        else:
            run_menu()
    finally:
        # ---- 清理 ----
        try:
            if _CTX.workspace and _CTX.workspace.is_dir():
                shutil.rmtree(_CTX.workspace, ignore_errors=True)
        except Exception:
            pass

    print()
    print("Goodbye / 再见")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)