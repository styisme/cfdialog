**简体中文** | [English](README_EN.md)

# cfdialog

> 单文件、零依赖、跨平台 CLI 文件对话框库。

[![CI](https://github.com/styisme/cfdialog/actions/workflows/ci.yml/badge.svg)](https://github.com/styisme/cfdialog/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.3.0-3776AB)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Made with AI](https://img.shields.io/badge/made%20with-AI-FF6B6B)](docs/AI_DISCLOSURE.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()

---

## ⚠️ AI 生成声明

> **本项目由 AI 辅助生成。**
>
> 遵循 [AI 开发规范](https://github.com/styisme/ai-development-guidelines)，在此明确披露：
> - **AI 深度参与部分**：单文件架构重构、CLI 浏览器引擎、i18n 系统、文件管理器、`demo.py` 测试套件、`gen_*.py` 代码生成器、CI 流水线。
> - **开发者负责部分**：需求定义、Android/Termux/Pydroid 真机验证、CI 架构决策、语言包审校、Bug 定位与最终发布决策。
>
> 关于 AI 参与范围与比例的详细说明，请见 [docs/AI_DISCLOSURE.md](docs/AI_DISCLOSURE.md)。

---

## 📦 版本与溯源

当前版本：**v0.3.0**。完整历史见 [CHANGELOG.md](CHANGELOG.md)。

## ✨ 核心特性

| 特性 | 说明 |
| --- | --- |
| 交互式 CLI 浏览器 | 数字选择、目录跳转、返回上级、返回起点、多选、隐藏文件 |
| 两种读取模式 | `path` 只给路径 / `copy` 自动复制到工作目录 |
| 扩展名过滤 | 单个、多个、不限制 |
| 文件管理器 | 只读 / 读写；删除 / 复制 / 剪切 / 粘贴 / 重命名 / 打开 / 属性 |
| 保存时自由命名 | 仅保存单个文件时可用 |
| Windows 分区 | 含无盘符分区，任意页面按 `g` 切换 |
| 语言包 | 内置 zh_CN / en，其余从 `lg/*.txt` 按需加载 |
| 调试开关 | `ts.txt` 控制 log 保存与 `force_language` |
| 自动提权 | Windows UAC / Android root / Linux sudo-su |
| 直接运行即用 | `python cfdialog.py` 打开文件管理器（读写） |

## 🚀 快速开始

### 依赖

- Python ≥ 3.8
- 仅标准库，无第三方运行时依赖

### 示例

```python
from cfdialog import (
    pick_file, pick_folder, save, file_manager,
    set_language, get_language,
)

# 文件选择器：单选，只给路径
p = pick_file(mode="path")

# 多选，复制到 ./imported
ps = pick_file(multiple=True, mode="copy", work_dir="./imported",
               extensions=[".txt", ".md"])

# 文件夹选择器
d = pick_folder()

# 保存：允许用户自定义文件名
out = save("report.txt", free_name=True)

# 批量复制
save(["a.txt", "b.txt"], mode="copy")

# 文件管理器
file_manager(access="readwrite")     # 或 access="readonly"

# 语言
print(get_language())                # 例如 "zh_CN"
set_language("ja")
```

### 直接运行

```bash
python cfdialog.py
```

打开读写模式的文件管理器，起始目录为当前工作目录。

## 📁 目录结构

```
cfdialog/
├── cfdialog.py          # 单文件运行时库
├── lg/                  # 外部语言包
├── ts.txt               # 调试配置
├── README.md / README_EN.md
├── CHANGELOG.md
├── CONTRIBUTING.md / CONTRIBUTING_EN.md
├── DEVELOPMENT.md / 开发文档.md   # 由 tools/gen_docs.py 生成
├── docs/
│   ├── AI_DISCLOSURE.md
│   └── DEVELOPMENT_CONSTRAINTS.md
├── tools/               # 开发辅助
├── examples/            # 可运行示例
├── tests/               # unittest 门禁
├── dist/cfdialog-lite/  # 最小分发
└── pyproject.toml
```

## 🔑 核心 API

```python
pick_file(multiple=False, mode="copy", work_dir=None,
          start_dir=None, extensions=None, overwrite=False,
          show_hidden=False, prompt=None, lang=None)

pick_folder(multiple=False, mode="path", work_dir=None,
            start_dir=None, show_hidden=False,
            prompt=None, lang=None)

pick(select="file", multiple=False, mode="path",
     work_dir=None, start_dir=None, extensions=None,
     overwrite=False, show_hidden=False,
     prompt=None, lang=None)

save(sources=None, target_dir=None, mode="path",
     work_dir=None, free_name=False, default_name=None,
     overwrite=False, on_progress=None,
     start_dir=None, show_hidden=False,
     prompt=None, lang=None)

file_manager(start_dir=None, access="readwrite",
             show_hidden=False, prompt=None, lang=None)
```

返回约定：

| 函数 | 单选 | 多选 | 取消 |
| --- | --- | --- | --- |
| `pick_file(mode='path')` | `Path` | `List[Path]` | `BrowserCancelled` |
| `pick_file(mode='copy')` | `Path`（副本） | `List[Path]` | `BrowserCancelled` |
| `pick_folder()` | `Path` | `List[Path]` | `BrowserCancelled` |
| `save(mode='path')` | `Path`（目录） | — | `None` |
| `save(mode='copy')` | `Path`（副本） | `List[Path]` | `None` |
| `file_manager()` | `None` | — | — |

## 🗂 文件管理器

```python
file_manager(access="readonly")     # 禁用 rm / ct / ps / rn / at
file_manager(access="readwrite")    # 全部可用
```

只读模式仍可**复制到内存剪贴板**（`cp`）和**打开**（`op`），但禁用一切写盘操作。

## 🌐 语言包

优先级从高到低：

```
ts.txt force_language  →  单次 lang= 参数  →  set_language()  →  detect_language()  →  en
```

内置仅 `zh_CN` / `en`；其他语言代码在运行时自动从 `lg/<code>.txt` 加载，缺失回退英语。语言包格式：

```text
# code=de
# name=Deutsch
# name_en=German
# native_name=Deutsch

prompt_folder=Ordner auswählen
prompt_file=Datei auswählen
```

运行时注册：

```python
from cfdialog import register_language, set_language
register_language("de", {"prompt_folder": "Ordner auswählen"})
set_language("de")
```

## ⚙️ 调试开关

`ts.txt`：

```ini
log=true
log_dir=log
force_language=zh_CN
```

- `log`：开启后写 `log/YYYYMMDD.txt`
- `log_dir`：相对库目录
- `force_language`：覆盖一切语言来源；`none` 或留空表示不强制

编辑后调用 `reload_debug_config()` 立即生效。

## 💽 分区切换

Windows 上包含盘符（C:、D:…）与**无盘符卷**；任意页面按 `g` 打开分区选择器。

```python
from cfdialog import list_partitions
for p in list_partitions():
    print(p["name"], p["path"], p["label"], p["type"])
```

## ⌨️ 键位表

| 键 | 作用 |
| --- | --- |
| `1` `2` `3` | 进入目录 / 选中文件 |
| `0` / `b` / `..` | 返回上级 |
| `r` / `~` | 回到起点 |
| `s` | 选中当前目录 |
| `s<数字>` | 切换编号条目 |
| `a` / `c` / `d` | 多选：全选 / 清空 / 完成 |
| `g` | 切换分区 |
| `h` | 切换隐藏文件 |
| `q` | 取消（抛 `BrowserCancelled`） |
| 直接路径 | 跳转 / 选中 |
| **管理器专用** | |
| `rm` | 删除（只读禁用） |
| `cp` / `ct` | 复制 / 剪切到剪贴板 |
| `ps` | 粘贴（只读禁用） |
| `rn` | 重命名（只读禁用） |
| `op` | 打开（须恰好一项） |
| `at` | 查看 / 修改属性（须恰好一项，只读禁用） |
| `info` / `ls` | 查看属性 / 列出已选 |

## ❓ FAQ

**Q1. 为什么 Android 上自动提权会让程序退出？**
`su -c` 会新开 root 进程；父进程 `sys.exit(0)` 后原终端就“结束”了。建议 Android 上 `set_auto_elevate(False)`，需要时手动提权。

**Q2. 相对路径按哪个目录解析？**
`Path.cwd()`——运行目录，不是脚本目录。需要改基准就 `os.chdir()`。

**Q3. 扩展名过滤为什么对目录不生效？**
让用户能进子目录查找匹配文件；过滤目录会破坏导航。

**Q4. 语言包不存在会怎样？**
回退英语，不报错。加载尝试记入 log（若开启）。

**Q5. 只读模式下 `cp` 为什么可用？**
`cp` 只写内存剪贴板；`ps` 才真正写盘，所以只读禁用。

## 📚 关联文档

- [CHANGELOG.md](CHANGELOG.md) — 版本历史
- [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献指南
- [DEVELOPMENT.md](DEVELOPMENT.md) / [开发文档.md](开发文档.md) — 开发文档（由 `tools/gen_docs.py` 生成）
- [docs/AI_DISCLOSURE.md](docs/AI_DISCLOSURE.md) — AI 参与声明
- [docs/DEVELOPMENT_CONSTRAINTS.md](docs/DEVELOPMENT_CONSTRAINTS.md) — 开发约束与诚实声明

## 🤝 致谢

- 本项目在开发过程中使用了 **DeepSeek** 提供的辅助（代码生成、文档撰写、测试用例设计、语言包整理），在此致谢。
- 感谢所有测试与反馈过 cfdialog 的用户。
- 本项目只依赖 Python 标准库，不含任何第三方运行时依赖。

## 📜 协议

[MIT License](LICENSE)。