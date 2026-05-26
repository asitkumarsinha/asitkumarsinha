import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from hello_world.main import get_message, read_four_excel_files


class GetMessageTest(unittest.TestCase):
    def test_get_message_returns_hello_world(self) -> None:
        self.assertEqual(get_message(), "Hello, world!")


class ReadFourExcelFilesTest(unittest.TestCase):
    def test_reads_four_excel_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = []
            for index in range(4):
                path = Path(temp_dir) / f"workbook_{index + 1}.xlsx"
                workbook = Workbook()
                worksheet = workbook.active
                worksheet.append(["name", "count"])
                worksheet.append([f"file-{index + 1}", index + 1])
                worksheet.append([None, None])
                workbook.save(path)
                paths.append(path)

            result = read_four_excel_files(paths)

        self.assertEqual(len(result), 4)
        for index, path in enumerate(paths):
            self.assertEqual(result[str(path)], [{"name": f"file-{index + 1}", "count": index + 1}])

    def test_requires_exactly_four_files(self) -> None:
        with self.assertRaisesRegex(ValueError, "Exactly four Excel file paths"):
            read_four_excel_files(["one.xlsx", "two.xlsx", "three.xlsx"])


if __name__ == "__main__":
    unittest.main()
