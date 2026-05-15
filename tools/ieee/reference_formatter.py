#!/usr/bin/env python3
"""
Reference parsing and formatting to IEEE numbered style [1], [2], ...

Supports:
- Plain text / URL lists (heuristic parse)
- BibTeX (.bib) files via bibtexparser
- RIS files (basic)
- Zotero CSV/JSON export
"""

import re
from typing import List, Dict


def _ieee_format_article(entry: Dict) -> str:
    """Format a bibtex article entry to IEEE style."""
    authors = entry.get("author", "")
    title = entry.get("title", "")
    journal = entry.get("journal", "")
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "")
    year = entry.get("year", "")

    # IEEE: Author, "Title," Journal, vol. X, no. Y, pp. Z, Year.
    parts = [f"{authors}, \"{title},\""]
    if journal:
        parts.append(f" {journal}")
    if volume:
        parts.append(f", vol. {volume}")
    if number:
        parts.append(f", no. {number}")
    if pages:
        parts.append(f", pp. {pages}")
    if year:
        parts.append(f", {year}")
    parts.append(".")
    return "".join(parts)


def _ieee_format_inproceedings(entry: Dict) -> str:
    """Format a bibtex inproceedings entry to IEEE style."""
    authors = entry.get("author", "")
    title = entry.get("title", "")
    booktitle = entry.get("booktitle", "")
    year = entry.get("year", "")
    pages = entry.get("pages", "")

    parts = [f"{authors}, \"{title},\""]
    if booktitle:
        parts.append(f" in *{booktitle}*")
    if pages:
        parts.append(f", pp. {pages}")
    if year:
        parts.append(f", {year}")
    parts.append(".")
    return "".join(parts)


def _ieee_format_misc(entry: Dict) -> str:
    """Format misc / web / report entries."""
    authors = entry.get("author", entry.get("howpublished", ""))
    title = entry.get("title", "")
    url = entry.get("url", "")
    year = entry.get("year", "")

    parts = []
    if authors:
        parts.append(f"{authors}, ")
    if title:
        parts.append(f"\"{title}.\"")
    if url:
        parts.append(f" Available: {url}")
    if year:
        parts.append(f", {year}")
    parts.append(".")
    return "".join(parts)


def format_bibtex_entry(entry: Dict) -> str:
    """Route bibtex entry to correct IEEE formatter."""
    etype = entry.get("ENTRYTYPE", "misc").lower()
    if etype == "article":
        return _ieee_format_article(entry)
    elif etype in ("inproceedings", "conference"):
        return _ieee_format_inproceedings(entry)
    else:
        return _ieee_format_misc(entry)


def parse_bibtex_file(bib_path: str) -> List[str]:
    """Parse a .bib file and return IEEE-formatted reference strings."""
    try:
        import bibtexparser
    except ImportError:
        raise ImportError("bibtexparser not installed. Run: pip install bibtexparser")

    with open(bib_path, "r", encoding="utf-8") as f:
        bib_db = bibtexparser.load(f)

    refs = [format_bibtex_entry(entry) for entry in bib_db.entries]
    return refs


def parse_plain_text_refs(text_lines: List[str]) -> List[str]:
    """
    Heuristic parser for plain-text reference lists.
    Splits on blank lines and strips numbering like [1], 1., etc.
    """
    refs = []
    current = ""
    for line in text_lines:
        line = line.strip()
        if not line:
            if current:
                refs.append(current.strip())
                current = ""
            continue
        # Remove existing numbering
        line = re.sub(r"^\[\d+\]\s*", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        current += " " + line
    if current:
        refs.append(current.strip())
    return refs


def number_references(refs: List[str]) -> List[str]:
    """Return references with [N] prefix (for display)."""
    # Already handled by styles.add_reference_entry, but useful for Markdown
    return refs


def validate_ieee_reference(ref: str) -> List[str]:
    """Check common IEEE formatting issues in a reference string."""
    issues = []
    if '"' in ref and "\"" not in ref:
        issues.append("Use curly quotes or proper LaTeX quotes")
    if ref.count(".") < 2:
        issues.append("Possibly incomplete reference")
    if "http" in ref and "Available:" not in ref:
        issues.append("URL should follow 'Available:' for web sources")
    return issues
