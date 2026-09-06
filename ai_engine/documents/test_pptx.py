from documents.pptx import PPTXParser


parser = PPTXParser()

print("Reading PPTX...\n")

text = parser.parse("test_document.pptx")

print("EXTRACTED TEXT:")
print(text)
