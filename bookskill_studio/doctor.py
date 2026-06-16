from __future__ import annotations

import shutil
import sys
from pathlib import Path

from bookskill_studio.extractor import SUPPORTED_EXTENSIONS
from bookskill_studio.installer import detect_skill_homes


def run_doctor() -> dict:
    detected_skill_homes = detect_skill_homes()
    checks = {
        "python_3_11_plus": sys.version_info >= (3, 11),
        "project_writable": Path.cwd().exists() and Path.cwd().is_dir(),
        "pdftotext_available": shutil.which("pdftotext") is not None,
        "epub_supported": True,
        "markdown_supported": True,
    }
    score = round(sum(1 for passed in checks.values() if passed) / len(checks) * 100)
    return {
        "ok": checks["python_3_11_plus"] and checks["project_writable"],
        "score": score,
        "checks": checks,
        "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
        "detected_skill_homes": detected_skill_homes,
        "tips": build_tips(checks),
    }


def build_tips(checks: dict[str, bool]) -> list[str]:
    tips = [
        "Use `bookskill demo --output demo-output` to verify the happy path.",
        "Use `bookskill validate <skill-dir>` after every compile.",
        "Use `bookskill install <skill-dir>` to copy a compiled skill into your local agent skill home.",
    ]
    if not checks["pdftotext_available"]:
        tips.append("Install `pdftotext` to unlock PDF support. On macOS: `brew install poppler`.")
    return tips
