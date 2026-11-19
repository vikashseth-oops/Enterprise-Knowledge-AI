import csv
import io
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.errors import DocumentParsingError
from app.core.logging import logger


class ParsedSection:
    def __init__(self, text: str, page_number: int = 1, section_title: str = ""):
        self.text = text
        self.page_number = page_number
        self.section_title = section_title


class DocumentParser:
    """Universal parser for enterprise formats (PDF, DOCX, TXT, MD, HTML, CSV)."""

    @classmethod
    def parse_pdf(cls, content: bytes, filename: str) -> list[ParsedSection]:
        try:
            reader = PdfReader(io.BytesIO(content))
            sections = []
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                page_text = page_text.strip()
                if page_text:
                    sections.append(
                        ParsedSection(
                            text=page_text,
                            page_number=page_idx + 1,
                            section_title=f"Page {page_idx + 1}",
                        )
                    )
            return sections
        except Exception as e:
            logger.error("pdf_parse_error", filename=filename, error=str(e))
            raise DocumentParsingError(filename, f"PDF extraction failed: {e!s}")

    @classmethod
    def parse_docx(cls, content: bytes, filename: str) -> list[ParsedSection]:
        try:
            doc = DocxDocument(io.BytesIO(content))
            sections = []
            current_section = "Introduction"
            buffer = []

            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue
                # Heading detection
                if p.style.name.startswith("Heading"):
                    if buffer:
                        sections.append(
                            ParsedSection(
                                text="\n".join(buffer),
                                page_number=1,
                                section_title=current_section,
                            )
                        )
                        buffer = []
                    current_section = text
                else:
                    buffer.append(text)

            # Also parse tables if present
            for table in doc.tables:
                table_lines = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_lines.append(" | ".join(row_data))
                if table_lines:
                    buffer.append("\n[Table]\n" + "\n".join(table_lines))

            if buffer:
                sections.append(
                    ParsedSection(
                        text="\n".join(buffer),
                        page_number=1,
                        section_title=current_section,
                    )
                )
            return sections
        except Exception as e:
            logger.error("docx_parse_error", filename=filename, error=str(e))
            raise DocumentParsingError(filename, f"DOCX extraction failed: {e!s}")

    @classmethod
    def parse_html(cls, content: bytes, filename: str) -> list[ParsedSection]:
        try:
            soup = BeautifulSoup(content, "html.parser")
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()

            sections = []
            headers = soup.find_all(["h1", "h2", "h3"])
            if not headers:
                text = soup.get_text(separator="\n").strip()
                return [ParsedSection(text=text, page_number=1, section_title="Main Content")]

            for h in headers:
                title = h.get_text().strip()
                content_nodes = []
                sibling = h.find_next_sibling()
                while sibling and sibling.name not in ["h1", "h2", "h3"]:
                    text = sibling.get_text(strip=True)
                    if text:
                        content_nodes.append(text)
                    sibling = sibling.find_next_sibling()

                if content_nodes:
                    sections.append(
                        ParsedSection(
                            text="\n".join(content_nodes),
                            page_number=1,
                            section_title=title,
                        )
                    )
            return sections or [
                ParsedSection(
                    text=soup.get_text(separator="\n").strip(),
                    page_number=1,
                    section_title="Content",
                )
            ]
        except Exception as e:
            logger.error("html_parse_error", filename=filename, error=str(e))
            raise DocumentParsingError(filename, f"HTML extraction failed: {e!s}")

    @classmethod
    def parse_csv(cls, content: bytes, filename: str) -> list[ParsedSection]:
        try:
            decoded = content.decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(decoded))
            rows = list(reader)
            if not rows:
                return []

            header = rows[0]
            sections = []
            chunk_rows = []
            for row_idx, row in enumerate(rows[1:], start=1):
                row_str = ", ".join(f"{h}: {val}" for h, val in zip(header, row))
                chunk_rows.append(row_str)
                if len(chunk_rows) >= 20:  # group 20 rows per chunk
                    sections.append(
                        ParsedSection(
                            text="\n".join(chunk_rows),
                            page_number=(row_idx // 20) + 1,
                            section_title=f"Rows {row_idx - 19} to {row_idx}",
                        )
                    )
                    chunk_rows = []

            if chunk_rows:
                sections.append(
                    ParsedSection(
                        text="\n".join(chunk_rows),
                        page_number=len(sections) + 1,
                        section_title="Final Rows",
                    )
                )
            return sections
        except Exception as e:
            logger.error("csv_parse_error", filename=filename, error=str(e))
            raise DocumentParsingError(filename, f"CSV extraction failed: {e!s}")

    @classmethod
    def parse_text(cls, content: bytes, filename: str) -> list[ParsedSection]:
        try:
            text = content.decode("utf-8", errors="replace").strip()
            # Split markdown by top headings if markdown
            if filename.lower().endswith(".md"):
                lines = text.splitlines()
                sections = []
                cur_title = "Header"
                cur_lines = []
                for line in lines:
                    if line.startswith("# ") or line.startswith("## "):
                        if cur_lines:
                            sections.append(
                                ParsedSection(
                                    text="\n".join(cur_lines).strip(),
                                    page_number=1,
                                    section_title=cur_title,
                                )
                            )
                            cur_lines = []
                        cur_title = line.lstrip("#").strip()
                    cur_lines.append(line)
                if cur_lines:
                    sections.append(
                        ParsedSection(
                            text="\n".join(cur_lines).strip(),
                            page_number=1,
                            section_title=cur_title,
                        )
                    )
                return sections or [ParsedSection(text=text, page_number=1, section_title="Document")]

            return [ParsedSection(text=text, page_number=1, section_title="Document")]
        except Exception as e:
            logger.error("text_parse_error", filename=filename, error=str(e))
            raise DocumentParsingError(filename, f"Text decoding failed: {e!s}")

    @classmethod
    def parse(cls, content: bytes, filename: str) -> list[ParsedSection]:
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            return cls.parse_pdf(content, filename)
        elif ext in [".docx", ".doc"]:
            return cls.parse_docx(content, filename)
        elif ext in [".html", ".htm"]:
            return cls.parse_html(content, filename)
        elif ext == ".csv":
            return cls.parse_csv(content, filename)
        elif ext in [".txt", ".md", ".json", ".log"]:
            return cls.parse_text(content, filename)
        else:
            # Fallback to UTF-8 text parser
            return cls.parse_text(content, filename)
