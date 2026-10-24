# tools/

| 脚本 | 作用 | 注意 |
|---|---|---|
| `demo.py` | 可用性测试 / 交互菜单 / `--auto` / `--list-langs` | `--auto` 全跑可当 smoke test；`--list-langs` 快速看语言 |
| `gen_docs.py` | 生成 README / DEVELOPMENT / 开发文档 | 不带 `--out` 时写到**仓库根**（会覆盖现有文档）；`--out DIR` 写到指定目录 |
| `gen_lang_packs.py` | 批量生成 `lg/*.txt` | 只覆盖 `PACKS` 里的 6 个语言（zh_TW/ja/ko/ru/fr/es），不含 `ar` |
| `make_custom_lang.py` | 交互式做单个语言包 | 输出到仓库根 `lg/`；`--code` / `--ref` 可非交互 |

全部脚本的 `THIS_DIR` 已指向仓库根，可在任意 CWD 运行。

## 已知问题

- `demo.py --auto` 里 T02 的 `("ar", "ar")`：仓库必须有 `lg/ar.txt` 才能过。
  本仓库已提供占位 `lg/ar.txt`（`prompt_*` 为阿拉伯语，其余英文），
  可用 `make_custom_lang.py --code ar --ref en` 继续完善。
- `gen_lang_packs.py` 不含 `ar`；新增 `ar` 请用 `make_custom_lang.py` 或手写 `lg/ar.txt`。
- `cfdialog.py` 的 `SUPPORTED_LANGUAGES` 声明了 `ar`，但只有 `lg/ar.txt` 存在时才能真正选中；
  缺失时 `set_language("ar")` 会回退到 `en`。

## 常用命令

```bash
python tools/demo.py --list-langs
python tools/demo.py --auto --ui en < /dev/null
python tools/gen_docs.py              # 写到仓库根
python tools/gen_docs.py --out /tmp/x # 写到 /tmp/x
python tools/gen_lang_packs.py
```
