from pathlib import Path

from reportlab.pdfgen import canvas

from documents.pdf import PDFParser


def test_pdf_parser_reads_pages(tmp_path: Path):
	pdf_path = tmp_path / "test_document.pdf"
	document = canvas.Canvas(str(pdf_path))
	document.drawString(72, 720, "KARYA PDF test")
	document.save()

	pages = PDFParser().parse(pdf_path)

	assert len(pages) == 1
	assert pages[0].page_number == 1
	assert "KARYA PDF test" in pages[0].text
