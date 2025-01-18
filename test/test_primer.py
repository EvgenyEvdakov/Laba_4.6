#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import unittest


sys.path.append("../src")
from primer import Staff, Worker


class TestStaff(unittest.TestCase):
    def setUp(self):
        """Инициализация данных перед каждым тестом."""
        self.staff = Staff()

    def test_add_worker(self):
        """Тест: добавление сотрудника."""
        self.staff.add("Иванов И.И.", "Инженер", 2015)
        self.assertEqual(len(self.staff.workers), 1)
        self.assertEqual(self.staff.workers[0].name, "Иванов И.И.")
        self.assertEqual(self.staff.workers[0].post, "Инженер")
        self.assertEqual(self.staff.workers[0].year, 2015)

    def test_select_workers(self):
        """Тест: выбор сотрудников по стажу."""
        self.staff.add("Иванов И.И.", "Инженер", 2015)
        self.staff.add("Петров П.П.", "Менеджер", 2010)
        selected = self.staff.select(10)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].name, "Петров П.П.")


if __name__ == "__main__":
    unittest.main()
