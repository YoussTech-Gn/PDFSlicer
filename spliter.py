#!/usr/bin/env python3
"""
split_pdf_sections.py
Split a text-based PDF into sections (lessons, chapters, units...) by reading the
section number printed on each page (in the footer or in the first-page heading).

For every section it writes a folder containing:
  - <label>_NN.pdf       only the pages of that section
  - page_XXX.png ...     one image per page (optional)

Examples:
  python split_pdf_sections.py book.pdf --list
  python split_pdf_sections.py book.pdf --label Chapter --from 1 --to 3
  python split_pdf_sections.py book.pdf --footer-regex "Unit\\s+(\\d+)\\s*\\|\\s*Page"
"""
import argparse
import re
import sys
from pathlib import Path

import pymupdf  # PyMuPDF


def build_patterns(label, footer_regex, header_regex):
    """Return (footer, header) compiled patterns. Each must have ONE capture group: the number."""
    lab = re.escape(label)
    if footer_regex is None:
        # e.g. "Lesson 1 – January 2000 – Page 2", "Chapter 3 | Page 12"
        footer_regex = rf"{lab}\s+(\d+)\s*[–—\-|:·]\s*[^\n]{{0,60}}?\bPage\s+\d+"
    if header_regex is None:
        # e.g. "LESSON 1 – TITLE" at the very start of the page text
        header_regex = rf"^\s*{lab.upper()}\s+(\d+)\b"
    return re.compile(footer_regex, re.I), re.compile(header_regex)


def section_of_page(text, footer, header):
    """Return the section number of a page, or None."""
    found = footer.findall(text)
    if found:
        return int(found[-1])          # last footer match on the page
    m = header.search(text)
    return int(m.group(1)) if m else None


def group_pages(doc, footer, header):
    """Return {section number: [page indexes (0-based)]}. Pages before the first section are skipped."""
    groups, current = {}, None
    for i, page in enumerate(doc):
        n = section_of_page(page.get_text(), footer, header)
        if n is not None:
            current = n
        if current is None:
            continue
        groups.setdefault(current, []).append(i)
    return groups


def main():
    ap = argparse.ArgumentParser(description="Split a PDF into sections by page footer/heading.")
    ap.add_argument("pdf")
    ap.add_argument("--out", default="sections", help="output folder (default: sections)")
    ap.add_argument("--label", default="Lesson", help="word before the number, e.g. Lesson, Chapter, Unit")
    ap.add_argument("--footer-regex", help="custom footer pattern with ONE capture group (the number)")
    ap.add_argument("--header-regex", help="custom heading pattern with ONE capture group (the number)")
    ap.add_argument("--from", dest="first", type=int, default=1, help="first section number")
    ap.add_argument("--to", dest="last", type=int, default=None, help="last section number")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--list", action="store_true", help="only print the detected sections, write nothing")
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()

    footer, header = build_patterns(a.label, a.footer_regex, a.header_regex)
    doc = pymupdf.open(a.pdf)
    groups = group_pages(doc, footer, header)
    if not groups:
        sys.exit("No sections detected. Is the PDF scanned (no text layer)? "
                 "Try --label or custom --footer-regex / --header-regex.")

    last = a.last if a.last is not None else max(groups)
    name = re.sub(r"\W+", "_", a.label.strip().lower()) or "section"

    for n in range(a.first, last + 1):
        pages = groups.get(n)
        if not pages:
            print(f"{a.label} {n}: not found, skipped")
            continue
        print(f"{a.label} {n}: {len(pages)} pages (pages {pages[0] + 1} to {pages[-1] + 1})")
        if a.list:
            continue

        folder = Path(a.out) / f"{name}_{n:02d}"
        folder.mkdir(parents=True, exist_ok=True)

        if not a.no_pdf:
            sub = pymupdf.open()
            for p in pages:
                sub.insert_pdf(doc, from_page=p, to_page=p)
            sub.save(folder / f"{name}_{n:02d}.pdf")
            sub.close()

        if not a.no_images:
            zoom = a.dpi / 72
            for p in pages:
                doc[p].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(folder / f"page_{p + 1:03d}.png")


if __name__ == "__main__":
    main()