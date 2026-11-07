# 安全警告 / Security Notice

**简体中文** 在上，**English** 在下。
Chinese first, English below.

> 本文档描述 cfdialog 的**已知风险面**。它是工具，不是沙箱。使用前请读完与你相关的部分。
> This document describes cfdialog's **known risk surface**. It is a tool, not a sandbox. Read the parts relevant to you before use.

相关文档：[README](README.md) / [README_EN](README_EN.md) / [AI 披露](docs/AI_DISCLOSURE.md) / [开发约束](docs/DEVELOPMENT_CONSTRAINTS.md)。

---

## 🇨🇳 简体中文

### 1. 提权：这是最高风险项

cfdialog 会在**首次**调用 `pick_*` / `save_*` / `file_manager` 时尝试自动提权：

| 平台 | 机制 | 风险 |
|---|---|---|
| Windows | `ShellExecuteW("runas", ...)` (UAC) | 会弹出系统 UAC 窗口；用户同意后新进程以管理员身份运行 |
| Android | `su -c "<cmd>"` | 会启动一个 root 子进程；父进程**立即退出**，原终端会话丢失 |
| Linux / macOS | `sudo` 优先，其次 `su` | 输入密码后整个进程以 root 运行 |

**风险**：

- 提权后，**整个库的所有文件操作都以 root / Administrator 身份执行**，包括删除、重命名、写入系统目录。
- 提权后的进程**不再受你的用户权限约束**。一个误操作（例如在 `/` 下执行 `rm`）后果不可恢复。
- Android 上 `su -c` 会脱离原终端，`ctrl-c`、`SIGINT`、终端历史都会失效。

**建议**：

```python
import cfdialog
cfdialog.set_auto_elevate(False)   # 全局关闭自动提权
```

需要提权时，显式调用：

```python
cfdialog.request_elevation(interactive=True)
```

并在自己的代码里对文件操作做额外校验（路径白名单、确认弹窗等）。

### 2. 文件删除不可恢复

`file_manager(access="readwrite")` 里的 `rm` 命令**直接删除**，不进入回收站、不做备份：

```python
file_manager(access="readwrite")
# 用户输入 rm + y 后，_remove_path() 会：
#   - 目录：shutil.rmtree()
#   - 文件：Path.unlink()
```

`rm` 会作用于**所有已选中的条目**（`sa` 全选后 `rm` 尤其危险）。删除是立即的，不可撤销。

**建议**：在只读环境下使用 `access="readonly"`；需要写操作时，对 `file_manager` 加二次确认包装。

### 3. 系统分区与无盘符卷

`list_partitions()` 和 `g` 键会列出：

