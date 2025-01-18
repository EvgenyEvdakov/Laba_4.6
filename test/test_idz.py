#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.append("../src")
from idz import DirectoryItem, XMLDataHandler, build_tree, get_directory_contents


class TestDirectoryItem(unittest.TestCase):
    def test_to_xml_and_from_xml(self):
        item = DirectoryItem(
            name="test_dir",
            path="/path/to/test_dir",
            is_dir=True,
            children=[
                DirectoryItem(name="file1.txt", path="/path/to/test_dir/file1.txt", is_dir=False),
                DirectoryItem(name="sub_dir", path="/path/to/test_dir/sub_dir", is_dir=True),
            ],
        )
        xml_element = item.to_xml_element()
        recreated_item = DirectoryItem.from_xml_element(xml_element)

        self.assertEqual(item, recreated_item)


class TestXMLDataHandler(unittest.TestCase):
    def test_save_and_load(self):
        item = DirectoryItem(
            name="test_dir",
            path="/path/to/test_dir",
            is_dir=True,
            children=[
                DirectoryItem(name="file1.txt", path="/path/to/test_dir/file1.txt", is_dir=False),
                DirectoryItem(name="sub_dir", path="/path/to/test_dir/sub_dir", is_dir=True),
            ],
        )

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name

        try:
            XMLDataHandler.save(item, filename)
            self.assertTrue(os.path.exists(filename))

            loaded_item = XMLDataHandler.load(filename)
            self.assertEqual(item, loaded_item)
        finally:
            os.remove(filename)


class TestUtilityFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        (self.test_dir / "file1.txt").touch()
        (self.test_dir / "file2.txt").touch()
        (self.test_dir / "subdir").mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_directory_contents(self):
        args = type("Namespace", (object,), {"a": True, "d": False, "f": False})
        contents = get_directory_contents(self.test_dir, args)

        expected = {self.test_dir / "file1.txt", self.test_dir / "file2.txt", self.test_dir / "subdir"}
        self.assertEqual(set(contents), expected)

    def test_build_tree(self):
        args = type("Namespace", (object,), {"a": True, "d": False, "f": False, "t": False})
        tree = build_tree(self.test_dir, args)

        self.assertEqual(tree.name, self.test_dir.name)
        self.assertEqual(tree.is_dir, True)
        self.assertEqual(len(tree.children), 3)
        self.assertTrue(any(child.name == "file1.txt" for child in tree.children))
        self.assertTrue(any(child.name == "file2.txt" for child in tree.children))
        self.assertTrue(any(child.name == "subdir" and child.is_dir for child in tree.children))


if __name__ == "__main__":
    unittest.main()
