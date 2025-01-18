#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional, Protocol


# Интерфейс для сохранения/загрузки данных
class DataHandler(Protocol):
    def save(self, data: "DirectoryItem", filename: str) -> None: ...

    def load(self, filename: str) -> "DirectoryItem": ...


# DataClass для представления файла или каталога
@dataclass
class DirectoryItem:
    name: str
    path: str
    is_dir: bool
    children: List["DirectoryItem"] = field(default_factory=list)

    def to_xml_element(self) -> ET.Element:
        """Конвертирует DirectoryItem в XML-элемент."""
        element = ET.Element("directory" if self.is_dir else "file", name=self.name, path=self.path)
        for child in self.children:
            element.append(child.to_xml_element())
        return element

    @staticmethod
    def from_xml_element(element: ET.Element) -> "DirectoryItem":
        """Создает DirectoryItem из XML-элемента."""
        children = [DirectoryItem.from_xml_element(child) for child in element]
        return DirectoryItem(
            name=element.get("name", ""),
            path=element.get("path", ""),
            is_dir=(element.tag == "directory"),
            children=children,
        )


class XMLDataHandler:
    """Класс для обработки данных XML формата."""

    @staticmethod
    def save(data: DirectoryItem, filename: str) -> None:
        """Сохраняет структуру каталога в XML-файл."""
        tree = ET.ElementTree(data.to_xml_element())
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        print(f"Данные сохранены в {filename}")

    @staticmethod
    def load(filename: str) -> DirectoryItem:
        """Загружает структуру каталога из XML-файла."""
        tree = ET.parse(filename)
        root_element = tree.getroot()
        return DirectoryItem.from_xml_element(root_element)


def run_mypy() -> None:
    """Запускает mypy для проверки аннотаций типов в текущем файле."""
    try:
        result = subprocess.run(["mypy", __file__], capture_output=True, text=True)
        if result.returncode == 0:
            print("Проверка типов с mypy завершена успешно. Ошибок не найдено.")
        else:
            print("Ошибки проверки типов с mypy:")
            print(result.stdout)
    except FileNotFoundError:
        print("mypy не установлен. Установите его с помощью 'pip install mypy'.")


def build_tree(directory: pathlib.Path, args: argparse.Namespace) -> DirectoryItem:
    """Рекурсивно строит структуру каталога."""
    contents = get_directory_contents(directory, args)
    dir_item = DirectoryItem(name=directory.name, path=str(directory), is_dir=True)

    for path in contents:
        if path.is_dir():
            child_item = build_tree(path, args)
            dir_item.children.append(child_item)
        else:
            file_item = DirectoryItem(name=path.name, path=str(path), is_dir=False)
            dir_item.children.append(file_item)

        display_path = str(path) if args.t else path.name
        print(("├── " if path != contents[-1] else "└── ") + display_path)

    return dir_item


def get_directory_contents(directory: pathlib.Path, args: argparse.Namespace) -> List[pathlib.Path]:
    """Возвращает отфильтрованное содержимое каталога в зависимости от аргументов командной строки."""
    contents = list(directory.iterdir())
    if not args.a:
        contents = [file for file in contents if not file.name.startswith(".")]
    if args.d:
        contents = [file for file in contents if file.is_dir()]
    if args.f:
        contents = [file for file in contents if file.is_file()]
    return contents


def parse_arguments(command_line: Optional[List[str]] = None) -> argparse.Namespace:
    """Разбирает аргументы командной строки и возвращает объект Namespace."""
    parser = argparse.ArgumentParser(description="Аналог команды tree в Linux.")
    parser.add_argument("directory", type=str, help="The directory to list.")
    parser.add_argument("-a", action="store_true", help="List all files, including hidden files.")
    choose = parser.add_mutually_exclusive_group()
    choose.add_argument("-d", action="store_true", help="List directories only.")
    choose.add_argument("-f", action="store_true", help="List files only.")
    parser.add_argument("-p", type=int, help="Max display depth of the directory tree.")
    parser.add_argument("-t", action="store_true", help="Print the full path prefix for each file.")
    parser.add_argument("--version", action="version", version="%(prog)s 0.0.1")
    return parser.parse_args(command_line)


def main(command_line: Optional[List[str]] = None) -> None:
    """Основная функция программы."""
    run_mypy()
    args = parse_arguments(command_line)
    directory = pathlib.Path(args.directory).resolve(strict=True)

    root_item = build_tree(directory, args)

    # Сохранение в XML после построения дерева
    xml_handler = XMLDataHandler()
    xml_handler.save(root_item, "directory_structure.xml")
    print("Структура каталога сохранена в XML файл.")


if __name__ == "__main__":
    main()
