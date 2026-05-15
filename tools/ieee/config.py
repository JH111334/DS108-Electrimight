#!/usr/bin/env python3
"""
IEEE Conference Paper Configuration Constants.
All values follow IEEE conference proceedings standard (US Letter, 2-column optional).
"""

from docx.shared import Inches, Pt, Cm

# ---------------------------------------------------------------------------
# Page Setup
# ---------------------------------------------------------------------------
PAGE_WIDTH = Inches(8.5)      # US Letter
PAGE_HEIGHT = Inches(11.0)
LEFT_MARGIN = Inches(1.0)
RIGHT_MARGIN = Inches(1.0)
TOP_MARGIN = Inches(1.0)
BOTTOM_MARGIN = Inches(1.0)

# ---------------------------------------------------------------------------
# Font
# ---------------------------------------------------------------------------
FONT_NAME = "Times New Roman"

# ---------------------------------------------------------------------------
# Font Sizes (pt)
# ---------------------------------------------------------------------------
SIZE_TITLE = Pt(14)
SIZE_AUTHOR = Pt(12)
SIZE_SECTION = Pt(10)         # Heading 1 (ALL CAPS, bold)
SIZE_SUBSECTION = Pt(10)      # Heading 2 (bold italic)
SIZE_BODY = Pt(10)
SIZE_ABSTRACT = Pt(9)
SIZE_KEYWORDS = Pt(9)
SIZE_REFERENCE = Pt(9)
SIZE_CAPTION = Pt(8)

# ---------------------------------------------------------------------------
# Paragraph Spacing (pt)
# ---------------------------------------------------------------------------
SPACE_AFTER_TITLE = 6
SPACE_AFTER_AUTHOR = 12
SPACE_BEFORE_SECTION = 12
SPACE_AFTER_SECTION = 6
SPACE_BEFORE_SUBSECTION = 6
SPACE_AFTER_SUBSECTION = 3
SPACE_AFTER_ABSTRACT = 6
SPACE_AFTER_KEYWORDS = 12
SPACE_AFTER_BODY = 0

# ---------------------------------------------------------------------------
# Line Spacing
# ---------------------------------------------------------------------------
LINE_SPACING_SINGLE = 1.0

# ---------------------------------------------------------------------------
# Indentation
# ---------------------------------------------------------------------------
BODY_FIRST_LINE_INDENT = Cm(1.27)   # ~0.5 inch paragraph indent
REF_HANGING_INDENT = Cm(0.63)       # hanging indent for references

# ---------------------------------------------------------------------------
# Section Numbering
# ---------------------------------------------------------------------------
SECTION_NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
SUBSECTION_PREFIXES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

# ---------------------------------------------------------------------------
# Pandoc Paths
# ---------------------------------------------------------------------------
PANDOC_REF_DOC = r"tools\ieee\templates\ieee_reference.docx"
PANDOC_FILTER_DIR = r"tools\ieee\filters"
