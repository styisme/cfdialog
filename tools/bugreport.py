#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/bugreport.py — 收集 cfdialog 运行环境，生成可粘贴到 GitHub Issue 的 markdown。

用法：
    python tools/bugreport.py
    python tools/bugreport.py --no-log        # 不读 log/ 目录
    python tools/bugreport.py --out bug.txt   # 写到文件（默认 stdout）

注意：
    - 输出可能包含本地路径。贴到 issue 前请先审阅。
    - 只读，不会修改任何文件。
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _safe(fn, default="n/a"):
    try:
        return fn()
    except Exception as exc:
        return f"<error: {type(exc).__name__}: {exc}>"


def collect(args) -> str:
    lines = []
    add = lines.append

    add("# cfdialog bug report")
    add("")
    add(f"- generated: {time.strftime('%Y-%m-%d %H:%M:%S %z')}")

    # ---- 系统 ----
    add("")
    add("## System")
    add("")
    add(f"- platform : {platform.platform()}")
    add(f"- python   : {sys.version.split()[0]}")
    add(f"- exe      : {sys.executable}")
    add(f"- cwd      : {Path.cwd()}")
    add(f"- repo root: {ROOT}")

    # 终端环境特征
    markers = []
    if os.environ.get("TERMUX_VERSION"):
        markers.append(f"Termux {os.environ['TERMUX_VERSION']}")
    if "pydroid" in sys.executable.lower() or os.environ.get("PYDROID"):
        markers.append("Pydroid 3")
    if os.environ.get("SSH_CONNECTION"):
        markers.append("SSH session")
    if os.environ.get("TERM"):
        markers.append(f"TERM={os.environ['TERM']}")
    if markers:
        add(f"- terminal : {', '.join(markers)}")

    # ---- cfdialog ----
    add("")
    add("## cfdialog")
    add("")
    try:
        import cfdialog
    except Exception as exc:
        add(f"- **import failed**: {type(exc).__name__}: {exc}")
        return "\n".join(lines) + "\n"

    add(f"- LIB_DIR : {_safe(lambda: cfdialog.LIB_DIR)}")
    add(f"- LG_DIR  : {_safe(lambda: cfdialog.LG_DIR)}")
    add(f"- TS_FILE : {_safe(lambda: cfdialog.TS_FILE)}")
    add("")

    add("### Platform flags")
    add("")
    for name in ("is_windows", "is_android", "is_elevated", "has_root_available"):
        fn = getattr(cfdialog, name, None)
        add(f"- {name:22} = {_safe(fn) if fn else 'n/a'}")
    add(f"- auto_elevate           = {_safe(lambda: cfdialog._AUTO_ELEVATE, 'n/a')}")

    add("")
    add("### Language")
    add("")
    add(f"- get_language()    = {_safe(cfdialog.get_language)!r}")
    add(f"- detect_language() = {_safe(cfdialog.detect_language)!r}")
    add(f"- list_languages()  = {_safe(cfdialog.list_languages)}")
    add(f"- BUILTIN           = {_safe(lambda: cfdialog.BUILTIN_LANGUAGES)}")
    add(f"- SUPPORTED         = {_safe(lambda: cfdialog.SUPPORTED_LANGUAGES)}")

    add("")
    add("### Debug config (ts.txt)")
    add("")
    cfg = _safe(cfdialog.get_debug_config, {})
    add(f"- cfg = {cfg}")

    ts = ROOT / "ts.txt"
    if ts.is_file():
        add("")
        add("```ini")
        try:
            add(ts.read_text(encoding="utf-8").rstrip())
        except Exception as exc:
            add(f"<error: {exc}>")
        add("```")

    # ---- lg 目录 ----
    add("")
    add("## Language packs (lg/)")
    add("")
    try:
        lg = ROOT / "lg"
        files = sorted(p.name for p in lg.glob("*.txt")) if lg.is_dir() else []
        add(f"- files: {files if files else '(none)'}")
    except Exception as exc:
        add(f"- <error: {exc}>")

    # ---- demo --list-langs ----
    add("")
    add("## demo --list-langs")
    add("")
    demo = ROOT / "tools" / "demo.py"
    if demo.is_file():
        try:
            r = subprocess.run(
                [sys.executable, str(demo), "--list-langs"],
                cwd=str(ROOT), capture_output=True, text=True, timeout=30,
            )
            add("```")
            add((r.stdout or r.stderr).rstrip())
            add(f"# rc = {r.returncode}")
            add("```")
        except Exception as exc:
            add(f"<error: {exc}>")
    else:
        add("- tools/demo.py not found")

    # ---- log ----
    if not args.no_log:
        add("")
        add("## Recent log")
        add("")
        log_dir = ROOT / (cfg.get("log_dir") or "log") if isinstance(cfg, dict) else ROOT / "log"
        if not log_dir.is_dir():
            add(f"- {log_dir} does not exist")
        else:
            files = sorted(log_dir.glob("*.txt"))
            if not files:
                add(f"- {log_dir} has no *.txt")
            else:
                latest = files[-1]
                add(f"- showing tail of `{latest.name}` (review before pasting)")
                add("")
                add("```")
                try:
                    text = latest.read_text(encoding="utf-8", errors="replace")
                    tail = text.rstrip().splitlines()[-40:]
                    add("\n".join(tail))
                except Exception as exc:
                    add(f"<error: {exc}>")
                add("```")

    # ---- unittest（可选，快速） ----
    if not args.no_tests:
        add("")
        add("## Unittest")
        add("")
        try:
            r = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                cwd=str(ROOT), capture_output=True, text=True, timeout=120,
            )
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            add("```")
            add("\n".join(tail))
            add(f"# rc = {r.returncode}")
            add("```")
        except Exception as exc:
            add(f"<error: {exc}>")

    add("")
    add("---")
    add("_Generated by tools/bugreport.py_")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Collect cfdialog environment info.")
    ap.add_argument("--no-log", action="store_true", help="skip log/ tail")
    ap.add_argument("--no-tests", action="store_true", help="skip unittest run")
    ap.add_argument("--out", default=None, help="write to file instead of stdout")
    args = ap.parse_args(argv)

    text = collect(args)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"written: {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
