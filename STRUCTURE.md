# Repository layout

```
.
├── cfdialog.py          # single-file runtime library
├── lg/                  # external language packs
├── ts.txt               # debug config (log / force_language)
├── README.md
├── DEVELOPMENT.md
├── 开发文档.md
├── LICENSE
├── pyproject.toml
├── tools/               # dev helpers (demo, doc gen, lang pack gen)
├── examples/            # runnable examples (share the root cfdialog.py)
└── dist/
    └── cfdialog-lite/   # minimal distribution (lib + lg only)
```

## Run an example

```bash
python examples/<name>/run.py
```

## Regenerate docs / lang packs

```bash
python tools/gen_docs.py --out .
python tools/gen_lang_packs.py
```

> Note: `tools/gen_docs.py` writes to the current directory by default,
> so run it from the repository root with `--out .`.
