# pdf-section-splitter

Split a long, text-based PDF into separate sections (lessons, chapters, units...) by
reading the section number printed on each page. Each section is saved as its own PDF
plus one PNG image per page.

Useful when you want to:

- feed a textbook or manual to an AI assistant one chapter at a time
- study or review a long PDF in small pieces
- extract chapters without opening a PDF editor and counting pages by hand

## Install

Requires Python 3.9+.

```bash
python -m pip install -r requirements.txt
```

## Usage

```bash
# 1. See what the script detects (writes nothing)
python split_pdf_sections.py book.pdf --list

# 2. Split everything
python split_pdf_sections.py book.pdf

# 3. Only chapters 2 to 4, with a different label
python split_pdf_sections.py book.pdf --label Chapter --from 2 --to 4

# PDF files only, no images
python split_pdf_sections.py book.pdf --no-images
```

Output:

```
sections/
  lesson_01/
    lesson_01.pdf
    page_002.png
    page_003.png
  lesson_02/
    ...
```

## How detection works

For every page the script looks for a section number in this order:

1. A footer like `Lesson 1 – January 2000 – Page 2` or `Chapter 3 | Page 12`
2. A heading at the start of the page like `LESSON 1 – TITLE`

Pages with no match belong to the previous section. Pages before the first section
(cover, table of contents) are skipped.

### Custom patterns

If your PDF uses a different format, pass your own regular expressions. Each must
contain exactly one capture group: the section number.

```bash
python split_pdf_sections.py book.pdf --footer-regex "Unit\s+(\d+)\s*\|\s*Page"
python split_pdf_sections.py book.pdf --header-regex "^\s*CHAPTER\s+(\d+)"
```

## Options

| Option | Meaning |
|---|---|
| `--label` | Word before the number (default `Lesson`) |
| `--from`, `--to` | First and last section number |
| `--out` | Output folder (default `sections`) |
| `--dpi` | Image resolution (default 150) |
| `--list` | Print detected sections only |
| `--no-images` / `--no-pdf` | Skip images or PDFs |
| `--footer-regex`, `--header-regex` | Custom patterns |

## Limitations

- The PDF must contain real text. Scanned PDFs (images only) need OCR first.
- Detection relies on a section number printed on the pages. A section with no
  number on any page cannot be found.
- Appendices placed after the last section may be merged into that section.

## A note on copyrighted material

Only process documents you have the right to use. This repository ignores `*.pdf`
files by default so you do not commit books by accident.

## License

MIT, see [LICENSE](LICENSE).
