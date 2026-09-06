from documents.xlsx import XLSXParser


parser = XLSXParser()

print("Reading XLSX...\n")

text = parser.parse("test_document.xlsx")

print("EXTRACTED DATA:")
print(text)
