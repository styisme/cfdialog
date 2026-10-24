#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cfdialog — 单文件跨平台 CLI 文件对话框库 v0.3.0

新增 (相比 v0.2):
    * 语言包外置：核心只内置 zh_CN / en，其他语言放 lg/*.txt
    * 调试开关 ts.txt：log 保存 / 强制语言
    * 直接运行本文件 -> 打开文件管理器（读写模式）

API 速览:
    pick_file / pick_folder / pick / save / save_folder / file_manager
    list_partitions / request_elevation / set_auto_elevate
    get_language / set_language / detect_language
    register_language / unregister_language / list_languages
    copy_into / BrowserCancelled
"""

from __future__ import annotations

import ctypes
import os
import platform
import shlex
import shutil
import stat as _stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple, Union

__all__ = [
    "BrowserCancelled",
    "request_elevation", "is_elevated", "is_windows", "is_android",
    "has_root_available", "set_auto_elevate",
    "pick", "pick_file", "pick_folder",
    "save", "save_folder",
    "file_manager",
    "list_partitions",
    "copy_into",
    "get_language", "set_language", "detect_language",
    "register_language", "unregister_language", "list_languages",
    "get_language_meta",
    "reload_debug_config", "get_debug_config",
    "SUPPORTED_LANGUAGES", "BUILTIN_LANGUAGES",
    "LIB_DIR", "LG_DIR", "LOG_DIR", "TS_FILE",
]

PathLike = Union[str, Path]

# =========================================================================== #
#                             常量与路径                                       #
# =========================================================================== #

_IS_WINDOWS = platform.system() == "Windows"
_IS_ANDROID = bool(
    os.environ.get("ANDROID_ROOT")
    or os.environ.get("ANDROID_DATA")
    or os.environ.get("ANDROID_STORAGE")
)

LIB_DIR: Path = Path(__file__).resolve().parent
LG_DIR: Path = LIB_DIR / "lg"
LOG_DIR: Path = LIB_DIR / "log"
TS_FILE: Path = LIB_DIR / "ts.txt"

_DEFAULT_LANG = "en"
BUILTIN_LANGUAGES = ("zh_CN", "en")
SUPPORTED_LANGUAGES = ("zh_CN", "zh_TW", "en", "ja", "ko", "ru", "fr", "es", "ar")

# 首次运行时确保目录存在
try:
    LG_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


# =========================================================================== #
#                              异常                                           #
# =========================================================================== #

class BrowserCancelled(Exception):
    """用户在 CLI 浏览器里取消了操作。"""
    pass


# =========================================================================== #
#                              调试系统                                       #
# =========================================================================== #

_DEBUG = {
    "log": False,
    "log_dir": "log",
    "force_language": None,
}


def reload_debug_config() -> dict:
    """
    重新读取库目录下的 ts.txt。

    ts.txt 格式（# 后为注释；行内 # 之后也被忽略）:
        log=true                    开启 log 保存
        log_dir=log                 可选，log 目录（相对库目录）
        force_language=zh_CN        可选，强制语言代码；none 或空表示不强制
    """
    global _DEBUG
    _DEBUG = {"log": False, "log_dir": "log", "force_language": None}

    if not TS_FILE.is_file():
        return dict(_DEBUG)

    try:
        text = TS_FILE.read_text(encoding="utf-8")
    except Exception:
        return dict(_DEBUG)

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().lower()
        v = v.strip()
        if k == "log":
            _DEBUG["log"] = v.lower() in ("1", "true", "yes", "on", "y", "开", "是")
        elif k == "log_dir":
            _DEBUG["log_dir"] = v or "log"
        elif k == "force_language":
            _DEBUG["force_language"] = v if v and v.lower() != "none" else None

    return dict(_DEBUG)


def get_debug_config() -> dict:
    """返回当前调试配置的副本。"""
    return dict(_DEBUG)


def _debug_log(msg: str) -> None:
    if not _DEBUG.get("log"):
        return
    try:
        d = LIB_DIR / (_DEBUG.get("log_dir") or "log")
        d.mkdir(parents=True, exist_ok=True)
        fname = d / (time.strftime("%Y%m%d") + ".txt")
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(fname, "a", encoding="utf-8") as fp:
            fp.write(f"[{stamp}] {msg}\n")
    except Exception:
        pass


# 首次 import 时加载调试配置
reload_debug_config()
_debug_log("cfdialog loaded")


# =========================================================================== #
#                              内置语言包                                     #
# =========================================================================== #

_BUILTIN_STRINGS = {
    "en": {
        "prompt_folder": "Select a folder",
        "prompt_file": "Select a file",
        "prompt_any": "Select a file or folder",
        "prompt_save": "Select a target folder",
        "prompt_partition": "Select a partition",
        "current_dir": "Current directory",
        "access_mode": "Access mode",
        "access_ro": "read-only",
        "access_rw": "read-write",
        "ext_limit": "Format limit",
        "hidden_on": "[Hidden files shown]",
        "selected_n": "Selected: {n}",
        "tips_base": "[num] Enter/Pick  [s] Pick current  [s<num>] Toggle item  "
                     "[b] Back  [r] Start  [g] Partition  [h] Hidden  [q] Cancel",
        "tips_multi": "\n  [a] Select all  [c] Clear  [d] Done",
        "tips_manager": "  ops: rm=delete  cp=copy  ct=cut  ps=paste  "
                        "rn=rename  op=open  at=attr  info=info  ls=list",
        "err_no_perm": "! No permission to read this directory.",
        "err_bad_num": "! Index out of range.",
        "err_bad_type": "! Item type does not match selection.",
        "err_no_pick": "! Nothing selected yet.",
        "err_not_exist": "! Path does not exist.",
        "err_dir_mismatch": "! Current directory does not match selection type.",
        "err_file_mismatch": "! File does not match selection type.",
        "ask_admin": "Not running as administrator. Request elevation?",
        "ask_root": "Not running as root. Request root access?",
        "no_root": "[cfdialog] No su available, skipping elevation.",
        "elevate_failed": "[cfdialog] Elevation failed: {msg}",
        "elevate_denied": "[cfdialog] Elevation denied by user.",
        "input_end": "Input ended",
        "user_cancel": "Cancelled by user",
        "free_name_prompt": "File name (blank = default)",
        "default_is": "default: {name}",
        "readonly_denied": "! Read-only mode: this action is disabled.",
        "nothing_sel": "! No items selected.",
        "must_one": "! Please select exactly one item.",
        "confirm_delete": "Delete {n} item(s)?",
        "deleted_ok": "Deleted: {n} item(s).",
        "clip_copied": "Copied {n} item(s) to clipboard.",
        "clip_cut": "Cut {n} item(s) to clipboard.",
        "clip_empty": "! Clipboard is empty.",
        "pasted_ok": "Pasted: {n} item(s).",
        "renamed_ok": "Renamed: {old} -> {new}",
        "opened_ok": "Opened: {path}",
        "attr_hdr": "Attributes of {name}",
        "attr_ro": "read-only",
        "attr_hidden": "hidden",
        "attr_size": "size",
        "attr_mtime": "mtime",
        "attr_toggle_ro": "toggle read-only",
        "attr_toggle_hidden": "toggle hidden (Windows only)",
        "attr_done": "Done.",
        "no_partitions": "! No partitions found.",
        "enter_num_or_q": "Enter a number or q to cancel: ",
        "yes_no_prompt": "[y/N]: ",
        "mode_path": "path mode",
        "mode_copy": "copy mode",
        "work_dir": "work directory",
        "prompt_rename": "New name",
        "prompt_lang_code": "System language code (e.g. de, ru, pt_BR)",
        "prompt_lang_name": "Language display name",
        "prompt_ref_lang": "Reference language (zh_CN or en)",
        "prompt_skip": "Press Enter to keep English fallback",
    },
    "zh_CN": {
        "prompt_folder": "请选择文件夹",
        "prompt_file": "请选择文件",
        "prompt_any": "请选择文件或文件夹",
        "prompt_save": "请选择目标文件夹",
        "prompt_partition": "请选择分区",
        "current_dir": "当前目录",
        "access_mode": "访问模式",
        "access_ro": "只读",
        "access_rw": "读写",
        "ext_limit": "格式限制",
        "hidden_on": "[显示隐藏文件]",
        "selected_n": "已选 {n} 项",
        "tips_base": "[编号] 进入/选择   [s] 选中当前   [s编号] 切换条目   "
                     "[b] 返回上级   [r] 回到起点   [g] 切换分区   [h] 隐藏文件   [q] 取消",
        "tips_multi": "\n  [a] 全选   [c] 清空   [d] 完成",
        "tips_manager": "  操作: rm=删除  cp=复制  ct=剪切  ps=粘贴  "
                        "rn=重命名  op=打开  at=属性  info=信息  ls=列表",
        "err_no_perm": "! 没有权限读取当前目录。",
        "err_bad_num": "! 编号超出范围。",
        "err_bad_type": "! 条目类型不符合选择要求。",
        "err_no_pick": "! 还没有选择任何条目。",
        "err_not_exist": "! 路径不存在。",
        "err_dir_mismatch": "! 当前目录不符合选择类型。",
        "err_file_mismatch": "! 该文件不符合选择要求。",
        "ask_admin": "当前未以管理员身份运行，是否需要提权？",
        "ask_root": "当前未以 root 运行，是否需要获取 root 权限？",
        "no_root": "[cfdialog] 未检测到 root（su 不可用），跳过提权。",
        "elevate_failed": "[cfdialog] 提权失败：{msg}",
        "elevate_denied": "[cfdialog] 用户拒绝了提权请求。",
        "input_end": "输入结束",
        "user_cancel": "用户取消操作",
        "free_name_prompt": "文件名（留空使用默认）",
        "default_is": "默认: {name}",
        "readonly_denied": "! 只读模式：该操作已被禁用。",
        "nothing_sel": "! 未选中任何条目。",
        "must_one": "! 请恰好选择一项。",
        "confirm_delete": "确认删除 {n} 个条目？",
        "deleted_ok": "已删除 {n} 个条目。",
        "clip_copied": "已复制 {n} 个条目到剪贴板。",
        "clip_cut": "已剪切 {n} 个条目到剪贴板。",
        "clip_empty": "! 剪贴板为空。",
        "pasted_ok": "已粘贴 {n} 个条目。",
        "renamed_ok": "已重命名: {old} -> {new}",
        "opened_ok": "已打开: {path}",
        "attr_hdr": "{name} 的属性",
        "attr_ro": "只读",
        "attr_hidden": "隐藏",
        "attr_size": "大小",
        "attr_mtime": "修改时间",
        "attr_toggle_ro": "切换只读",
        "attr_toggle_hidden": "切换隐藏（仅 Windows）",
        "attr_done": "完成。",
        "no_partitions": "! 未找到分区。",
        "enter_num_or_q": "输入编号或 q 取消: ",
        "yes_no_prompt": "[y/N]: ",
        "mode_path": "路径模式",
        "mode_copy": "复制模式",
        "work_dir": "工作目录",
        "prompt_rename": "新名称",
        "prompt_lang_code": "系统语言代码（例如 de、ru、pt_BR）",
        "prompt_lang_name": "语言显示名称",
        "prompt_ref_lang": "参考语言（zh_CN 或 en）",
        "prompt_skip": "直接回车保留英语回退",
    },
}

_BUILTIN_META = {
    "en": {
        "code": "en",
        "name": "英语",
        "name_en": "English",
        "native_name": "English",
    },
    "zh_CN": {
        "code": "zh_CN",
        "name": "简体中文",
        "name_en": "Simplified Chinese",
        "native_name": "简体中文",
    },
}

# 运行时的完整表
_STRINGS: dict = {k: dict(v) for k, v in _BUILTIN_STRINGS.items()}
_LANG_META: dict = {k: dict(v) for k, v in _BUILTIN_META.items()}
_LANG_LOAD_TRIED: set = set()


def _load_lang_pack(code: str) -> bool:
    """从 lg/<code>.txt 加载语言包。返回是否成功。"""
    if not code:
        return False
    if code in _BUILTIN_STRINGS:
        return True
    if code in _STRINGS:
        return True
    if code in _LANG_LOAD_TRIED:
        return False
    _LANG_LOAD_TRIED.add(code)

    path = LG_DIR / f"{code}.txt"
    if not path.is_file():
        _debug_log(f"lang pack not found: {path}")
        return False

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        _debug_log(f"failed reading lang pack {path}: {exc}")
        return False

    strings: dict = {}
    meta: dict = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            body = stripped[1:].strip()
            if "=" in body:
                k, v = body.split("=", 1)
                meta[k.strip()] = v.strip()
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        strings[k.strip()] = v

    if not strings:
        _debug_log(f"lang pack empty: {path}")
        return False

    base = dict(_BUILTIN_STRINGS[_DEFAULT_LANG])
    base.update(strings)
    _STRINGS[code] = base

    if meta:
        _LANG_META[code] = meta
    else:
        _LANG_META[code] = {"code": code, "name": code, "name_en": code, "native_name": code}

    _debug_log(f"loaded lang pack: {code} from {path}")
    return True


def _list_lg_files() -> List[str]:
    try:
        return sorted(p.stem for p in LG_DIR.glob("*.txt"))
    except Exception:
        return []


# =========================================================================== #
#                              语言代码归一化                                 #
# =========================================================================== #

_REGION_MAP = {
    "zh_cn": "zh_CN", "zh_hans": "zh_CN", "zh_sg": "zh_CN",
    "zh_tw": "zh_TW", "zh_hk": "zh_TW", "zh_mo": "zh_TW",
    "zh_hant": "zh_TW", "zh_cht": "zh_TW",
}

_PRIMARY_MAP = {
    "zh": "zh_CN",
    "ja": "ja", "jp": "ja",
    "ko": "ko", "kr": "ko",
    "ru": "ru",
    "fr": "fr",
    "es": "es",
    "ar": "ar",
    "en": "en",
}


def _normalize_lang_code(code) -> Optional[str]:
    if not code:
        return None
    s = str(code).split(":")[0]
    s = s.split(".")[0].split("@")[0].strip()
    if not s:
        return None

    low = s.replace("-", "_").lower()
    if low in ("c", "posix"):
        return None

    # 1) 内置 / 已加载
    if s in _STRINGS:
        return s
    for reg in _STRINGS:
        if reg.lower() == low:
            return reg

    # 2) 尝试外部语言包
    if _load_lang_pack(s):
        return s
    if _load_lang_pack(low):
        return low

    # 3) 区域特例
    if low in _REGION_MAP:
        target = _REGION_MAP[low]
        if _load_lang_pack(target):
            return target

    # 4) 主语言
    primary = low.split("_")[0]
    for reg in list(_STRINGS.keys()) + [p for p in _list_lg_files()]:
        if reg.lower().split("_")[0] == primary:
            if _load_lang_pack(reg):
                return reg
    if primary in _PRIMARY_MAP:
        target = _PRIMARY_MAP[primary]
        if _load_lang_pack(target):
            return target

    return None


# =========================================================================== #
#                              语言状态                                       #
# =========================================================================== #

_LANG = _DEFAULT_LANG


def _detect_language() -> str:
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        val = os.environ.get(var)
        if val:
            code = _normalize_lang_code(val)
            if code:
                return code
    try:
        import locale
        loc = locale.getlocale()
        if loc and loc[0]:
            code = _normalize_lang_code(loc[0])
            if code:
                return code
    except Exception:
        pass
    if _IS_WINDOWS:
        try:
            langid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            mapping = {
                0x0404: "zh_TW", 0x0C04: "zh_TW", 0x1404: "zh_TW",
                0x0804: "zh_CN", 0x1004: "zh_CN",
                0x0409: "en", 0x0809: "en", 0x0C09: "en",
                0x0411: "ja", 0x0412: "ko",
                0x040C: "fr", 0x080C: "fr", 0x0C0C: "fr",
                0x0419: "ru",
                0x0C0A: "es", 0x040A: "es",
                0x0401: "ar", 0x0801: "ar", 0x0C01: "ar",
            }
            if langid in mapping:
                target = mapping[langid]
                if _load_lang_pack(target):
                    return target
        except Exception:
            pass
    return _DEFAULT_LANG


_LANG = _detect_language()
_debug_log(f"detected language: {_LANG}")


def _resolve_lang(lang) -> str:
    """
    决定本次调用使用的语言代码。

    优先级（从高到低）:
        1. ts.txt 里的 force_language
        2. 调用方传入的 lang 参数
        3. 全局 _LANG
        4. _DEFAULT_LANG
    """
    forced = _DEBUG.get("force_language")
    if forced:
        code = _normalize_lang_code(forced)
        if code:
            return code

    if lang is None:
        return _LANG

    code = _normalize_lang_code(lang)
    return code if code else _DEFAULT_LANG


def _t(key: str, lang: Optional[str] = None, **fmt) -> str:
    code = lang if lang else _LANG
    if code not in _STRINGS:
        if not _load_lang_pack(code):
            code = _DEFAULT_LANG
    table = _STRINGS.get(code) or _STRINGS[_DEFAULT_LANG]
    s = table.get(key)
    if s is None:
        s = _STRINGS[_DEFAULT_LANG].get(key, key)
    if fmt:
        try:
            return s.format(**fmt)
        except Exception:
            return s
    return s


# =========================================================================== #
#                              语言公开 API                                   #
# =========================================================================== #

def get_language() -> str:
    return _LANG


def set_language(lang) -> str:
    global _LANG
    if lang is None:
        _LANG = _DEFAULT_LANG
        return _LANG
    code = _normalize_lang_code(lang)
    _LANG = code if code else _DEFAULT_LANG
    _debug_log(f"set_language -> {_LANG}")
    return _LANG


def detect_language() -> str:
    return _detect_language()


def register_language(code: str,
                      strings: Optional[dict] = None,
                      base: Optional[str] = None,
                      meta: Optional[dict] = None,
                      **kwargs) -> str:
    """
    注册 / 覆盖语言（运行时内存中）。
    若想持久化到 lg/，请使用 make_custom_lang.py。
    """
    if not code:
        raise ValueError("language code is required")
    provided: dict = {}
    if strings:
        if not isinstance(strings, dict):
            raise TypeError("strings must be a dict")
        provided.update(strings)
    if kwargs:
        provided.update(kwargs)

    key = code.strip()
    base_code = base if base is not None else _DEFAULT_LANG
    if base_code not in _STRINGS:
        base_code = _normalize_lang_code(base_code) or _DEFAULT_LANG

    merged = dict(_STRINGS.get(base_code, _STRINGS[_DEFAULT_LANG]))
    if key in _STRINGS:
        merged.update(_STRINGS[key])
    merged.update(provided)
    _STRINGS[key] = merged

    if meta is None:
        _LANG_META.setdefault(key, {
            "code": key, "name": key, "name_en": key, "native_name": key,
        })
    else:
        _LANG_META[key] = dict(meta)

    _debug_log(f"register_language: {key}")
    return key


def unregister_language(code: str) -> bool:
    if code in BUILTIN_LANGUAGES:
        raise ValueError(f"cannot unregister builtin language: {code}")
    if code in _STRINGS:
        del _STRINGS[code]
        _LANG_META.pop(code, None)
        _LANG_LOAD_TRIED.discard(code)
        if _LANG == code:
            set_language(None)
        return True
    return False


def list_languages() -> List[str]:
    """返回当前可用的语言代码（内置 + 外部文件 + 运行时注册）。"""
    codes = set(_STRINGS.keys())
    codes.update(_list_lg_files())
    return sorted(codes)


def get_language_meta(code: str) -> dict:
    """返回语言元数据（系统名称、英文名、本地名）。"""
    if code in _LANG_META:
        return dict(_LANG_META[code])
    if _load_lang_pack(code):
        return dict(_LANG_META.get(code, {"code": code, "name": code,
                                          "name_en": code, "native_name": code}))
    return {"code": code, "name": code, "name_en": code, "native_name": code}


# =========================================================================== #
#                              提权                                           #
# =========================================================================== #

def is_windows() -> bool:
    return _IS_WINDOWS


def is_android() -> bool:
    return _IS_ANDROID


def is_elevated() -> bool:
    if _IS_WINDOWS:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def has_root_available() -> bool:
    if _IS_WINDOWS:
        return True
    if shutil.which("su") or shutil.which("sudo"):
        return True
    for p in ("/system/xbin/su", "/system/bin/su", "/su/bin/su", "/sbin/su"):
        if os.path.exists(p):
            return True
    return False


def _default_ask(question: str) -> bool:
    try:
        ans = input(f"{question} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes", "是", "1")


def request_elevation(interactive: bool = True,
                      ask: Optional[Callable[[str], bool]] = None,
                      lang: Optional[str] = None) -> str:
    ask = ask or _default_ask
    code = _resolve_lang(lang)
    if is_elevated():
        return "already"
    if _IS_WINDOWS:
        if not interactive:
            return "denied"
        if not ask(_t("ask_admin", lang=code)):
            return "denied"
        return _relaunch_windows(code)
    if _IS_ANDROID:
        if not has_root_available():
            print(_t("no_root", lang=code))
            return "unavailable"
        if not interactive:
            return "denied"
        if not ask(_t("ask_root", lang=code)):
            return "denied"
        return _relaunch_root(code)
    if shutil.which("sudo") or shutil.which("su"):
        if not interactive:
            return "denied"
        if not ask(_t("ask_root", lang=code)):
            return "denied"
        return _relaunch_root(code)
    return "not_needed"


def _relaunch_windows(lang: str) -> str:
    try:
        if getattr(sys, "frozen", False):
            exe = sys.executable
            params = " ".join(shlex.quote(a) for a in sys.argv[1:])
        else:
            script = os.path.abspath(sys.argv[0])
            args = " ".join(shlex.quote(a) for a in sys.argv[1:])
            exe = sys.executable
            params = f'"{script}" {args}'.strip()
        rc = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", exe, params, None, 1)
    except Exception as exc:
        print(_t("elevate_failed", lang=lang, msg=str(exc)))
        return "denied"
    if rc <= 32:
        print(_t("elevate_denied", lang=lang))
        return "denied"
    return "relaunched"


def _relaunch_root(lang: str) -> str:
    cmd = [sys.executable, *sys.argv]
    quoted = " ".join(shlex.quote(c) for c in cmd)
    if _IS_ANDROID:
        if shutil.which("su"):
            argv = ["su", "-c", quoted]
        elif shutil.which("sudo"):
            argv = ["sudo", *cmd]
        else:
            return "unavailable"
    else:
        if shutil.which("sudo"):
            argv = ["sudo", *cmd]
        elif shutil.which("su"):
            argv = ["su", "-c", quoted]
        else:
            return "unavailable"
    try:
        subprocess.Popen(argv)
    except Exception as exc:
        print(_t("elevate_failed", lang=lang, msg=str(exc)))
        return "denied"
    return "relaunched"


_AUTO_ELEVATE = True
_ELEVATION_DONE = False
_FORCE_ANDROID_ELEVATE = False


def set_auto_elevate(enabled: bool) -> None:
    global _AUTO_ELEVATE
    _AUTO_ELEVATE = bool(enabled)


def _maybe_elevate(lang: Optional[str] = None) -> None:
    global _ELEVATION_DONE
    if _ELEVATION_DONE:
        return
    _ELEVATION_DONE = True
    if not _AUTO_ELEVATE:
        return
    if _IS_ANDROID and not _FORCE_ANDROID_ELEVATE:
        return
    status = request_elevation(interactive=True, lang=lang)
    if status == "relaunched":
        sys.exit(0)


# =========================================================================== #
#                              分区                                           #
# =========================================================================== #

def list_partitions() -> List[dict]:
    if _IS_WINDOWS:
        return _list_windows_partitions()
    return _list_posix_mounts()


def _list_posix_mounts() -> List[dict]:
    items = [{"name": "/", "path": "/", "kind": "root", "label": "", "type": ""}]
    seen = {"/"}
    for base in ("/mnt", "/media", "/Volumes", "/run/media"):
        if not os.path.isdir(base):
            continue
        try:
            entries = sorted(os.listdir(base))
        except OSError:
            continue
        for name in entries:
            full = os.path.join(base, name)
            if not os.path.isdir(full) or full in seen:
                continue
            seen.add(full)
            items.append({"name": name, "path": full, "kind": "mount",
                          "label": "", "type": ""})
    return items


def _list_windows_partitions() -> List[dict]:
    items: List[dict] = []
    seen_mounts = set()

    try:
        mask = ctypes.windll.kernel32.GetLogicalDrives()
    except Exception:
        mask = 0

    for i in range(26):
        if not (mask & (1 << i)):
            continue
        letter = chr(ord("A") + i)
        root = f"{letter}:\\"
        seen_mounts.add(root.upper())
        try:
            kind_code = ctypes.windll.kernel32.GetDriveTypeW(root)
        except Exception:
            kind_code = 0
        kind_str = {0: "unknown", 1: "invalid", 2: "removable", 3: "fixed",
                    4: "remote", 5: "cdrom", 6: "ramdisk"}.get(kind_code, "unknown")
        items.append({"name": f"{letter}:", "path": root, "kind": "drive",
                      "label": _win_volume_label(root), "type": kind_str})

    try:
        for vol_path in _win_enumerate_volumes():
            mounts = _win_volume_mounts(vol_path)
            if any(m.upper() in seen_mounts for m in mounts):
                continue
            items.append({"name": vol_path.rstrip("\\"), "path": vol_path,
                          "kind": "volume", "label": _win_volume_label(vol_path),
                          "type": "volume"})
    except Exception:
        pass

    return items


def _win_volume_label(path: str) -> str:
    try:
        buf = ctypes.create_unicode_buffer(261)
        ok = ctypes.windll.kernel32.GetVolumeInformationW(
            path, buf, 261, None, None, None, None, 0)
        return buf.value if ok else ""
    except Exception:
        return ""


def _win_enumerate_volumes() -> List[str]:
    buf_size = 1024
    buf = ctypes.create_unicode_buffer(buf_size)
    try:
        handle = ctypes.windll.kernel32.FindFirstVolumeW(buf, buf_size)
    except Exception:
        return []
    INVALID = ctypes.c_void_p(-1).value
    if not handle or handle == INVALID:
        return []
    result: List[str] = []
    try:
        while True:
            result.append(buf.value)
            if not ctypes.windll.kernel32.FindNextVolumeW(handle, buf, buf_size):
                break
    finally:
        try:
            ctypes.windll.kernel32.FindVolumeClose(handle)
        except Exception:
            pass
    return result


def _win_volume_mounts(volume_path: str) -> List[str]:
    try:
        size = ctypes.wintypes.DWORD(0)
        ctypes.windll.kernel32.GetVolumePathNamesForVolumeNameW(
            volume_path, None, 0, ctypes.byref(size))
        if not size.value:
            return []
        buf = ctypes.create_unicode_buffer(size.value)
        ctypes.windll.kernel32.GetVolumePathNamesForVolumeNameW(
            volume_path, buf, size.value, ctypes.byref(size))
        text = ctypes.wstring_at(buf, size.value * ctypes.sizeof(ctypes.c_wchar))
        return [s for s in text.split("\x00") if s]
    except Exception:
        return []


if _IS_WINDOWS:
    import ctypes.wintypes  # noqa: E402


# =========================================================================== #
#                              扩展名                                         #
# =========================================================================== #

def _normalize_extensions(extensions) -> Optional[frozenset]:
    if extensions is None:
        return None
    if isinstance(extensions, str):
        extensions = [extensions]
    exts = set()
    for e in extensions:
        if e is None:
            continue
        s = str(e).strip().lower()
        if not s:
            continue
        if s in ("*", "*.*", "all", "any"):
            return None
        if s.startswith("*"):
            s = s[1:]
        if not s.startswith("."):
            s = "." + s
        exts.add(s)
    return frozenset(exts) if exts else None


def _match_extension(name: str, exts: Optional[frozenset]) -> bool:
    if exts is None:
        return True
    lower = name.lower()
    return any(lower.endswith(e) for e in exts)


# =========================================================================== #
#                              文件工具                                       #
# =========================================================================== #

def _unique_path(target: Path) -> Path:
    parent = target.parent
    if target.is_dir():
        stem, suffix = target.name, ""
    else:
        stem, suffix = target.stem, target.suffix
    i = 1
    while True:
        cand = parent / f"{stem}_{i}{suffix}"
        if not cand.exists():
            return cand
        i += 1


def _remove_path(p: Path) -> None:
    if p.is_dir() and not p.is_symlink():
        shutil.rmtree(p)
    else:
        p.unlink()


def copy_into(src: PathLike, dst_dir: PathLike, overwrite: bool = False) -> Path:
    src_p = Path(src).expanduser().resolve()
    dst_p = Path(dst_dir).expanduser().resolve()
    if not src_p.exists():
        raise FileNotFoundError(src_p)
    dst_p.mkdir(parents=True, exist_ok=True)
    target = dst_p / src_p.name
    if target.exists():
        if overwrite:
            _remove_path(target)
        else:
            target = _unique_path(target)
    if src_p.is_dir():
        shutil.copytree(src_p, target)
    else:
        shutil.copy2(src_p, target)
    _debug_log(f"copy: {src_p} -> {target}")
    return target


def _move_into(src: PathLike, dst_dir: PathLike, overwrite: bool = False) -> Path:
    src_p = Path(src).expanduser().resolve()
    dst_p = Path(dst_dir).expanduser().resolve()
    if not src_p.exists():
        raise FileNotFoundError(src_p)
    dst_p.mkdir(parents=True, exist_ok=True)
    target = dst_p / src_p.name
    if target.exists():
        if overwrite:
            _remove_path(target)
        else:
            target = _unique_path(target)
    shutil.move(str(src_p), str(target))
    _debug_log(f"move: {src_p} -> {target}")
    return target


# =========================================================================== #
#                              浏览器核心                                     #
# =========================================================================== #

def _list_dir(cur: Path, show_hidden: bool,
              extensions: Optional[frozenset], t: Callable) -> List[Tuple[str, Path, bool]]:
    rows: List[Tuple[str, Path, bool]] = []
    try:
        names = os.listdir(cur)
    except PermissionError:
        print(t("err_no_perm"))
        return rows
    except OSError as exc:
        print(f"! {exc}")
        return rows

    def sort_key(n: str):
        p = cur / n
        try:
            is_dir = p.is_dir()
        except OSError:
            is_dir = False
        return (not is_dir, n.lower())

    for name in sorted(names, key=sort_key):
        if not show_hidden and name.startswith("."):
            continue
        p = cur / name
        try:
            is_dir = p.is_dir()
        except OSError:
            is_dir = False
        if not is_dir and not _match_extension(name, extensions):
            continue
        rows.append((name, p, is_dir))
    return rows


def _format_size(n: int) -> str:
    f = float(n)
    for u in ["B", "K", "M", "G", "T"]:
        if f < 1024 or u == "T":
            return f"{int(f)}B" if u == "B" else f"{f:.1f}{u}"
        f /= 1024
    return f"{n}B"


def _render_browse(cur: Path, items, picked, multiple: bool, prompt: str,
                   show_hidden: bool, exts, access: Optional[str],
                   manager: bool, t: Callable) -> None:
    bar = "─" * 72
    print()
    print(bar)
    print(f"  {prompt}")
    print(f"  {t('current_dir')}: {cur}")
    if access is not None:
        mode_str = t("access_rw") if access == "readwrite" else t("access_ro")
        print(f"  {t('access_mode')}: {mode_str}")
    if exts:
        print(f"  {t('ext_limit')}: {', '.join(sorted(exts))}")
    if show_hidden:
        print("  " + t("hidden_on"))
    if multiple and picked:
        print("  " + t("selected_n", n=len(picked)))
    print(bar)
    if cur.parent != cur:
        print("    0)  <DIR>  ..")
    for i, (name, p, is_dir) in enumerate(items, 1):
        tag = "<DIR> " if is_dir else "<FILE>"
        mark = "*" if p in picked else " "
        slash = "/" if is_dir else ""
        size = ""
        if not is_dir:
            try:
                size = f" ({_format_size(p.stat().st_size)})"
            except OSError:
                size = ""
        print(f"  {mark} {i:>3}) {tag} {name}{slash}{size}")
    print(bar)
    print("  " + t("tips_base"))
    if multiple:
        print(t("tips_multi"))
    if manager:
        print(t("tips_manager"))
    print(bar)


def _browse_partitions(lang: str, prompt: Optional[str] = None) -> Optional[str]:
    parts = list_partitions()
    if not parts:
        print(_t("no_partitions", lang=lang))
        return None
    while True:
        bar = "─" * 72
        print()
        print(bar)
        print(f"  {prompt or _t('prompt_partition', lang=lang)}")
        print(bar)
        for i, p in enumerate(parts, 1):
            label = p.get("label", "")
            typ = p.get("type", "")
            extra = " ".join(x for x in (label, typ) if x)
            if extra:
                extra = f"  ({extra})"
            print(f"  {i:>3})  {p['name']:<28}{extra}")
            print(f"        {p['path']}")
        print(bar)
        print("  " + _t("enter_num_or_q", lang=lang))
        print(bar)
        try:
            raw = input("> ").strip()
        except EOFError:
            return None
        if raw.lower() in ("q", "quit", "exit", ""):
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(parts):
                return parts[idx - 1]["path"]
        print("! 无效输入 / Invalid.")


def _browse(start_dir: Optional[PathLike] = None,
            select: str = "file",
            multiple: bool = False,
            show_hidden: bool = False,
            prompt: Optional[str] = None,
            extensions=None,
            lang: Optional[str] = None,
            access: Optional[str] = None,
            manager: bool = False) -> List[Path]:
    if select not in ("file", "dir", "any"):
        raise ValueError("select must be 'file' / 'dir' / 'any'")

    code = _resolve_lang(lang)

    def t(key, **fmt):
        return _t(key, lang=code, **fmt)

    if prompt is None:
        if select == "dir":
            prompt = t("prompt_folder")
        elif select == "any":
            prompt = t("prompt_any")
        else:
            prompt = t("prompt_file")

    exts = _normalize_extensions(extensions)

    cur = Path(start_dir).expanduser() if start_dir else Path.cwd()
    if not cur.is_absolute():
        cur = (Path.cwd() / cur).resolve()
    if not cur.is_dir():
        cur = Path.cwd().resolve()
    origin = cur
    picked: List[Path] = []

    _debug_log(f"browse start: cur={cur} select={select} multiple={multiple}")

    def accepts(p: Path, is_dir: bool) -> bool:
        if select == "dir":
            return is_dir
        if is_dir:
            return select == "any"
        return _match_extension(p.name, exts)

    while True:
        items = _list_dir(cur, show_hidden, exts, t)
        _render_browse(cur, items, picked, multiple, prompt,
                       show_hidden, exts, access, manager, t)

        try:
            raw = input("> ").strip()
        except EOFError:
            raise BrowserCancelled(t("input_end"))

        if not raw:
            continue
        low = raw.lower()

        if low in ("q", "quit", "exit"):
            raise BrowserCancelled(t("user_cancel"))

        if low == "g":
            new_path = _browse_partitions(code)
            if new_path:
                try:
                    p = Path(new_path)
                    if p.is_dir():
                        cur = p
                except Exception:
                    print("! 无法进入该分区。")
            continue

        if low in ("b", "back", ".."):
            if cur.parent != cur:
                cur = cur.parent
            continue

        if low in ("r", "root", "home", "~"):
            cur = origin
            continue

        if low == "h":
            show_hidden = not show_hidden
            continue

        if low == "c" and multiple:
            picked.clear()
            continue

        if low == "a" and multiple:
            for _, p, is_dir in items:
                if accepts(p, is_dir) and p not in picked:
                    picked.append(p)
            continue

        if low == "d" and multiple:
            if not picked:
                print(t("err_no_pick"))
                continue
            return list(picked)

        if low == "s":
            if not accepts(cur, True):
                print(t("err_dir_mismatch"))
                continue
            if multiple:
                if cur not in picked:
                    picked.append(cur)
            else:
                return [cur]
            continue

        if low.startswith("s") and low[1:].strip().isdigit():
            idx = int(low[1:].strip())
            if not (1 <= idx <= len(items)):
                print(t("err_bad_num"))
                continue
            _, p, is_dir = items[idx - 1]
            if not accepts(p, is_dir):
                print(t("err_bad_type"))
                continue
            if multiple:
                if p in picked:
                    picked.remove(p)
                else:
                    picked.append(p)
            else:
                return [p]
            continue

        if raw.isdigit():
            idx = int(raw)
            if idx == 0:
                if cur.parent != cur:
                    cur = cur.parent
                continue
            if not (1 <= idx <= len(items)):
                print(t("err_bad_num"))
                continue
            _, p, is_dir = items[idx - 1]
            if is_dir:
                cur = p
                continue
            if not accepts(p, False):
                print(t("err_file_mismatch"))
                continue
            if multiple:
                if p in picked:
                    picked.remove(p)
                else:
                    picked.append(p)
            else:
                return [p]
            continue

        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = cur / p
        try:
            p = p.resolve()
        except OSError:
            pass

        if not p.exists():
            print(t("err_not_exist"))
            continue
        if p.is_dir():
            cur = p
            continue
        if not accepts(p, False):
            print(t("err_file_mismatch"))
            continue
        if multiple:
            if p in picked:
                picked.remove(p)
            else:
                picked.append(p)
        else:
            return [p]


# =========================================================================== #
#                              选择器 API                                     #
# =========================================================================== #

def pick(select: str = "file",
         multiple: bool = False,
         mode: str = "path",
         work_dir: Optional[PathLike] = None,
         start_dir: Optional[PathLike] = None,
         extensions=None,
         overwrite: bool = False,
         show_hidden: bool = False,
         prompt: Optional[str] = None,
         lang: Optional[str] = None):
    if select not in ("file", "folder", "any"):
        raise ValueError("select must be 'file'/'folder'/'any'")
    if mode not in ("path", "copy"):
        raise ValueError("mode must be 'path'/'copy'")
    internal = "dir" if select == "folder" else select
    _maybe_elevate(lang=lang)

    paths = _browse(start_dir=start_dir, select=internal, multiple=multiple,
                    show_hidden=show_hidden, prompt=prompt,
                    extensions=extensions if select != "folder" else None,
                    lang=lang)

    if mode == "copy" and paths:
        dst = Path(work_dir).expanduser().resolve() if work_dir else Path.cwd().resolve()
        copies = [copy_into(p, dst, overwrite=overwrite) for p in paths]
        return copies if multiple else copies[0]
    return paths if multiple else (paths[0] if paths else None)


def pick_file(multiple: bool = False,
              mode: str = "copy",
              work_dir: Optional[PathLike] = None,
              start_dir: Optional[PathLike] = None,
              extensions=None,
              overwrite: bool = False,
              show_hidden: bool = False,
              prompt: Optional[str] = None,
              lang: Optional[str] = None):
    return pick(select="file", multiple=multiple, mode=mode,
                work_dir=work_dir, start_dir=start_dir,
                extensions=extensions, overwrite=overwrite,
                show_hidden=show_hidden, prompt=prompt, lang=lang)


def pick_folder(multiple: bool = False,
                mode: str = "path",
                work_dir: Optional[PathLike] = None,
                start_dir: Optional[PathLike] = None,
                show_hidden: bool = False,
                prompt: Optional[str] = None,
                lang: Optional[str] = None):
    return pick(select="folder", multiple=multiple, mode=mode,
                work_dir=work_dir, start_dir=start_dir,
                show_hidden=show_hidden, prompt=prompt, lang=lang)


# =========================================================================== #
#                              保存器 API                                     #
# =========================================================================== #

def _prompt_free_name(default_name: str, lang: str) -> Optional[str]:
    try:
        hint = f" ({_t('default_is', lang=lang, name=default_name)})"
        raw = input(f"  {_t('free_name_prompt', lang=lang)}{hint}\n  > ").strip()
    except EOFError:
        return None
    if raw == "":
        return default_name
    return os.path.basename(raw)


def save(sources=None,
         target_dir: Optional[PathLike] = None,
         mode: str = "path",
         work_dir: Optional[PathLike] = None,
         free_name: bool = False,
         default_name: Optional[str] = None,
         overwrite: bool = False,
         on_progress: Optional[Callable[[int, int, Path], None]] = None,
         start_dir: Optional[PathLike] = None,
         show_hidden: bool = False,
         prompt: Optional[str] = None,
         lang: Optional[str] = None):
    """
    统一保存器（详见文档 §4.4）。
    """
    if mode not in ("path", "copy"):
        raise ValueError("mode must be 'path'/'copy'")
    code = _resolve_lang(lang)
    _maybe_elevate(lang=code)

    if sources is None:
        src_list: List[Path] = []
        single = False
    elif isinstance(sources, (str, Path)):
        single = True
        src_list = [Path(sources)]
    else:
        src_list = [Path(s) for s in sources]
        single = (len(src_list) == 1)

    base = Path(work_dir).expanduser().resolve() if work_dir else Path.cwd().resolve()
    resolved: List[Path] = []
    for p in src_list:
        if not p.is_absolute():
            p = base / p
        p = p.expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(p)
        resolved.append(p)

    if target_dir is None:
        pr = prompt or _t("prompt_save", lang=code)
        picked = _browse(start_dir=start_dir, select="dir", multiple=False,
                         show_hidden=show_hidden, prompt=pr, lang=code)
        if not picked:
            return None
        target_dir_path = picked[0]
    else:
        target_dir_path = Path(target_dir).expanduser().resolve()
        target_dir_path.mkdir(parents=True, exist_ok=True)

    if free_name and single:
        default_nm = default_name or resolved[0].name
        new_name = _prompt_free_name(default_nm, code)
        if new_name is None:
            return None
        target_file = target_dir_path / new_name
        if target_file.exists() and not overwrite:
            target_file = _unique_path(target_file)
        if mode == "copy":
            src = resolved[0]
            if src.is_dir():
                shutil.copytree(src, target_file)
            else:
                shutil.copy2(src, target_file)
        return target_file

    if mode == "path" or not resolved:
        return target_dir_path

    results: List[Path] = []
    total = len(resolved)
    for i, src in enumerate(resolved, 1):
        if on_progress:
            on_progress(i, total, src)
        results.append(copy_into(src, target_dir_path, overwrite=overwrite))
    return results[0] if single else results


def save_folder(start_dir: Optional[PathLike] = None,
                show_hidden: bool = False,
                prompt: Optional[str] = None,
                lang: Optional[str] = None) -> Optional[Path]:
    return save(sources=None, mode="path", start_dir=start_dir,
                show_hidden=show_hidden, prompt=prompt, lang=lang)


# =========================================================================== #
#                              文件管理器                                     #
# =========================================================================== #

def _open_path(p: Path) -> bool:
    try:
        if _IS_WINDOWS:
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])
        return True
    except Exception as exc:
        _debug_log(f"open failed: {exc}")
        return False


def _get_attrs_win(p: Path) -> Optional[int]:
    if not _IS_WINDOWS:
        return None
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(p))
        if attrs == 0xFFFFFFFF:
            return None
        return int(attrs)
    except Exception:
        return None


def _set_attrs_win(p: Path, attrs: int) -> bool:
    if not _IS_WINDOWS:
        return False
    try:
        return bool(ctypes.windll.kernel32.SetFileAttributesW(str(p), attrs))
    except Exception:
        return False


def _is_readonly(p: Path) -> bool:
    if _IS_WINDOWS:
        a = _get_attrs_win(p)
        if a is not None:
            return bool(a & 0x01)
    try:
        return not os.access(p, os.W_OK)
    except Exception:
        return False


def _set_readonly(p: Path, value: bool) -> bool:
    if _IS_WINDOWS:
        attrs = _get_attrs_win(p)
        if attrs is None:
            attrs = 0x80
        attrs = (attrs | 0x01) if value else (attrs & ~0x01)
        return _set_attrs_win(p, attrs)
    try:
        mode = p.stat().st_mode
        if value:
            mode &= ~(_stat.S_IWUSR | _stat.S_IWGRP | _stat.S_IWOTH)
        else:
            mode |= _stat.S_IWUSR
        os.chmod(p, mode)
        return True
    except Exception:
        return False


def _is_hidden(p: Path) -> bool:
    if _IS_WINDOWS:
        a = _get_attrs_win(p)
        if a is not None:
            return bool(a & 0x02)
    return p.name.startswith(".")


def _set_hidden(p: Path, value: bool) -> bool:
    if _IS_WINDOWS:
        attrs = _get_attrs_win(p)
        if attrs is None:
            attrs = 0x80
        attrs = (attrs | 0x02) if value else (attrs & ~0x02)
        return _set_attrs_win(p, attrs)
    return False


def file_manager(start_dir: Optional[PathLike] = None,
                 access: str = "readwrite",
                 show_hidden: bool = False,
                 prompt: Optional[str] = None,
                 lang: Optional[str] = None) -> None:
    """
    交互式文件管理器（详见文档 §4.5）。

    access: "readonly" | "readwrite"
    """
    if access not in ("readonly", "readwrite"):
        raise ValueError("access must be 'readonly'/'readwrite'")
    code = _resolve_lang(lang)

    def t(key, **fmt):
        return _t(key, lang=code, **fmt)

    _maybe_elevate(lang=code)
    _debug_log(f"file_manager start: access={access}")

    cur = Path(start_dir).expanduser() if start_dir else Path.cwd()
    if not cur.is_absolute():
        cur = (Path.cwd() / cur).resolve()
    if not cur.is_dir():
        cur = Path.cwd().resolve()
    origin = cur

    picked: List[Path] = []
    clipboard: List[Path] = []
    clipboard_mode: Optional[str] = None
    allow_write = (access == "readwrite")

    def _render():
        items = _list_dir(cur, show_hidden, None, t)
        pr = prompt or t("prompt_any")
        _render_browse(cur, items, picked, True, pr, show_hidden,
                       None, access, True, t)
        if clipboard:
            mode_str = "cut" if clipboard_mode == "cut" else "copy"
            print(f"  [{mode_str}] clipboard: {len(clipboard)} item(s)")
        return items

    def _require_write() -> bool:
        if not allow_write:
            print(t("readonly_denied"))
            return False
        return True

    def _ask_confirm(question: str) -> bool:
        try:
            ans = input(f"  {question} {t('yes_no_prompt')}").strip().lower()
        except EOFError:
            return False
        return ans in ("y", "yes", "是", "1")

    def _resolve_targets(args: List[str], items) -> List[Path]:
        result: List[Path] = []
        for a in args:
            if a.isdigit():
                idx = int(a)
                if 1 <= idx <= len(items):
                    result.append(items[idx - 1][1])
        return result

    def _show_attrs(p: Path) -> None:
        try:
            st = p.stat()
        except OSError as exc:
            print(f"! {exc}")
            return
        print()
        print("─" * 64)
        print(f"  {t('attr_hdr', name=p.name)}")
        print("─" * 64)
        print(f"  path         : {p}")
        print(f"  {t('attr_ro'):<13}: {_is_readonly(p)}")
        print(f"  {t('attr_hidden'):<13}: {_is_hidden(p)}")
        if p.is_file():
            print(f"  {t('attr_size'):<13}: {_format_size(st.st_size)}")
        print(f"  {t('attr_mtime'):<13}: "
              f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))}")
        print("─" * 64)

    def _edit_attrs(p: Path) -> None:
        while True:
            _show_attrs(p)
            print(f"  r = {t('attr_toggle_ro')}")
            if _IS_WINDOWS:
                print(f"  h = {t('attr_toggle_hidden')}")
            print(f"  q = {t('attr_done')}")
            try:
                ch = input("  > ").strip().lower()
            except EOFError:
                return
            if ch in ("q", ""):
                return
            if ch == "r":
                new_val = not _is_readonly(p)
                if _set_readonly(p, new_val):
                    print(f"  ✔ {t('attr_ro')} = {new_val}")
                else:
                    print("! 修改失败 / failed")
            elif ch == "h" and _IS_WINDOWS:
                new_val = not _is_hidden(p)
                if _set_hidden(p, new_val):
                    print(f"  ✔ {t('attr_hidden')} = {new_val}")
                else:
                    print("! 修改失败 / failed")

    while True:
        items = _render()
        try:
            raw = input("> ").strip()
        except EOFError:
            return
        if not raw:
            continue
        low = raw.lower()

        # ---------------- 导航 ----------------
        if low in ("q", "quit", "exit"):
            return
        if low == "g":
            new_path = _browse_partitions(code)
            if new_path:
                try:
                    p = Path(new_path)
                    if p.is_dir():
                        cur = p
                except Exception:
                    print("! 无法进入该分区。")
            continue
        if low in ("b", "back", ".."):
            if cur.parent != cur:
                cur = cur.parent
            continue
        if low in ("r", "root", "home", "~"):
            cur = origin
            continue
        if low == "h":
            show_hidden = not show_hidden
            continue

        # ---------------- 选择 ----------------
        if low == "sa":
            for _, p, _ in items:
                if p not in picked:
                    picked.append(p)
            continue
        if low == "sc":
            picked.clear()
            continue
        if low.startswith("s") and low[1:].isdigit():
            idx = int(low[1:])
            if 1 <= idx <= len(items):
                p = items[idx - 1][1]
                if p in picked:
                    picked.remove(p)
                else:
                    picked.append(p)
            else:
                print(t("err_bad_num"))
            continue
        if raw.isdigit():
            idx = int(raw)
            if idx == 0:
                if cur.parent != cur:
                    cur = cur.parent
                continue
            if 1 <= idx <= len(items):
                _, p, is_dir = items[idx - 1]
                if is_dir:
                    cur = p
                else:
                    if p in picked:
                        picked.remove(p)
                    else:
                        picked.append(p)
            else:
                print(t("err_bad_num"))
            continue

        # ---------------- 操作 ----------------
        if low == "ls":
            if not picked:
                print(t("nothing_sel"))
            else:
                for p in picked:
                    print(f"  - {p}")
            continue

        if low == "info":
            if not picked:
                print(t("nothing_sel"))
                continue
            if len(picked) != 1:
                print(t("must_one"))
                continue
            _show_attrs(picked[0])
            continue

        if low == "op":
            if not picked:
                print(t("nothing_sel"))
                continue
            if len(picked) != 1:
                print(t("must_one"))
                continue
            if _open_path(picked[0]):
                print(t("opened_ok", path=picked[0]))
            else:
                print("! 打开失败 / open failed")
            continue

        if low == "rm":
            if not _require_write():
                continue
            if not picked:
                print(t("nothing_sel"))
                continue
            if not _ask_confirm(t("confirm_delete", n=len(picked))):
                continue
            n = 0
            for p in list(picked):
                try:
                    _remove_path(p)
                    picked.remove(p)
                    n += 1
                    _debug_log(f"deleted: {p}")
                except Exception as exc:
                    print(f"! {p}: {exc}")
            print(t("deleted_ok", n=n))
            continue

        if low == "cp":
            if not picked:
                print(t("nothing_sel"))
                continue
            clipboard = list(picked)
            clipboard_mode = "copy"
            print(t("clip_copied", n=len(clipboard)))
            continue

        if low == "ct":
            if not _require_write():
                continue
            if not picked:
                print(t("nothing_sel"))
                continue
            clipboard = list(picked)
            clipboard_mode = "cut"
            print(t("clip_cut", n=len(clipboard)))
            continue

        if low == "ps":
            if not _require_write():
                continue
            if not clipboard:
                print(t("clip_empty"))
                continue
            n = 0
            for src in list(clipboard):
                try:
                    if clipboard_mode == "cut":
                        _move_into(src, cur)
                    else:
                        copy_into(src, cur)
                    n += 1
                except Exception as exc:
                    print(f"! {src}: {exc}")
            if clipboard_mode == "cut":
                clipboard = []
                clipboard_mode = None
            print(t("pasted_ok", n=n))
            continue

        if low == "rn":
            if not _require_write():
                continue
            if not picked:
                print(t("nothing_sel"))
                continue
            if len(picked) != 1:
                print(t("must_one"))
                continue
            src = picked[0]
            try:
                new_name = input(f"  {t('prompt_rename')}: ").strip()
            except EOFError:
                continue
            if not new_name:
                continue
            new_name = os.path.basename(new_name)
            target = src.parent / new_name
            if target.exists():
                print("! 目标已存在 / target exists")
                continue
            try:
                src.rename(target)
                picked = [target]
                print(t("renamed_ok", old=src.name, new=new_name))
                _debug_log(f"renamed: {src} -> {target}")
            except Exception as exc:
                print(f"! {exc}")
            continue

        if low == "at":
            if not _require_write():
                continue
            if not picked:
                print(t("nothing_sel"))
                continue
            if len(picked) != 1:
                print(t("must_one"))
                continue
            _edit_attrs(picked[0])
            continue

        # 路径输入
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = cur / p
        try:
            p = p.resolve()
        except OSError:
            pass
        if p.exists():
            if p.is_dir():
                cur = p
            else:
                if p in picked:
                    picked.remove(p)
                else:
                    picked.append(p)
        else:
            print(t("err_not_exist"))


# =========================================================================== #
#                              直接运行入口                                    #
# =========================================================================== #

def _main():
    """直接运行本文件时启动文件管理器（读写模式）。"""
    print("═" * 72)
    print(f"  cfdialog v0.3.0  |  dir: {LIB_DIR}")
    print(f"  language: {_LANG}  |  debug: {_DEBUG}")
    print("═" * 72)
    try:
        file_manager(access="readwrite")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    except Exception as exc:
        _debug_log(f"file_manager crashed: {exc}")
        print(f"! {exc}")


if __name__ == "__main__":
    _main()