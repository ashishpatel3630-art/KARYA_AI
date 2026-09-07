from pathlib import Path

from openpyxl import Workbook

from documents.xlsx import XLSXParser


def test_xlsx_parser_reads_workbook(tmp_path: Path):
	workbook_path = tmp_path / "test_document.xlsx"
	workbook = Workbook()
	workbook.active["A1"] = "KARYA XLSX test"
	workbook.save(workbook_path)

	parsed = XLSXParser().parse(workbook_path)

	assert "[Sheet: Sheet]" in parsed
	assert "KARYA XLSX test" in parsed
