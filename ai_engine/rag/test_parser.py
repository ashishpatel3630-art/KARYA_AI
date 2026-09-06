from rag.parser import DocumentParser


parser = DocumentParser()

document = parser.parse(
    file_name="maintenance_report.pdf",
    file_type=".pdf",
    content="""
    KARYA AI - Industrial Maintenance Report

    Equipment: Pump P-101
    Temperature: 85 C
    Vibration: 7.2 mm/s
    Status: Critical
    """,
)

print("FILE NAME:")
print(document.file_name)

print("\nFILE TYPE:")
print(document.file_type)

print("\nNORMALIZED CONTENT:")
print(document.content)
