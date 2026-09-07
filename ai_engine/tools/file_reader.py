from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from documents.docx import DOCXParser
from documents.pdf import PDFParser
from documents.pptx import PPTXParser
from documents.xlsx import XLSXParser
from tools.schemas import ToolDefinition, ToolResult


@dataclass
class FileReaderTool:
    """
    KARYA file-reading tool.

    Supports:
    - PDF
    - DOCX
    - XLSX
    - PPTX
    - TXT
    - MD
    """

    name: str = "file_reader"

    description: str = (
        "Read and extract text or structured content from "
        "local PDF, DOCX, XLSX, PPTX, TXT, and Markdown files."
    )

    def __post_init__(self) -> None:
        self._pdf_parser = PDFParser()
        self._docx_parser = DOCXParser()
        self._pptx_parser = PPTXParser()
        self._xlsx_parser = XLSXParser()

    def definition(self) -> ToolDefinition:
        """Return the tool definition."""

        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "Absolute or relative path to the "
                            "local file."
                        ),
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False,
            },
        )

    def execute(
        self,
        file_path: str,
    ) -> ToolResult:
        """Read a local file and return extracted content."""

        if not isinstance(file_path, str):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="file_path must be a string.",
            )

        file_path = file_path.strip()

        if not file_path:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="file_path cannot be empty.",
            )

        path = Path(file_path)

        if not path.exists():
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"File not found: {path}",
            )

        if not path.is_file():
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Path is not a file: {path}",
            )

        try:
            suffix = path.suffix.lower()

            if suffix == ".pdf":
                output = self._read_pdf(path)

            elif suffix == ".docx":
                output = self._read_docx(path)

            elif suffix == ".pptx":
                output = self._read_pptx(path)

            elif suffix == ".xlsx":
                output = self._read_xlsx(path)

            elif suffix in {".txt", ".md"}:
                output = path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )

            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    output=None,
                    error=(
                        f"Unsupported file type: {suffix}. "
                        "Supported types: PDF, DOCX, XLSX, PPTX, "
                        "TXT, MD."
                    ),
                )

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=output,
                error=None,
            )

        except Exception as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Failed to read file: {exc}",
            )

    def execute_with_input(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute using ToolRegistry-style arguments."""

        if not isinstance(arguments, dict):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Tool arguments must be a dictionary.",
            )

        file_path = arguments.get("file_path")

        if file_path is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Missing required argument: file_path.",
            )

        return self.execute(file_path)

    def _read_pdf(
        self,
        path: Path,
    ) -> str:
        pages = self._pdf_parser.parse(path)

        sections: list[str] = []

        for page in pages:
            sections.append(
                f"[Page {page.page_number}]\n"
                f"{page.text}"
            )

        return "\n\n".join(sections)

    def _read_docx(
        self,
        path: Path,
    ) -> str:
        document = self._docx_parser.parse(path)

        sections: list[str] = []

        if hasattr(document, "paragraphs"):
            for paragraph in document.paragraphs:
                text = getattr(paragraph, "text", "")

                if text:
                    sections.append(text)

        if hasattr(document, "tables"):
            for table_index, table in enumerate(
                document.tables,
                start=1,
            ):
                sections.append(
                    f"[Table {table_index}]"
                )

                for row in table:
                    values = []

                    for cell in row:
                        values.append(
                            getattr(cell, "text", str(cell))
                        )

                    sections.append(
                        " | ".join(values)
                    )

        return "\n".join(sections)

    def _read_pptx(
        self,
        path: Path,
    ) -> str:
        slides = self._pptx_parser.parse(path)

        sections: list[str] = []

        for slide in slides:
            sections.append(
                f"[Slide {slide.slide_number}]\n"
                f"{slide.text}"
            )

        return "\n\n".join(sections)

    def _read_xlsx(
        self,
        path: Path,
    ) -> str:
        workbook = self._xlsx_parser.parse(path)

        sections: list[str] = []

        for sheet in workbook.sheets:
            sections.append(
                f"[Sheet: {sheet.sheet_name}]"
            )

            for row in sheet.rows:
                sections.append(
                    " | ".join(
                        str(value)
                        for value in row
                    )
                )

        return "\n".join(sections)