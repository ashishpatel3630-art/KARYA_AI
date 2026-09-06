from documents.docx import DOCXParser


parser = DOCXParser()

print("Reading DOCX...\n")

text = parser.parse("test_document.docx")

print("EXTRACTED TEXT:")
print(text)
