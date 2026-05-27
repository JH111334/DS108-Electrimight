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

## Windows UTF-8 Workflow (Vietnamese Text)

> See global skill: `windows-utf8-workflow`

When editing Vietnamese text on Windows PowerShell:

1. **Never print Vietnamese to Shell stdout.** Redirect to file instead:
   ```powershell
   python script.py > output.txt
   ```
2. **Prefer `WriteFile` / `StrReplaceFile` / `ReadFile`** over `Shell` for Vietnamese content.
3. **For bulk replacement**, write a temporary `.py` script to disk, execute it, then delete it.
4. **Set UTF-8 explicitly** at session start if using Shell heavily:
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   $env:PYTHONIOENCODING = "utf-8"
   ```
5. **Always specify `encoding="utf-8"`** in Python file I/O.
6. **Verify with `ReadFile`**, not `Get-Content` or `type` in Shell.
7. **Clean up temp files** (`_temp_*`, `_*.py`) before ending the session.