- Windows：`C:\`、`D:\` 等盘符，以及**无盘符的卷**（`\\?\Volume{...}\`）
- POSIX：`/`、`/mnt`、`/media`、`/Volumes`、`/run/media` 下的挂载点

这些路径下可能包含系统分区、EFI 分区、用户主目录。进入后如果执行写操作（`rm` / `ps` / `rn` / `at`），**会真的修改系统分区**。

**建议**：用 `start_dir=` 把起始目录限定在用户数据目录内；不要在生产环境或无人值守脚本里开放 `g` 键。

### 4. 符号链接与路径穿越

`copy_into()` / `_move_into()` / `_remove_path()` 会跟随符号链接：

- `_remove_path(p)` 对**目录符号链接**会做 `unlink()`（删链接本身，不删目标），但对**普通目录**会 `shutil.rmtree()`（删整个目录树）。
- 如果选中的是符号链接指向的目录，`rm` 删的是链接本身；但如果用户先进入该目录、再删里面的文件，删的就是**真实目标**。
- `copy_into()` 用 `shutil.copytree()` 递归复制，遇到循环符号链接可能报错或复制大量无关内容。

`save(free_name=True)` 会让用户自定义文件名，`_prompt_free_name()` 用 `os.path.basename()` 剥掉路径成分，但它**不会阻止** `..`、绝对路径、NTFS 保留名（`CON`、`NUL`）等问题名。

**建议**：处理不可信输入时，在调用 cfdialog 前自己校验路径；不要对来路不明的目标目录开启写权限。

### 5. 不可信环境使用

cfdialog 是**面向人类交互**的终端工具，不适合：

- **无人值守的 CI / 定时任务**：`_browse()` 需要 `input()`，没有 stdin 会立刻抛 `BrowserCancelled`。
- **多用户共享终端**：剪贴板是**进程内内存变量**，不跨进程；但文件管理器可以删除任意已授权路径下的内容。
- **接受远程输入的服务器**：用户的 `input()` 可以是任意路径，包括 `/etc/passwd`、`~/.ssh/`。

**建议**：CI 里用 `pick_file(mode="path")` 前先 `set_auto_elevate(False)`，并显式传入 `start_dir` 与 `extensions`。

### 6. 日志与调试信息可能泄露本地路径

`ts.txt` 里 `log=true` 时，`_debug_log()` 会把以下内容写入 `log/YYYYMMDD.txt`：

- 完整的源路径与目标路径（`copy: /home/you/secret.txt -> /mnt/usb/secret.txt`）
- 语言包加载路径
- 探测到的系统语言

这些日志**不会被自动清理**，且 `log/` 目录在库目录下，可能被打包进发行版或误上传。

**建议**：

- 生产环境保持 `log=false`。
- 分享日志前手动 review，或 `grep` 掉本地路径。
- `log/` 已在 `.gitignore` 里（`log/` 一行），但**不要**把它打进 `dist/`。

### 7. 语言包是可替换的外部文件

`lg/<code>.txt` 是纯文本，`_load_lang_pack()` 会**直接读取并解析**。如果攻击者能写 `lg/` 目录，他可以：

- 把提示文案改成误导性内容（例如把 `confirm_delete` 从“确认删除 N 个条目？”改成“按 Enter 继续”）。
- 把 `readonly_denied` 改掉，让只读模式看起来像可写。

cfdialog 不校验语言包的来源或哈希。

**建议**：不要把 `lg/` 暴露给不可信用户；发布时用打包后的文件（`dist/cfdialog-lite/`）而非源码目录。

### 8. `ts.txt` 的 `force_language` 可以覆盖一切

`ts.txt` 里的 `force_language` 优先级**高于**：

- 调用方的 `lang=` 参数
- `set_language()`
- `detect_language()`

如果攻击者能写 `ts.txt`，就能强制界面显示某种语言，配合第 7 条可以构造误导性 UI。

**建议**：`ts.txt` 只放在库目录，不要从网络或用户可写目录加载。

---

### 如何报告安全漏洞

**不要**开公开 issue。请通过以下方式之一联系维护者：

- 邮件：`sty_20120423@petalmail.com`（主题加 `[cfdialog-security]`）
- GitHub Security Advisories（仓库 **Security** 标签页 → **Report a vulnerability**）

请包含：

1. 受影响的版本（`pyproject.toml` 或 `git describe --tags`）
2. 复现步骤
3. 影响范围（能否删除文件 / 提权 / 读取越权路径）
4. 建议的修复方向（可选）

我们会在 **7 天内**确认收到，**30 天内**给出处理计划。修复发布后会在 [CHANGELOG](CHANGELOG.md) 的 Security 段注明。

### 不在范围内

以下**不算**安全漏洞，请不要报告：

- 用户主动输入 `/` 后执行 `rm` 导致系统损坏（这是用户操作，不是库的 bug）。
- 用户手动把 `lg/en.txt` 改成恶意内容（这是用户对本地文件的修改）。
- 在 `access="readwrite"` 下删除用户自己选的文件（这是预期行为）。
- 提权后执行了危险操作（提权本身就是高风险，见第 1 条）。

---

## 🇬🇧 English

### 1. Elevation — the highest-risk item

cfdialog attempts auto-elevation on the **first** call to `pick_*` / `save_*` / `file_manager`:

| Platform | Mechanism | Risk |
|---|---|---|
| Windows | `ShellExecuteW("runas", ...)` (UAC) | System UAC prompt; the new process runs as Administrator |
| Android | `su -c "<cmd>"` | Spawns a root child; parent exits **immediately**, terminal session is lost |
| Linux / macOS | `sudo` first, then `su` | After password, the whole process runs as root |

**Risks**:

- After elevation, **every file operation runs as root / Administrator**, including delete, rename, and writes into system directories.
- The elevated process is **no longer bound by your user permissions**. A mistake (e.g. `rm` under `/`) is unrecoverable.
- On Android, `su -c` detaches from the terminal; `ctrl-c`, `SIGINT`, and shell history no longer reach the process.

**Recommendation**:

```python
import cfdialog
cfdialog.set_auto_elevate(False)   # disable globally
```

When elevation is needed, call it explicitly:

```python
cfdialog.request_elevation(interactive=True)
```

and add your own validation (path allowlist, confirmation prompt) around file operations.

### 2. Deletion is irreversible

The `rm` command inside `file_manager(access="readwrite")` **deletes directly** — no recycle bin, no backup:

```python
file_manager(access="readwrite")
# After the user types `rm` + `y`, _remove_path() does:
#   - directory: shutil.rmtree()
#   - file:      Path.unlink()
```

`rm` applies to **all selected items** (especially dangerous after `sa` / select-all). Deletion is immediate and cannot be undone.

**Recommendation**: use `access="readonly"` in read-only contexts; wrap `file_manager` with an extra confirmation when write access is needed.

### 3. System partitions and letter-less volumes

`list_partitions()` and the `g` key expose:

- Windows: drive letters `C:\`, `D:\`, … and **letter-less volumes** (`\\?\Volume{...}\`)
- POSIX: mount points under `/`, `/mnt`, `/media`, `/Volumes`, `/run/media`

These may include system partitions, EFI partitions, and user home directories. Write operations (`rm` / `ps` / `rn` / `at`) inside them **really modify the system partition**.

**Recommendation**: pin `start_dir=` to a user-data directory; do not expose the `g` key in production or unattended scripts.

### 4. Symlinks and path traversal

`copy_into()` / `_move_into()` / `_remove_path()` follow symlinks:

- `_remove_path(p)` uses `unlink()` for **directory symlinks** (removes the link only), but `shutil.rmtree()` for **real directories** (removes the whole tree).
- If the selection is a symlinked directory, `rm` removes the link; but if the user navigates into it and deletes files, those are the **real targets**.
- `copy_into()` uses `shutil.copytree()`, which may fail or copy unexpected content on cyclic symlinks.

`save(free_name=True)` lets the user supply a name; `_prompt_free_name()` strips path components via `os.path.basename()`, but it does **not** reject `..`, absolute paths, or reserved Windows names (`CON`, `NUL`).

**Recommendation**: validate paths yourself before calling cfdialog when input is untrusted; do not enable write access on directories you don't control.

### 5. Untrusted environments

cfdialog is a **human-interactive terminal tool**; it is unsuitable for:

- **Unattended CI / cron**: `_browse()` needs `input()`; without stdin it raises `BrowserCancelled` immediately.
- **Shared multi-user terminals**: the clipboard is an **in-process variable**, but `file_manager` can delete anything in the accessible tree.
- **Servers accepting remote input**: the user's `input()` can be any path, including `/etc/passwd`, `~/.ssh/`.

**Recommendation**: in CI, call `set_auto_elevate(False)` before `pick_file(mode="path")`, and pass explicit `start_dir` and `extensions`.

### 6. Logs and debug output may leak local paths

When `ts.txt` has `log=true`, `_debug_log()` writes the following into `log/YYYYMMDD.txt`:

- Full source and target paths (`copy: /home/you/secret.txt -> /mnt/usb/secret.txt`)
- Language pack load paths
- Detected system language

These logs are **never auto-rotated**, live under the library directory, and may end up in release artifacts or accidental uploads.

**Recommendation**:

- Keep `log=false` in production.
- Review logs before sharing, or `grep` out local paths.
- `log/` is already in `.gitignore`, but **do not** package it into `dist/`.

### 7. Language packs are replaceable external files

`lg/<code>.txt` is plain text; `_load_lang_pack()` reads and parses it **without integrity checks**. Anyone who can write to `lg/` can:

- Rewrite prompts to be misleading (e.g. change `confirm_delete` from “Delete N items?” to “Press Enter to continue”).
- Rewrite `readonly_denied` so read-only mode looks writable.

cfdialog does not verify origin or hash of language packs.

**Recommendation**: do not expose `lg/` to untrusted users; ship the packaged `dist/cfdialog-lite/` rather than a source checkout.

### 8. `ts.txt` `force_language` overrides everything

`force_language` in `ts.txt` takes precedence **over**:

- the caller's `lang=` argument
- `set_language()`
- `detect_language()`

Anyone who can write `ts.txt` can force a specific UI language; combined with §7 this enables misleading UI.

**Recommendation**: keep `ts.txt` inside the library directory; never load it from a network or user-writable location.

---

### Reporting a vulnerability

**Do not** open a public issue. Contact the maintainer via one of:

- Email: `sty_20120423@petalmail.com` (subject prefix `[cfdialog-security]`)
- GitHub Security Advisories (repo **Security** tab → **Report a vulnerability**)

Please include:

1. Affected version (`pyproject.toml` or `git describe --tags`)
2. Steps to reproduce
3. Impact scope (file deletion / elevation / out-of-scope reads)
4. Suggested fix direction (optional)

We will acknowledge within **7 days** and provide a plan within **30 days**. Fixes are noted in the Security section of [CHANGELOG](CHANGELOG.md).

### Out of scope

The following are **not** vulnerabilities:

- Running `rm` under `/` after the user typed `/` themselves (user action, not a library bug).
- Manually editing `lg/en.txt` to malicious content (user modification of local files).
- Deleting files the user explicitly selected under `access="readwrite"` (expected behavior).
- Executing dangerous operations after elevation (elevation itself is high risk, see §1).

---

_Maintained alongside cfdialog. Last reviewed: 2026-11-08._
