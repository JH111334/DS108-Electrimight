# Agent Instructions — DS108-Electrimight

## Encoding Convention

- **All text files** (`.md`, `.py`, `.txt`, `.csv` metadata, notebooks extracted text) **must be UTF-8 encoded**.
- **Do not use** `cp1252`, `latin-1`, `iso-8859-1`, or any legacy Windows single-byte encoding.
- When editing on Windows, ensure your editor saves as **UTF-8 without BOM**.
- When reading/writing files in Python, always specify `encoding="utf-8"` explicitly:
  ```python
  with open("file.md", "w", encoding="utf-8") as f:
      f.write(content)
  ```
- If a file already contains mojibake (e.g. `Gi��i thi���u`), rewrite it entirely with correct Vietnamese diacritics in UTF-8 rather than attempting in-place repair.

## Project Context

- **Language**: Documentation and reports are written in Vietnamese with full diacritics.
- **Python version**: 3.12
- **Platform**: Windows (PowerShell)
- **Data**: UTF-8 CSV files with `dayfirst=True` date parsing (`DD/MM/YYYY` format).
