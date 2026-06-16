from __future__ import annotations

import re
from pathlib import Path


def validate_skill_dir(skill_dir: Path) -> dict:
    required = [
        skill_dir / "SKILL.md",
        skill_dir / "chapters",
        skill_dir / "references" / "cheatsheet.md",
        skill_dir / "references" / "concepts.md",
        skill_dir / "references" / "evidence-map.md",
        skill_dir / "validation-report.md",
        skill_dir / "validation-report.html",
        skill_dir / "bookskill-manifest.json",
    ]
    missing = [str(path.relative_to(skill_dir)) for path in required if not path.exists()]

    skill_path = skill_dir / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
    frontmatter_ok = bool(re.search(r"(?s)^---\nname: .+\ndescription: .+\n---", skill_text))
    chapter_links = re.findall(r"\(chapters/([^)]+)\)", skill_text)
    broken_links = [link for link in chapter_links if not (skill_dir / "chapters" / link).exists()]
    chapter_count = len(list((skill_dir / "chapters").glob("*.md"))) if (skill_dir / "chapters").exists() else 0
    evidence_has_sections = (skill_dir / "references" / "evidence-map.md").read_text(encoding="utf-8").count("## Ch ") if (skill_dir / "references" / "evidence-map.md").exists() else 0

    checks = {
        "required_files": not missing,
        "frontmatter": frontmatter_ok,
        "chapter_links": not broken_links,
        "chapter_count": chapter_count > 0,
        "evidence_coverage": evidence_has_sections >= chapter_count if chapter_count else False,
    }
    score = round(sum(1 for passed in checks.values() if passed) / len(checks) * 100)
    return {
        "ok": all(checks.values()),
        "score": score,
        "checks": checks,
        "missing": missing,
        "broken_links": broken_links,
        "chapter_count": chapter_count,
        "evidence_sections": evidence_has_sections,
    }
