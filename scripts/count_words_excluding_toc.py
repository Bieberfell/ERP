import os
import re
import argparse
from collections import Counter


def get_text_pages_pypdf2(path):
    try:
        from PyPDF2 import PdfReader
    except Exception:
        return None
    texts = []
    reader = PdfReader(path)
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return texts


def get_text_pages_pdfminer(path):
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer
    except Exception:
        return None
    texts = []
    for page_layout in extract_pages(path):
        page_text = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                page_text.append(element.get_text())
        texts.append("".join(page_text))
    return texts


def is_toc_page(text):
    if not text:
        return False
    txt = text.strip()
    # direct heading
    if re.search(r'Inhaltsverzeichnis|Inhalt|Table of Contents|Inhalts-\w+', txt, re.I):
        return True
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if not lines:
        return False
    toc_like = 0
    for line in lines:
        # lines like "Kapitel 1 .................. 12" or "Einleitung  1"
        if re.search(r'\.{2,}\s*\d+$', line):
            toc_like += 1
            continue
        if re.search(r'\s\d{1,4}$', line) and len(line.split()) <= 8:
            toc_like += 1
            continue
    return toc_like >= 3


WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿÄÖÜäöüß]+", re.UNICODE)


def words_in_text(text):
    return WORD_RE.findall(text)


def process_pdf(path):
    # try PyPDF2 first, then pdfminer
    pages = get_text_pages_pypdf2(path)
    if pages is None:
        pages = get_text_pages_pdfminer(path)
    if pages is None:
        raise RuntimeError('Keine geeignete PDF-Bibliothek installiert (PyPDF2 oder pdfminer.six)')

    total_words = 0
    per_page = []
    for i, page_text in enumerate(pages, start=1):
        if is_toc_page(page_text):
            per_page.append((i, 0, True))
            continue
        w = words_in_text(page_text)
        per_page.append((i, len(w), False))
        total_words += len(w)
    return total_words, per_page


def count_all_pdfs(root):
    results = {}
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith('.pdf'):
                path = os.path.join(dirpath, fn)
                try:
                    cnt, per_page = process_pdf(path)
                except Exception as e:
                    results[path] = {'error': str(e)}
                    continue
                results[path] = {'words': cnt, 'pages': per_page}
                total += cnt
    return {'total_words': total, 'files': results}


def main():
    p = argparse.ArgumentParser(description='Count words in PDFs, excluding detected TOC pages')
    p.add_argument('root', nargs='?', default='.', help='Root folder to scan')
    args = p.parse_args()
    summary = count_all_pdfs(args.root)
    print('Gesamtwörter (ohne Inhaltsverzeichnisse):', summary['total_words'])
    for path, data in summary['files'].items():
        if 'error' in data:
            print(f"Fehler bei {path}: {data['error']}")
        else:
            print(f"{data['words']:7d}  {path}")
    return summary


if __name__ == '__main__':
    main()
