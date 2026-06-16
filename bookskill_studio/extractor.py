from __future__ import annotations

import html
import re
import shutil
import subprocess
import zipfile
from pathlib import Path


SUPPORTED_EXTENSIONS = {".md", ".txt", ".epub", ".pdf"}


def extract_text(input_path: Path) -> str:
    suffix = input_path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return input_path.read_text(encoding="utf-8")
    if suffix == ".epub":
        return extract_epub_text(input_path)
    if suffix == ".pdf":
        return extract_pdf_text(input_path)
    raise ValueError(f"Unsupported file type: {suffix}")


def extract_epub_text(input_path: Path) -> str:
    parts: list[str] = []
    with zipfile.ZipFile(input_path) as archive:
        html_files = sorted(
            name
            for name in archive.namelist()
            if name.lower().endswith((".xhtml", ".html", ".htm"))
        )
        for name in html_files:
            raw = archive.read(name).decode("utf-8", errors="ignore")
            text = html_to_text(raw)
            if text:
                parts.append(text)
    if not parts:
        raise ValueError(f"No readable HTML content found in EPUB: {input_path}")
    return "\n\n".join(parts)


def extract_pdf_text(input_path: Path) -> str:
    if shutil.which("pdftotext") is None:
        raise ValueError("PDF extraction requires `pdftotext` to be installed and available on PATH.")
    result = subprocess.run(
        ["pdftotext", str(input_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    text = result.stdout.strip()
    if not text:
        raise ValueError(f"pdftotext produced empty output for: {input_path}")
    return text


def html_to_text(raw_html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw_html)
    text = re.sub(r"(?i)</(p|div|section|article|h1|h2|h3|h4|li|ul|ol|br)>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\r", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

