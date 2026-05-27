#!/usr/bin/env python3
"""
UTF-8 safe string replacement helper for Windows.
Use when StrReplaceFile fails on Vietnamese or special Unicode text.

Usage:
    python tools/utf8_replace.py file.tex "old" "new"
    python tools/utf8_replace.py file.tex --json replacements.json
"""
import argparse
import json
import sys


def replace_inline(filepath: str, old: str, new: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Replaced in {filepath}")


def replace_from_json(filepath: str, json_path: str) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    for rep in data.get("replacements", []):
        old = rep["old"]
        new = rep["new"]
        count = content.count(old)
        content = content.replace(old, new)
        print(f"  Replaced '{old}' -> '{new}' ({count} occurrences)")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Done: {filepath}")


def main() -> None:
    parser = argparse.ArgumentParser(description="UTF-8 safe replacement")
    parser.add_argument("file", help="Target file")
    parser.add_argument("old", nargs="?", help="String to replace")
    parser.add_argument("new", nargs="?", help="Replacement string")
    parser.add_argument("--json", help="JSON file with replacements array")
    args = parser.parse_args()

    if args.json:
        replace_from_json(args.file, args.json)
    elif args.old is not None and args.new is not None:
        replace_inline(args.file, args.old, args.new)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
