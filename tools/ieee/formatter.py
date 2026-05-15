#!/usr/bin/env python3
"""
High-level IEEE paper formatter.
Orchestrates styles.py helpers to build a complete IEEE document from structured data.
"""

from docx import Document
from docx.shared import Inches

from tools.ieee.config import (
    PAGE_WIDTH,
    PAGE_HEIGHT,
    LEFT_MARGIN,
    RIGHT_MARGIN,
    TOP_MARGIN,
    BOTTOM_MARGIN,
    SECTION_NUMERALS,
    SUBSECTION_PREFIXES,
)
from tools.ieee import styles


def setup_ieee_document():
    """Create a new Document with IEEE page setup."""
    doc = Document()
    section = doc.sections[0]
    section.page_width = PAGE_WIDTH
    section.page_height = PAGE_HEIGHT
    section.left_margin = LEFT_MARGIN
    section.right_margin = RIGHT_MARGIN
    section.top_margin = TOP_MARGIN
    section.bottom_margin = BOTTOM_MARGIN
    return doc


def build_ieee_paper(
    output_path,
    title,
    authors,
    abstract,
    keywords,
    sections,       # list of dicts: {"title": "", "subsections": [{"title": "", "paragraphs": [""]}]}
    references,     # list of strings
    tables=None,    # optional list of {"caption": "", "rows": [[...]]}
    figures=None,   # optional list of {"caption": "", "path": ""}
):
    """
    Build a complete IEEE paper and save to output_path.

    Args:
        output_path: Path to save .docx
        title: Paper title string
        authors: Multi-line author string
        abstract: Abstract text (150-250 words)
        keywords: Comma-separated keywords
        sections: Hierarchical content
        references: List of reference strings
        tables: Optional table data
        figures: Optional figure image paths
    """
    doc = setup_ieee_document()

    # Title & Authors
    styles.add_title(doc, title)
    styles.add_author_block(doc, authors)

    # Abstract & Keywords
    styles.add_abstract(doc, abstract)
    styles.add_keywords(doc, keywords)

    # Body Sections
    for idx, sec in enumerate(sections):
        roman = SECTION_NUMERALS[idx] if idx < len(SECTION_NUMERALS) else str(idx + 1)
        styles.add_section_heading(doc, roman, sec["title"])

        for sidx, sub in enumerate(sec.get("subsections", [])):
            letter = SUBSECTION_PREFIXES[sidx] if sidx < len(SUBSECTION_PREFIXES) else str(sidx + 1)
            styles.add_subsection_heading(doc, letter, sub["title"])
            for para in sub.get("paragraphs", []):
                styles.add_body_paragraph(doc, para)

        # Paragraphs directly under section (no subsection)
        for para in sec.get("paragraphs", []):
            styles.add_body_paragraph(doc, para)

    # References
    if references:
        styles.add_section_heading(doc, "", "REFERENCES")
        for num, ref in enumerate(references, 1):
            styles.add_reference_entry(doc, num, ref)

    doc.save(output_path)
    print(f"[IEEE] Paper saved to: {output_path}")
    print(f"[IEEE] Sections: {len(sections)} | References: {len(references)}")
