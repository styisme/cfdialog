# cfdialog — Development Documentation

> Version 0.3.0 | Python 3.8+
> Audience: contributors, integrators, reviewers.

## Table of Contents

1. [Design Goals](#1-design-goals)
2. [Architecture](#2-architecture)
3. [Public API](#3-public-api)
4. [Browser Engine](#4-browser-engine)
5. [File Manager](#5-file-manager)
6. [i18n System](#6-i18n-system)
7. [Debug System](#7-debug-system)
8. [Elevation](#8-elevation)
9. [Windows Partitions](#9-windows-partitions)
10. [Copy / Move Semantics](#10-copy--move-semantics)
11. [Extending](#11-extending)
12. [Testing](#12-testing)
13. [Release Checklist](#13-release-checklist)
14. [FAQ](#14-faq)
15. [Acknowledgements](#15-acknowledgements)

## 1. Design Goals

- **Single file**: `cfdialog.py` is the only runtime dependency. Easy to ship to Android, CI, embedded systems.
- **Zero third-party deps**: only the Python standard library.
- **Terminal-first**: works over SSH, in Termux, in Pydroid, in CI logs.
- **Extensible without forking**: languages and debug options are driven by plain text files that live next to the library.
- **Functional API**: `pick_*` / `save_*` / `file_manager` are module-level functions, no instances to manage.

## 2. Architecture

### 2.1 Layers

```text
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
```

### 2.2 Module Layout (single file)

| Section | Contents |
| --- | --- |
| Constants | `LIB_DIR`, `LG_DIR`, `LOG_DIR`, `TS_FILE`, `SUPPORTED_LANGUAGES`, `BUILTIN_LANGUAGES` |
| Exceptions | `BrowserCancelled` |
| Debug | `reload_debug_config`, `get_debug_config`, `_debug_log` |
| i18n | `_BUILTIN_STRINGS`, `_STRINGS`, `_LANG_META`, `_load_lang_pack`, `_t`, public language APIs |
| Elevation | `request_elevation`, `_relaunch_windows`, `_relaunch_root`, `_maybe_elevate` |
| Partitions | `list_partitions`, `_list_windows_partitions`, `_win_enumerate_volumes` |
| Extensions | `_normalize_extensions`, `_match_extension` |
| File ops | `copy_into`, `_move_into`, `_unique_path`, `_remove_path` |
| Browser | `_browse`, `_list_dir`, `_render_browse`, `_browse_partitions` |
| Pickers | `pick`, `pick_file`, `pick_folder` |
| Savers | `save`, `save_folder`, `_prompt_free_name` |
| Manager | `file_manager`, `_open_path`, `_is_readonly`, `_set_readonly`, `_is_hidden`, `_set_hidden` |
| Entry | `_main` (runs `file_manager(access='readwrite')`) |

## 3. Public API

### 3.1 Signature Summary

```python
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
```

### 3.2 Return Value Conventions

| Function | Single | Multiple | Cancel |
| --- | --- | --- | --- |
| `pick_file(mode='path')` | `Path` | `List[Path]` | `BrowserCancelled` |
| `pick_file(mode='copy')` | `Path` (copy) | `List[Path]` | `BrowserCancelled` |
| `pick_folder()` | `Path` | `List[Path]` | `BrowserCancelled` |
| `save(mode='path')` | `Path` (dir) | — | `None` |
| `save(mode='copy')` | `Path` (copy) | `List[Path]` | `None` |
| `save(free_name=True)` | `Path` (target file) | — | `None` |
| `file_manager()` | `None` | — | — |

## 4. Browser Engine

### 4.1 Main Loop

```text
while True:
    items = _list_dir(cur, show_hidden, exts, t)
    _render_browse(...)
    raw = input("> ").strip()
    dispatch(raw)
```

### 4.2 Dispatch Table

| Input | Handler |
| --- | --- |
| `q` / `quit` / `exit` | raise `BrowserCancelled` |
| `g` | open `_browse_partitions` and change `cur` |
| `b` / `back` / `..` | `cur = cur.parent` |
| `r` / `~` | `cur = origin` |
| `h` | flip `show_hidden` |
| `c` / `a` / `d` | multi-select: clear / all / done |
| `s` | pick current dir |
| `s<num>` | toggle item #num |
| `<num>` | enter dir or pick file |
| path string | resolve and jump / pick |

### 4.3 Rendering

`_render_browse` prints a fixed-width banner (72 columns), the current directory, optional format limit, optional hidden marker, optional selection counter, the item list, then the key hints.

`_format_size` produces compact sizes (`1.2K`, `3.4M`, `5.6G`).

## 5. File Manager

### 5.1 State

```python
cur            # current directory
origin         # the start_dir passed in
picked         # list[Path] of selected items
clipboard      # list[Path]
clipboard_mode # None | "copy" | "cut"
allow_write    # access == "readwrite"
```

### 5.2 Read-Only Restrictions

| Command | Read-only | Rationale |
| --- | --- | --- |
| `rm` | disabled | modifies disk |
| `ct` | disabled | a pending cut is destructive on paste |
| `ps` | disabled | writes to disk |
| `rn` | disabled | modifies disk |
| `at` | disabled | changes file attributes |
| `cp` | allowed | in-memory clipboard only |
| `op` | allowed | opens, does not modify |
| `info` / `ls` | allowed | read-only inspection |

### 5.3 Attributes

On Windows the manager uses `GetFileAttributesW` / `SetFileAttributesW` so the actual **read-only** and **hidden** bits are toggled.

On POSIX, read-only is toggled via `os.chmod`; the hidden flag is a no-op (POSIX hides files by leading dot only).

## 6. i18n System

### 6.1 Load Order

```text
1. Built-in _BUILTIN_STRINGS (zh_CN, en)
2. _load_lang_pack(code)   → lg/<code>.txt
3. _normalize_lang_code()  → alias map
4. Fallback to en
```

### 6.2 Pack Format

```text
# comments are metadata (leading '#')
# code=de
# name=Deutsch
# name_en=German
# native_name=Deutsch

prompt_folder=Ordner auswählen
prompt_file=Datei auswählen
...
```

Any key not present in the pack falls back to English at lookup time.

### 6.3 Priority

```text
ts.txt  force_language         ← highest
   ↓ none
per-call lang= argument
   ↓ None
global set_language()
   ↓ not called
detect_language()
   ↓ no match
en
```

## 7. Debug System

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

### 7.2 Global State

```python
_DEBUG = {
    "log": False,
    "log_dir": "log",
    "force_language": None,
}
```

`reload_debug_config()` re-reads the file. Call it after editing `ts.txt`.

`_debug_log(msg)` appends to `log/YYYYMMDD.txt` when `log=true`.

## 8. Elevation

### 8.1 Trigger

Elevation is **not** triggered at import. `_maybe_elevate()` runs on the **first** call to `pick_*`, `save_*`, or `file_manager`. A module-level `_ELEVATION_DONE` flag ensures it happens only once.

### 8.2 Platform Strategy

| Platform | Detection | Mechanism |
| --- | --- | --- |
| Windows | `IsUserAnAdmin()` | `ShellExecuteW("runas", ...)` (UAC) |
| Android | `os.geteuid() == 0` | `su -c "<cmd>"` |
| Linux / macOS | `os.geteuid() == 0` | `sudo` then `su` |

### 8.3 Return Values

| Value | Meaning |
| --- | --- |
| `already` | Already elevated |
| `relaunched` | Elevated process started; caller must `sys.exit(0)` |
| `denied` | User refused or elevation failed |
| `unavailable` | No elevation path (e.g. unrooted Android) |
| `not_needed` | Platform does not need elevation |

### 8.4 Android

`su -c` spawns a new root process and the terminal session is lost. The parent **must** exit immediately after seeing `relaunched`. For this reason the demo disables auto-elevation on Android.

## 9. Windows Partitions

### 9.1 Sources

- `GetLogicalDrives()` → drive letters (C:, D:, …)
- `FindFirstVolumeW` / `FindNextVolumeW` → all volumes incl. **letter-less**
- `GetVolumePathNamesForVolumeNameW` → mount points of each volume
- `GetVolumeInformationW` → volume label

### 9.2 Volume Filter

A volume is skipped if any of its mount points is already a drive letter returned by `GetLogicalDrives()`. Letter-less volumes are listed with their `\\?\Volume{...}\` device path, which `os.listdir` accepts.

## 10. Copy / Move Semantics

### 10.1 Name Clash

```python
def _unique_path(target: Path) -> Path:
    # a.txt -> a_1.txt -> a_2.txt
    # dir/  -> dir_1/ -> dir_2/
```

`overwrite=True` removes the existing target first; `False` picks a non-conflicting name.

### 10.2 Directory Copy

Directories are copied recursively via `shutil.copytree`. Files use `shutil.copy2` to preserve metadata.

### 10.3 Move

`_move_into` uses `shutil.move`, with the same collision policy.

## 11. Extending

### 11.1 New Language Pack

Either drop a `lg/<code>.txt` file or call `register_language()` at runtime.

### 11.2 New Select Mode

```python
if select not in ("file", "dir", "any", "executable"):
    ...

def accepts(p, is_dir):
    if select == "executable":
        return not is_dir and os.access(p, os.X_OK)
    ...
```

### 11.3 Custom Renderer

```python
import cfdialog, os

def my_render(cur, items, picked, multiple, prompt,
              show_hidden, exts, access, manager, t):
    os.system("clear")
    print(f"📁 {cur}")
    for i, (name, p, is_dir) in enumerate(items, 1):
        icon = "📂" if is_dir else "📄"
        print(f"  {i:>3}. {icon} {name}")

cfdialog._render_browse = my_render
```

### 11.4 Custom Copy

```python
import cfdialog
from pathlib import Path

_orig = cfdialog.copy_into

def my_copy(src, dst, overwrite=False):
    # keep symlinks as symlinks, etc.
    return _orig(src, dst, overwrite)

cfdialog.copy_into = my_copy
```

## 12. Testing

See `demo.py`. It offers:

- **Auto tests** — no interaction, good for CI
- **Manual tests** — step-by-step, interactive
- **Language menu** — list / switch / inspect
- **Partition viewer**
- **Debug viewer** + live `ts.txt` reload

```bash
python demo.py             # interactive menu
python demo.py --auto      # auto only
python demo.py --ui en     # UI in English
python demo.py --list-langs
```

## 13. Release Checklist

1. Bump `LIB_VERSION` in `cfdialog.py`.
2. Update `_BUILTIN_STRINGS` if new keys were added.
3. Regenerate language packs with `gen_lang_packs.py`.
4. Regenerate docs with `gen_docs.py`.
5. Exclude dev-only files from the release:
   - `gen_lang_packs.py`
   - `make_custom_lang.py`
   - `gen_docs.py`
   - `demo.py` (optional)
6. Verify `python cfdialog.py` opens the file manager.
7. Verify `ts.txt` still works (log on, force a language).

## 14. FAQ

### Q1. Why is the whole library in one file?

Distribution simplicity. Android/Termux, PyInstaller onefile, and CI runners all benefit from a single drop-in file.

### Q2. Why are language packs plain text?

So users can add a language without forking the library. A plain text pack is diffable, mergeable, and trivially editable on a phone.

### Q3. Why do I get `relaunched` and the process dies?

That is by design on Android and Windows. When `request_elevation` returns `relaunched`, the parent should call `sys.exit(0)`.

### Q4. Why is the extension filter not applied to directories?

So users can navigate. Filtering dirs would break navigation.

### Q5. Why does `file_manager` in read-only mode allow `cp`?

`cp` only stores picks in an in-memory clipboard. `ps` writes to disk and is therefore disabled.

## 15. Acknowledgements

- This project was developed with assistance from **DeepSeek** (code generation, documentation writing, test design, and language pack drafting). Sincere thanks.

- Thanks to everyone who tested cfdialog and sent feedback.

- The library depends on the Python standard library only; there are no third-party runtime dependencies.

---

*Generated by `gen_docs.py` · cfdialog v0.3.0*
