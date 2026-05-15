# IEEE Conference Paper Workflow

## Overview

This workflow converts structured content (Markdown or existing .docx) into a properly formatted IEEE conference paper (.docx).

## Prerequisites

```bash
# Installed automatically by setup
pip install python-docx pypandoc bibtexparser panflute
```

Pandoc binary (v3.x) must be available in PATH.

## Approach A: Markdown → IEEE Docx (Recommended)

### Step 1: Write content in Markdown

```markdown
---
title: "Advanced Data Preprocessing for Industrial Anomaly Detection"
author:
  - "Author One¹"
  - "Author Two²"
affiliation:
  - "¹Dept. of Data Science, University"
  - "²Dept. of EE, University"
abstract: |
  This paper presents... (150-250 words)
keywords: "Data preprocessing, anomaly detection, time series"
---

# I. INTRODUCTION

Body text with proper paragraph structure.

## A. Subsection Title

More body text.

# II. RELATED WORK

# III. PROPOSED FRAMEWORK

# REFERENCES

[1] Author, "Title," Journal, vol. x, pp. y, Year.
```

### Step 2: Convert via Pandoc

```bash
pandoc paper.md \
  --reference-doc=tools/ieee/templates/ieee_reference.docx \
  --filter=tools/ieee/filters/ieee_caption_filter.py \
  -o paper_ieee.docx
```

### Step 3: Validate

```bash
python tools/ieee/validator.py paper_ieee.docx
```

## Approach B: Existing Docx → IEEE Docx

```python
from tools.ieee.formatter import build_ieee_paper

build_ieee_paper(
    output_path="paper_ieee.docx",
    title="Your Title",
    authors="Author Name\nAffiliation",
    abstract="...",
    keywords="keyword1, keyword2",
    sections=[
        {"title": "INTRODUCTION", "paragraphs": ["..."]},
        {"title": "RELATED WORK", "paragraphs": ["..."]},
    ],
    references=["Author, \"Title,\" Journal, vol. x, pp. y, Year."],
)
```

## Approach C: BibTeX References

```python
from tools.ieee.reference_formatter import parse_bibtex_file

refs = parse_bibtex_file("references.bib")
# refs is now a list of IEEE-formatted strings
```

## Validation Checklist

- [ ] US Letter (8.5" × 11")
- [ ] Margins 1 inch all sides
- [ ] Times New Roman everywhere
- [ ] Title 14pt bold centered
- [ ] Author 12pt centered
- [ ] Abstract 9pt justified
- [ ] Keywords 9pt "Index Terms—"
- [ ] Section headings 10pt bold ALL CAPS centered
- [ ] Subsection 10pt bold italic left
- [ ] Body 10pt justified, first-line indent
- [ ] References 9pt hanging indent [N] format
- [ ] Table captions: "TABLE I" above table
- [ ] Figure captions: "Fig. 1." below figure
