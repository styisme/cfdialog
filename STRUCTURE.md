# Repository layout

```
.
├── cfdialog.py               # single-file runtime library (lg/ inlined as _PACKED_STRINGS)
├── lg/                       # external language packs (override _PACKED_STRINGS)
├── ts.txt                    # debug config (log / force_language)
│
├── README.md                 # 中文首页
├── README_EN.md              # English
├── CHANGELOG.md              # Keep a Changelog + SemVer
├── CONTRIBUTING.md           # 中文贡献指南
├── CONTRIBUTING_EN.md        # English
├── SECURITY.md               # 安全警告（中英双栏）
├── DEVELOPMENT.md            # English dev docs (generated)
├── 开发文档.md                # 中文 dev docs (generated)
├── STRUCTURE.md              # this file
├── LICENSE
│
├── pyproject.toml            # dynamic version + ruff + coverage + project metadata
├── .pre-commit-config.yaml   # ruff + pre-commit-hooks
├── .gitignore                # __pycache__ / *.bak / dist artifacts / log
│
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   └── workflows/
│       ├── ci.yml            # lint / syntax / test+coverage / demo / docs / demo-auto
│       └── publish.yml       # Trusted Publishing to PyPI
│
├── docs/
│   ├── AI_DISCLOSURE.md              # AI 参与范围 + 风险
│   └── DEVELOPMENT_CONSTRAINTS.md    # 环境约束 + 诚实声明 + 敏感模块清单
│
├── tests/
│   ├── __init__.py
│   └── test_smoke.py         # 22 条 unittest 门禁
│
├── tools/                    # dev helpers (THIS_DIR patched to repo root)
│   ├── README.md
│   ├── demo.py               # --auto / --list-langs / interactive menu
│   ├── gen_docs.py           # writes to repo root by default
│   ├── gen_lang_packs.py     # batch-generate lg/*.txt
│   ├── make_custom_lang.py   # interactive single pack
│   ├── bugreport.py          # collect env info for GitHub issues
│   └── organize_cfdialog_inplace.py
│
├── examples/                 # runnable examples (share the root cfdialog.py)
│   ├── notpad/               # cfnotepad.py + run.py + README.md
│   └── Terminal file organizer/  # main program.py + run.py + README.md
│
└── dist/
    ├── cfdialog-lite/        # minimal distribution (lib + lg only)
    └── cfdialog.zip          # ignored by .gitignore
```

## Run an example

```bash
python examples/<name>/run.py
```

## Run tests / lint

```bash
python -m unittest discover -s tests -v
python -m coverage run -m unittest discover -s tests && python -m coverage report
ruff check .
```

## Collect environment info for a bug report

```bash
python tools/bugreport.py | head -n 60
```

Paste the output into the "Environment" field of the Bug Report issue form.

## Regenerate docs / lang packs

```bash
python tools/gen_docs.py                 # writes to repo root (patched)
python tools/gen_docs.py --out /tmp/docs # explicit output dir
python tools/gen_lang_packs.py
```

> `tools/gen_docs.py` defaults to the repo root, regardless of CWD.
> `--out DIR` overrides it.

## Build (local check, no publish)

```bash
python -m build
unzip -l dist/*.whl | grep cfdialog.py
```

## Publish

Tag and publish a GitHub Release; `.github/workflows/publish.yml` builds
and uploads to PyPI via Trusted Publishing (OIDC, no token).