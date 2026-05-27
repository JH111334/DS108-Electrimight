# Agent Guideline — Encoding, Documentation & LaTeX

> Copy-paste this entire block into the `AGENTS.md` of any project that produces documentation or LaTeX reports in Vietnamese (or any non-ASCII language).

---

## 1. Encoding Convention (Mandatory)

- **All text files** (`.md`, `.py`, `.txt`, `.csv`, `.tex`, `.bib`, `.json`, `.yml`) **must be UTF-8 encoded**.
- **Do not use** `cp1252`, `latin-1`, `iso-8859-1`, or any legacy Windows single-byte encoding.
- When editing on Windows, ensure your editor saves as **UTF-8 without BOM**.
- When reading/writing files in Python, **always** specify `encoding="utf-8"` explicitly:
  ```python
  with open("file.md", "w", encoding="utf-8") as f:
      f.write(content)
  ```
- If a file already contains mojibake (e.g. `Gi��i thi���u`), rewrite it entirely with correct diacritics in UTF-8 rather than attempting in-place repair.

## 2. Windows UTF-8 Workflow (PowerShell)

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

## 3. LaTeX Document Standards

### 3.1 Vietnamese Language Support

For IEEE/ACM papers with Vietnamese text, always add to the preamble:

```latex
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc}
\usepackage[vietnamese]{babel}
```

If using **XeLaTeX** or **LuaLaTeX** (recommended for modern workflows), use `fontspec` instead:

```latex
\usepackage{fontspec}
\usepackage[vietnamese]{babel}
% No inputenc/fontenc needed with XeLaTeX
```

### 3.2 IEEE Format Checklist

| Item | Rule |
|------|------|
| Font | Times New Roman 10 pt (or Computer Modern with `newtxtext`) |
| Margins | 1 inch (2.54 cm) all sides |
| Columns | 2 columns for conference format |
| Spacing | Single spacing |
| Section numbering | Roman numerals: I, II, III... then A, B, C... |
| Headings | Level 1: ALL CAPS, bold, 10 pt; Level 2: Title Case, bold, 10 pt |
| Abstract | 150--250 words |
| Keywords | 3--5 keywords, separated by commas |
| Equations | Numbered in parentheses on the right: `(1)`, `(2)` |
| Figures | `Fig. 1.` caption below, 8 pt, bold |
| Tables | `TABLE I` caption above, ALL CAPS, 8 pt, bold |
| References | IEEE numbered `[1]`, `[2]`, hanging indent 0.25" |
| Citation | In-text: `[1]`, `[2]`, `[3]--[5]` |

### 3.3 Common LaTeX Pitfalls

1. **Wrong encoding**: File saved as cp1252 -> compile error or mojibake. Always verify with `ReadFile`.
2. **Missing `\text{}` in math mode**: Write `\text{Usage\_kWh}`, not `Usage_kWh`.
3. **Bare ampersands in tables**: Escape as `\&` in text, use column separators correctly in `tabular`.
4. **Unescaped underscores**: In text mode, `_` must be `\_`; in math mode it is fine.
5. **Babel caption override**: `\usepackage[vietnamese]{babel}` may change `\figurename` to `Hình`. Override if needed:
   ```latex
   \addto\captionsvietnamese{%
     \def\figurename{Fig.}%
     \def\tablename{TABLE}%
   }
   ```
6. **Equation punctuation**: End equations with a comma or period if they end a sentence.
7. **Non-breaking spaces**: Use `~` before citations: `Section~\ref{sec:methodology}`.

### 3.4 Report Length Limits

- **IEEE Conference**: Typically 4--6 pages (single column equivalent) or as specified by venue.
- **University Thesis/Report**: Follow local regulation (e.g., 20 trang đôi / 40 trang đơn).
- Always check the specific call-for-papers or department guideline.

## 4. Documentation Standards

### 4.1 Markdown Files

- Use UTF-8 without BOM.
- Use ATX-style headers (`#`, `##`, `###`).
- Use fenced code blocks with language tags.
- Use `---` for horizontal rules, not `***`.
- Keep line length <= 100 characters for readability.

### 4.2 Docstrings & Comments

```python
def compute_apparent_power(p: float, q: float) -> float:
    """Compute apparent power S = sqrt(P^2 + Q^2).

    Args:
        p: Active power in kW.
        q: Reactive power in kVar.

    Returns:
        Apparent power in kVA.
    """
    return math.sqrt(p ** 2 + q ** 2)
```

### 4.3 Notebook Extracts

- If extracting `.ipynb` to `.txt` for agent context, prefix output files with `notebooks_` and suffix with `_extracted.txt`.
- Store extracted notebook text in `artifacts/` (gitignored) to keep root clean.

## 5. Project Hygiene

- **Gitignore artifacts**: Add `artifacts/` and `*_extracted.txt` to `.gitignore`.
- **No temp files in repo**: Delete `_temp_*`, `_*.py`, `~$*.docx` before committing.
- **Reference materials**: Consolidate reference docs into `references/`:
  - `references/documents/` -- outlines, guides, templates (`.docx`, `.pdf`)
  - `references/report-guides/` -- markdown guides for each report section
- **LaTeX compilation artifacts**: Ignore `.aux`, `.log`, `.out`, `.toc`, `.synctex.gz`, `_minted-*`.

## 6. Quick Reference -- Session Startup

For any new Windows session involving Vietnamese text:

```powershell
# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

For XeLaTeX compilation:

```bash
xelatex -shell-escape -interaction=nonstopmode report.tex
```

For pdflatex with Vietnamese:

```bash
pdflatex -interaction=nonstopmode report.tex
```
