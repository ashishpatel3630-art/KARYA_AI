from documents.pdf import PDFParser


parser = PDFParser()

pdf_path = "test_document.pdf"

print("Reading PDF...\n")

text = parser.parse(pdf_path)

print("EXTRACTED TEXT:")
print(text)
