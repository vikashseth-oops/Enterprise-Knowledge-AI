from app.config import settings
from app.ingestion.parsers import ParsedSection
from app.schemas.documents import DocumentChunk


class RecursiveChunker:
    """
    Recursively chunks text using paragraph, sentence, and word boundaries
    while maintaining overlap and preserving contextual metadata.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        separators: list[str] | None = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.separators = separators or [
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ]

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively splits text until parts are within chunk_size."""
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1 :]
                break

        splits = text.split(separator) if separator != "" else list(text)

        good_splits = []
        for s in splits:
            if not s:
                continue
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if new_separators:
                    sub_splits = self._split_text(s, new_separators)
                    good_splits.extend(sub_splits)
                else:
                    good_splits.append(s)

        # Merge splits respecting chunk_size and chunk_overlap
        current_chunk = []
        current_len = 0

        for s in good_splits:
            add_len = len(s) + (len(separator) if current_chunk else 0)
            if current_len + add_len > self.chunk_size and current_chunk:
                merged = separator.join(current_chunk)
                final_chunks.append(merged)
                # Keep overlap from previous chunk
                overlap_chars = 0
                overlap_chunk = []
                for item in reversed(current_chunk):
                    if overlap_chars + len(item) <= self.chunk_overlap:
                        overlap_chunk.insert(0, item)
                        overlap_chars += len(item)
                    else:
                        break
                current_chunk = overlap_chunk
                current_len = sum(len(x) for x in current_chunk) + max(0, len(current_chunk) - 1) * len(separator)

            current_chunk.append(s)
            current_len += len(s) + (len(separator) if len(current_chunk) > 1 else 0)

        if current_chunk:
            final_chunks.append(separator.join(current_chunk))

        return final_chunks

    def chunk_sections(
        self,
        doc_id: str,
        doc_name: str,
        sections: list[ParsedSection],
    ) -> list[DocumentChunk]:
        """Processes parsed document sections into structured DocumentChunk objects."""
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for section in sections:
            raw_text = section.text.strip()
            if not raw_text:
                continue

            split_texts = self._split_text(raw_text, self.separators)
            for text_piece in split_texts:
                clean_text = text_piece.strip()
                if len(clean_text) < 20:  # Skip trivial fragments
                    continue

                # Approximate tokens by word count * 1.3
                approx_tokens = int(len(clean_text.split()) * 1.3)

                chunk = DocumentChunk(
                    chunk_id=f"{doc_id}#chunk_{chunk_index}",
                    doc_id=doc_id,
                    doc_name=doc_name,
                    chunk_index=chunk_index,
                    text=clean_text,
                    page_number=section.page_number,
                    section=section.section_title or None,
                    token_count=approx_tokens,
                    metadata={
                        "source": doc_name,
                        "doc_id": doc_id,
                        "page": section.page_number,
                        "section": section.section_title,
                    },
                )
                chunks.append(chunk)
                chunk_index += 1

        return chunks
