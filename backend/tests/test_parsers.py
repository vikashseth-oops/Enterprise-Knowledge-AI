from app.ingestion.parsers import DocumentParser


def test_parse_markdown():
    md_content = b"# Security Policy\nThis is the intro.\n## Passwords\nMinimum 14 characters."
    sections = DocumentParser.parse(md_content, "policy.md")
    assert len(sections) >= 1
    assert any("Passwords" in s.section_title or "14 characters" in s.text for s in sections)


def test_parse_html():
    html_content = b"<html><body><h1>API Architecture</h1><p>RESTful OpenAPI 3.1</p></body></html>"
    sections = DocumentParser.parse(html_content, "arch.html")
    assert len(sections) >= 1
    assert "OpenAPI" in sections[0].text


def test_parse_csv():
    csv_content = b"PolicyID,Name,Owner\nSEC-101,Passwords,IT\nHR-042,Remote,HR\n"
    sections = DocumentParser.parse(csv_content, "data.csv")
    assert len(sections) >= 1
    assert "SEC-101" in sections[0].text


def test_parse_plain_text():
    txt_content = b"Simple document line 1\nSimple document line 2"
    sections = DocumentParser.parse(txt_content, "notes.txt")
    assert len(sections) == 1
    assert "Simple document" in sections[0].text
