# IEEE Conference Paper Formatting

## Scope

This skill governs the creation, conversion, and validation of IEEE conference paper format `.docx` files within this project. All text files must be UTF-8 encoded.

## Standards

IEEE conference proceedings format (US Letter, single or double column):
- **Font**: Times New Roman everywhere
- **Page**: 8.5" × 11" (US Letter)
- **Margins**: 1 inch all sides
- **Title**: 14pt bold, centered
- **Author**: 12pt, centered
- **Abstract**: 9pt, "Abstract—" bold label, justified
- **Keywords**: 9pt, "Index Terms—" bold label, justified
- **Section headings**: 10pt bold, ALL CAPS, centered, Roman numerals (I, II, III...)
- **Subsection headings**: 10pt bold italic, left-aligned, letter prefix (A, B, C...)
- **Body text**: 10pt, justified, single spacing, first-line indent 0.5"
- **References**: 9pt, numbered [1], [2]..., hanging indent 0.25"
- **Table caption**: "TABLE I" bold ALL CAPS, 8pt, above table
- **Figure caption**: "Fig. 1." bold, 8pt, below figure

## Tools

| Tool | Path | Purpose |
|------|------|---------|
| Reference template | `tools/ieee/templates/ieee_reference.docx` | Pandoc `--reference-doc` |
| Caption filter | `tools/ieee/filters/ieee_caption_filter.py` | Pandoc filter for Fig/Table captions |
| Formatter module | `tools/ieee/formatter.py` | Programmatic docx generation |
| Styles module | `tools/ieee/styles.py` | Low-level paragraph/run styling |
| Reference formatter | `tools/ieee/reference_formatter.py` | BibTeX → IEEE refs |
| Validator | `tools/ieee/validator.py` | Automated compliance checking |
| Config | `tools/ieee/config.py` | All constants (fonts, sizes, margins) |

## Workflows

### Markdown → IEEE Docx (Preferred)

```bash
pandoc paper.md \
  --reference-doc=tools/ieee/templates/ieee_reference.docx \
  --filter=tools/ieee/filters/ieee_caption_filter.py \
  -o paper_ieee.docx
```

Then validate:
```bash
python tools/ieee/validator.py paper_ieee.docx
```

### Python API

```python
from tools.ieee.formatter import build_ieee_paper
from tools.ieee.reference_formatter import parse_bibtex_file

refs = parse_bibtex_file("references.bib")

build_ieee_paper(
    output_path="paper_ieee.docx",
    title="Paper Title",
    authors="Author¹\nAffiliation",
    abstract="150-250 words...",
    keywords="keyword1, keyword2",
    sections=[
        {"title": "INTRODUCTION", "paragraphs": ["..."]},
        {"title": "PROPOSED FRAMEWORK",
         "subsections": [
             {"title": "Time-Domain Features", "paragraphs": ["..."]},
         ]},
    ],
    references=refs,
)
```

## Encoding

All `.md`, `.py`, `.bib`, and `.docx` metadata must be **UTF-8**. Never use `cp1252` or `latin-1`.

## Common Pitfalls

1. **Font not applied**: Always set `w:ascii`, `w:hAnsi`, `w:cs`, `w:eastAsia` in XML.
2. **Line spacing defaults to 1.15**: Explicitly set `line_spacing = 1.0`.
3. **Two-column layout**: `python-docx` does not support native 2-column; use Pandoc with a pre-formatted reference doc.
4. **References without [N]**: IEEE requires bracketed numbers; plain text URLs are invalid.
5. **Heading not ALL CAPS**: Section headings must be fully capitalized.
