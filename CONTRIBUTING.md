# 贡献指南

**简体中文** | [English](CONTRIBUTING_EN.md)

感谢参与 **cfdialog** 的开发！本项目采用轻量但明确的源代码管理规范：**Conventional Commits + SemVer 2.0.0 + CHANGELOG**。

> 相关文档：[README](README.md) | [CHANGELOG](CHANGELOG.md) | [AI 披露](docs/AI_DISCLOSURE.md) | [开发约束](docs/DEVELOPMENT_CONSTRAINTS.md)。

---

## ⚠️ 关于 AI 生成代码

遵循 [AI 开发规范](https://github.com/styisme/ai-development-guidelines)，本项目绝大多数代码由 **AI 辅助生成**（尤其是单文件架构、i18n 系统、`demo.py` 测试套件）。

提交 PR 时请务必：
- 说明改动是否由 AI 生成。
- **人工验证过功能**（必须在本地跑过 `python -m unittest discover -s tests -v`，不能只看 CI）。
- 如果你也是用 AI 改的，请在 PR 描述里注明模型和提示词方向。

---

## 本地开发

### 环境要求

| 组件 | 版本 |
|---|---|
| Python | ≥ 3.8 |
| 依赖 | 无（仅标准库） |
| 测试 | `unittest`（标准库） |
| CI | GitHub Actions |

### 运行 / 测试

```bash
git clone https://github.com/styisme/cfdialog.git
cd cfdialog

python -m unittest discover -s tests -v
python tools/demo.py --list-langs
python tools/demo.py --auto --ui en < /dev/null
python cfdialog.py          # 直接运行文件管理器
```

### 工具脚本

| 脚本 | 作用 |
|---|---|
| `tools/demo.py` | 可用性测试 / 交互菜单 / `--auto` / `--list-langs` |
| `tools/gen_docs.py` | 生成 README / DEVELOPMENT / 开发文档（不带 `--out` 时写到仓库根，会覆盖现有文档） |
| `tools/gen_lang_packs.py` | 批量生成 `lg/*.txt` |
| `tools/make_custom_lang.py` | 交互式做单个语言包 |

---

## 项目结构

```
cfdialog/
├── cfdialog.py          # 单文件运行时库
├── lg/                  # 外部语言包
├── ts.txt               # 调试配置
├── README.md / README_EN.md
├── CHANGELOG.md
├── CONTRIBUTING.md / CONTRIBUTING_EN.md
├── DEVELOPMENT.md / 开发文档.md
├── docs/
│   ├── AI_DISCLOSURE.md
│   └── DEVELOPMENT_CONSTRAINTS.md
├── tools/
├── examples/
├── tests/
├── dist/cfdialog-lite/
└── pyproject.toml
```

---

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```
<type>(<scope>): <subject>
```

### 允许的 type

`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `build` / `ci` / `chore`

### 常用 scope

`browser` / `manager` / `i18n` / `cli` / `elevation` / `partitions` / `tests` / `docs`

---

## 分支模型

| 分支 | 用途 |
|---|---|
| `main` | 稳定分支 |
| `feat/xxx` | 功能分支 |
| `fix/xxx` | 修复分支 |

---

## Pull Request 流程

1. Fork 仓库
2. `git checkout -b feat/your-feature`
3. 改代码 + 本地跑测试
4. Conventional Commits 提交
5. Push 并发起 PR
6. 等 CI 通过 + Review

### PR 描述应包含

```markdown
## 变更内容
简述做了什么

## 变更类型
- [ ] feat / fix / refactor / docs / chore

## 关联 Issue
Closes #123

## 测试方式
- [ ] python -m unittest discover -s tests -v 通过
- [ ] python tools/demo.py --list-langs 通过
- [ ] python -m compileall -q cfdialog.py tools examples 通过

## 是否使用 AI 生成
- [ ] 是（请说明模型和人工验证内容）
- [ ] 否
```

---

## 版本号规则

遵循 [Semantic Versioning 2.0.0](https://semver.org/lang/zh-CN/)：

| 变更 | 版本号递增 |
|---|---|
| 不兼容变更 | **MAJOR** |
| 向后兼容的新功能 | **MINOR** |
| Bug 修复 | **PATCH** |

⚠️ **重要**：本项目**没有**自动化版本号注入。发布前必须手动：

1. 更新 `cfdialog.py` 中的 `LIB_VERSION`（如果存在）
2. 更新 `README.md` / `README_EN.md` 顶部徽章的版本号
3. 在 `CHANGELOG.md` 中添加 `## [x.y.z] - YYYY-MM-DD` 段

---

## 常见问题排查

**Q: 测试报 `FileNotFoundError: cfdialog.py`？**
A: 必须在仓库根运行 `python -m unittest discover -s tests -v`，`tests/test_smoke.py` 通过 `parents[1]` 定位仓库根。

**Q: `tools/demo.py --list-langs` 少了几种语言？**
A: 检查 `lg/` 下是否齐全（应含 zh_TW/ja/ko/ru/fr/es/ar）。`ar` 为占位包，`prompt_*` 是阿拉伯语，其余英文。

**Q: `gen_docs.py` 把文档写到 `tools/` 了？**
A: 不带 `--out` 时默认写到仓库根（已有 patch）。在仓库根执行 `python tools/gen_docs.py` 即写到根目录。

**Q: CI 的 `demo --auto` 是红的？**
A: 该 job 是 informational（`continue-on-error: true`）。点击进 Summary / Artifacts 查看完整输出。若要把 `ar` 那条修掉，见 `docs/DEVELOPMENT_CONSTRAINTS.md`。

**Q: 只读模式下 `cp` 为什么可用？**
A: `cp` 只写内存剪贴板；`ps` 才真正写盘，所以只读禁用。
