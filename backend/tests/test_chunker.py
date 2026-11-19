from app.ingestion.chunker import RecursiveChunker
from app.ingestion.parsers import ParsedSection


def test_chunking_and_metadata():
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
    sections = [
        ParsedSection(
            text="First long paragraph discussing the enterprise remote work policy in detail. " * 5,
            page_number=1,
            section_title="Eligibility",
        ),
    ]

    chunks = chunker.chunk_sections("doc123", "remote_policy.md", sections)
    assert len(chunks) > 1
    for c in chunks:
        assert c.doc_id == "doc123"
        assert c.doc_name == "remote_policy.md"
        assert c.page_number == 1
        assert c.section == "Eligibility"
        assert len(c.text) > 0
