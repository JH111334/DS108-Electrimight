#!/usr/bin/env python3
"""
Pandoc Lua-style filter (via panflute) for IEEE captions.

Converts Markdown figures/tables to IEEE-style captions:
- Images: "Fig. 1.  Caption text"
- Tables: "TABLE I  Caption text"

Usage with pandoc:
    pandoc input.md --filter=tools/ieee/filters/ieee_caption_filter.py -o output.docx
"""

import panflute as pf


def _roman(num: int) -> str:
    """Convert integer to Roman numeral (I, II, III...)."""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    for v, s in zip(val, syb):
        while num >= v:
            roman_num += s
            num -= v
    return roman_num


fig_counter = 0
table_counter = 0


def action(elem, doc):
    global fig_counter, table_counter

    if isinstance(elem, pf.Image):
        fig_counter += 1
        # Prepend "Fig. N." to caption
        if elem.caption:
            new_caption = [pf.Str(f"Fig. {fig_counter}."), pf.Space()] + list(elem.caption)
            elem.caption = pf.Caption(*new_caption)
        return elem

    if isinstance(elem, pf.Table):
        table_counter += 1
        roman = _roman(table_counter)
        if elem.caption:
            new_caption = [pf.Str(f"TABLE {roman}"), pf.Space()] + list(elem.caption)
            elem.caption = pf.Caption(*new_caption)
        return elem

    return None


def finalize(doc):
    pass


def main(doc=None):
    return pf.run_filter(action, finalize=finalize, doc=doc)


if __name__ == "__main__":
    main()
