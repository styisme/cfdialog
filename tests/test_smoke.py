#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_smoke.py — CI 门禁测试（零依赖，纯 unittest）

覆盖：
  * import、常量、lg/ 存在
  * 扩展名归一化
  * 语言切换 / 注册 / 移除内置拒绝
  * 分区列举
  * copy_into（含重名自动改名）
  * save(target_dir=...) 与缺失源异常

不覆盖：
  * pick_* / file_manager（需要交互）
  * demo.py --auto 的 T02 "ar"（已知缺 lg/ar.txt，见 ci.yml 注释）
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cfdialog  # noqa: E402

# 测试环境不需要提权，避免 _maybe_elevate 触发 input()
cfdialog.set_auto_elevate(False)


class TestConstants(unittest.TestCase):
    def test_lib_dir(self):
        self.assertTrue(cfdialog.LIB_DIR.is_dir())
        self.assertTrue((cfdialog.LIB_DIR / "cfdialog.py").is_file())

    def test_builtin_languages(self):
        self.assertIn("en", cfdialog.BUILTIN_LANGUAGES)
        self.assertIn("zh_CN", cfdialog.BUILTIN_LANGUAGES)

    def test_lg_dir(self):
        self.assertTrue(cfdialog.LG_DIR.is_dir())

    def test_browser_cancelled_is_exception(self):
        self.assertTrue(issubclass(cfdialog.BrowserCancelled, Exception))


class TestExtensions(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(cfdialog._normalize_extensions(None))

    def test_wildcard(self):
        self.assertIsNone(cfdialog._normalize_extensions("*"))
        self.assertIsNone(cfdialog._normalize_extensions("*.*"))

    def test_single(self):
        self.assertEqual(
            cfdialog._normalize_extensions(".txt"),
            frozenset({".txt"}),
        )

    def test_multiple(self):
        self.assertEqual(
            cfdialog._normalize_extensions([".md", "CSV", "*.py"]),
            frozenset({".md", ".csv", ".py"}),
        )


class TestLanguage(unittest.TestCase):
    def test_get_language(self):
        self.assertIsInstance(cfdialog.get_language(), str)

    def test_set_language_en(self):
        self.assertEqual(cfdialog.set_language("en"), "en")

    def test_set_language_zh_cn(self):
        self.assertEqual(cfdialog.set_language("zh-CN"), "zh_CN")

    def test_set_language_zh_tw(self):
        # 需要 lg/zh_TW.txt 存在
        self.assertEqual(cfdialog.set_language("zh-Hant"), "zh_TW")

    def test_set_language_unknown(self):
        # 未知语言回退到 en
        self.assertEqual(cfdialog.set_language("xx-YY"), "en")

    def test_register_unregister(self):
        code = cfdialog.register_language("test_xx", {"prompt_file": "test"})
        self.assertEqual(code, "test_xx")
        self.assertTrue(cfdialog.unregister_language("test_xx"))

    def test_cannot_unregister_builtin(self):
        with self.assertRaises(ValueError):
            cfdialog.unregister_language("en")

    def test_list_languages(self):
        langs = cfdialog.list_languages()
        self.assertIn("en", langs)
        self.assertIn("zh_CN", langs)


class TestPartitions(unittest.TestCase):
    def test_list_partitions(self):
        parts = cfdialog.list_partitions()
        self.assertIsInstance(parts, list)
        if os.name == "posix":
            self.assertGreater(len(parts), 0)
            self.assertTrue(all("path" in p for p in parts))


class TestCopy(unittest.TestCase):
    def test_copy_into(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "a.txt"
            src.write_text("hello", encoding="utf-8")
            dst = td / "out"
            r = cfdialog.copy_into(src, dst)
            self.assertTrue(r.is_file())
            self.assertEqual(r.read_text(encoding="utf-8"), "hello")

    def test_copy_into_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "a.txt"
            src.write_text("hello", encoding="utf-8")
            dst = td / "out"
            r1 = cfdialog.copy_into(src, dst)
            r2 = cfdialog.copy_into(src, dst)
            self.assertNotEqual(r1, r2)
            self.assertTrue(r2.name.startswith("a_"))

    def test_copy_into_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            with self.assertRaises(FileNotFoundError):
                cfdialog.copy_into(td / "nope.txt", td / "out")


class TestSave(unittest.TestCase):
    def test_save_target_dir(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "a.txt"
            src.write_text("hello", encoding="utf-8")
            target = td / "out"
            out = cfdialog.save(sources=src, target_dir=target, mode="copy")
            self.assertTrue(out.is_file())

    def test_save_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            with self.assertRaises(FileNotFoundError):
                cfdialog.save(sources=td / "nope.txt",
                              target_dir=td / "out", mode="copy")


if __name__ == "__main__":
    unittest.main()
