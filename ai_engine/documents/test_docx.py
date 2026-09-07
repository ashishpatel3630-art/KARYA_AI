from pathlib import Path

from docx import Document
from documents.docx import DOCXParser


def test_docx_parser_reads_document(tmp_path: Path):
	document_path = tmp_path / "test_document.docx"
	document = Document()
	document.add_paragraph("KARYA DOCX test")
	document.save(document_path)

	text = DOCXParser().parse(document_path)

	assert "KARYA DOCX test" in text
