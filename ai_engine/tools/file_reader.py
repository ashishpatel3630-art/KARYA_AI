
from pathlib import Path

from documents.docx import DOCXParser
from documents.pdf import PDFParser
from documents.pptx import PPTXParser
from documents.xlsx import XLSXParser


class FileReaderTool:
    """Read supported local documents for KARYA agents."""

    name = "file_reader"

    description = (
        "Reads local PDF, DOCX, XLSX, and PPTX files "
        "and returns their extracted text."
    )

    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": (
                    "Path to the local PDF, DOCX, XLSX, "
                    "or PPTX file."
                ),
            }
        },
        "required": ["file_path"],
    }

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".xlsx",
        ".pptx",
    }

    def __init__(self):
        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DOCXParser(),
            ".xlsx": XLSXParser(),
            ".pptx": PPTXParser(),
        }

    def execute(self, file_path: str) -> str:
        """Read and extract text from a local document."""

        if not file_path or not file_path.strip():
            raise ValueError(
                "File path cannot be empty."
            )

        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        parser = self.parsers[extension]

        if extension == ".pdf":
            pages = parser.parse(str(path))

            if not pages:
                raise ValueError(
                    f"No readable text found in: {path.name}"
                )

            content = []

            for page in pages:
                content.append(
                    f"[Page: {page.page_number}]"
                )
                content.append(page.content)

            return "\n".join(content)

        content = parser.parse(str(path))

        if not content or not content.strip():
            raise ValueError(
                f"No readable text found in: {path.name}"
            )

        return content
