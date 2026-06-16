from __future__ import annotations

import json
import re
import shutil
import tempfile
from datetime import UTC, datetime
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from bookskill_studio.extractor import extract_text
from bookskill_studio.i18n import Strings, get_strings, resolve_lang
from bookskill_studio.validator import validate_skill_dir


ZH_STOPWORDS = {
    "一个",
    "一些",
    "可以",
    "我们",
    "他们",
    "这个",
    "那个",
    "因为",
    "所以",
    "如果",
    "但是",
    "以及",
    "进行",
    "需要",
    "应该",
    "必须",
    "使用",
    "通过",
    "对于",
    "已经",
    "还是",
    "就是",
    "不是",
    "没有",
    "什么",
    "如何",
    "这样",
    "那样",
    "其中",
    "这种",
    "那些",
    "这些",
    "作为",
    "成为",
    "之后",
    "之前",
    "然后",
    "而且",
    "或者",
}


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "by",
    "for",
    "from",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "we",
    "when",
    "with",
    "you",
}


@dataclass
class Chapter:
    number: int
    title: str
    body: str


def compile_book(
    input_path: Path,
    output_dir: Path,
    skill_name: str | None = None,
    lang: str = "auto",
) -> dict:
    return compile_sources([input_path], output_dir, skill_name, lang=lang)


def compile_sources(
    source_paths: list[Path],
    output_dir: Path,
    skill_name: str | None = None,
    lang: str = "auto",
) -> dict:
    if not source_paths:
        raise ValueError("At least one source path is required.")

    extracted_sources = []
    for source_path in source_paths:
        source_text = extract_text(source_path)
        extracted_sources.append((source_path, source_text))

    primary_path, primary_text = extracted_sources[0]
    corpus = build_corpus(extracted_sources)
    resolved_lang = resolve_lang(lang, corpus)
    strings = get_strings(resolved_lang)
    title = detect_title(primary_path, primary_text)
    author = detect_author(primary_text, strings)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    chapters = detect_chapters(corpus, strings, resolved_lang)
    skill_slug = skill_name or slugify(title, fallback="book-skill")

    output_dir.mkdir(parents=True, exist_ok=True)
    chapters_dir = output_dir / "chapters"
    references_dir = output_dir / "references"
    chapters_dir.mkdir(exist_ok=True)
    references_dir.mkdir(exist_ok=True)

    chapter_rows = []
    topic_rows = []
    concept_rows = []
    cheatsheet_rows = []
    evidence_sections = []

    for chapter in chapters:
        chapter_slug = slugify(chapter.title, fallback=f"chapter-{chapter.number:02d}")
        chapter_filename = f"ch{chapter.number:02d}-{chapter_slug}.md"
        concepts = extract_concepts(chapter.body, resolved_lang)
        rules = extract_rules(chapter.body, resolved_lang, strings)
        summary = summarize(chapter.body, resolved_lang, strings)
        takeaways = concepts[:3] or [strings.default_takeaway]
        chapter_rows.append(
            (
                chapter.number,
                chapter.title,
                chapter_filename,
                ", ".join(concepts[:2]) or strings.core_concepts,
            )
        )

        chapter_path = chapters_dir / chapter_filename
        chapter_path.write_text(
            render_chapter(chapter, summary, concepts, rules, takeaways, strings),
            encoding="utf-8",
        )

        for concept in concepts[:5]:
            topic_rows.append(f"- **{concept}** -> ch{chapter.number:02d}")
            concept_rows.append(f"- **{concept}** — {summary} (Ch {chapter.number})")

        for rule in rules[:3]:
            cheatsheet_rows.append(f"- {strings.rule_prefix.format(when=rule['when'], do=rule['do'])}")

        evidence_sections.append(render_evidence_section(chapter, summary, concepts, rules, strings))

    (references_dir / "concepts.md").write_text(
        f"# {strings.concepts_title}\n\n" + "\n".join(dedupe_keep_order(concept_rows)) + "\n",
        encoding="utf-8",
    )
    (references_dir / "cheatsheet.md").write_text(
        f"# {strings.cheatsheet_title}\n\n"
        + "\n".join(dedupe_keep_order(cheatsheet_rows) or [strings.cheatsheet_fallback])
        + "\n",
        encoding="utf-8",
    )
    (references_dir / "evidence-map.md").write_text(
        f"# {strings.evidence_map_title}\n\n" + "\n\n".join(evidence_sections) + "\n",
        encoding="utf-8",
    )

    skill_path = output_dir / "SKILL.md"
    skill_path.write_text(
        render_skill(
            skill_slug=skill_slug,
            title=title,
            author=author,
            chapters=chapter_rows,
            topic_rows=dedupe_keep_order(topic_rows),
            strings=strings,
        ),
        encoding="utf-8",
    )

    (output_dir / "validation-report.md").write_text(
        f"# {strings.validation_title}\n\n{strings.validation_pending}\n",
        encoding="utf-8",
    )
    (output_dir / "validation-report.html").write_text(
        f"<!doctype html><html lang=\"{resolved_lang}\"><body><p>{strings.validation_pending}</p></body></html>\n",
        encoding="utf-8",
    )
    manifest_payload = {
        "name": skill_slug,
        "title": title,
        "author": author,
        "lang": resolved_lang,
        "source_path": str(primary_path.resolve()),
        "sources": [str(path.resolve()) for path, _ in extracted_sources],
        "chapter_count": len(chapters),
        "generated_at": datetime.now(UTC).isoformat(),
        "validation_score": None,
        "validation_ok": None,
    }
    (output_dir / "bookskill-manifest.json").write_text(
        json.dumps(
            manifest_payload,
            indent=2,
            ensure_ascii=(resolved_lang != "zh"),
        )
        + "\n",
        encoding="utf-8",
    )
    report = validate_skill_dir(output_dir)
    (output_dir / "validation-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=(resolved_lang != "zh")) + "\n",
        encoding="utf-8",
    )
    (output_dir / "validation-report.md").write_text(
        render_validation_report(report, primary_path, skill_slug, strings),
        encoding="utf-8",
    )
    (output_dir / "validation-report.html").write_text(
        render_validation_html(report, primary_path, skill_slug, strings, resolved_lang),
        encoding="utf-8",
    )
    manifest_payload["validation_score"] = report["score"]
    manifest_payload["validation_ok"] = report["ok"]
    (output_dir / "bookskill-manifest.json").write_text(
        json.dumps(
            manifest_payload,
            indent=2,
            ensure_ascii=(resolved_lang != "zh"),
        )
        + "\n",
        encoding="utf-8",
    )
    return report


def update_book(
    skill_dir: Path,
    input_path: Path,
    skill_name: str | None = None,
    lang: str = "auto",
) -> dict:
    manifest = load_manifest(skill_dir)
    existing_sources = manifest.get("sources") or [manifest.get("source_path")]
    existing_sources = [Path(source) for source in existing_sources if source]
    merged_sources = dedupe_paths(existing_sources + [input_path])
    target_name = skill_name or manifest.get("name")
    target_lang = lang if lang != "auto" else manifest.get("lang", "auto")
    staging_dir = Path(tempfile.mkdtemp(prefix=f"{skill_dir.name}-staging-", dir=skill_dir.parent))
    try:
        report = compile_sources(merged_sources, staging_dir, target_name, lang=target_lang)
        publish_compiled_skill(staging_dir, skill_dir)
        return report
    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)


def detect_title(input_path: Path, source_text: str) -> str:
    for line in source_text.splitlines():
        cleaned = line.strip().lstrip("#").strip()
        if cleaned:
            return cleaned[:80]
    return input_path.stem.replace("-", " ").title()


def detect_author(source_text: str, strings: Strings) -> str:
    match = re.search(r"(?im)^author:\s*(.+)$", source_text)
    if match:
        return match.group(1).strip()
    match = re.search(r"(?m)^作者[:：]\s*(.+)$", source_text)
    return match.group(1).strip() if match else strings.unknown_author


def detect_chapters(source_text: str, strings: Strings, lang: str) -> list[Chapter]:
    lines = source_text.splitlines()
    chapter_markers: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        heading_match = re.match(r"^(#{1,2})\s+(.+)", stripped)
        if heading_match:
            heading_level = len(heading_match.group(1))
            if heading_level == 2 or (heading_level == 1 and idx != 0):
                chapter_markers.append((idx, heading_match.group(2).strip()))
        elif re.match(r"(?i)^chapter\s+\d+[:\s-]", stripped):
            chapter_markers.append((idx, stripped))
        elif re.match(r"^第[0-9一二三四五六七八九十百千]+章", stripped):
            chapter_markers.append((idx, stripped))

    if not chapter_markers:
        paragraphs = [p.strip() for p in source_text.split("\n\n") if p.strip()]
        chunk_size = max(1, len(paragraphs) // 3)
        chapters = []
        for index, start in enumerate(range(0, len(paragraphs), chunk_size), start=1):
            body = "\n\n".join(paragraphs[start : start + chunk_size])
            chapters.append(Chapter(index, strings.section_title.format(index=index), body))
        return chapters or [Chapter(1, strings.overview, source_text.strip())]

    chapters: list[Chapter] = []
    for number, (start_idx, title) in enumerate(chapter_markers, start=1):
        end_idx = chapter_markers[number][0] if number < len(chapter_markers) else len(lines)
        body = "\n".join(lines[start_idx + 1 : end_idx]).strip()
        if not body:
            body = strings.no_body_text
        chapters.append(Chapter(number, title, body))
    return chapters


def summarize(body: str, lang: str, strings: Strings) -> str:
    if lang == "zh":
        sentences = [part.strip() for part in re.split(r"(?<=[。！？])", normalize_whitespace(body)) if part.strip()]
    else:
        sentences = re.split(r"(?<=[.!?])\s+", normalize_whitespace(body))
    summary = " ".join(sentences[:2]).strip()
    return summary or strings.default_summary


def extract_concepts(body: str, lang: str) -> list[str]:
    if lang == "zh":
        tokens = re.findall(r"[\u4e00-\u9fff]{2,8}", body)
        ranked = Counter(token for token in tokens if token not in ZH_STOPWORDS)
        return [token for token, _ in ranked.most_common(6)]
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", body.lower())
    ranked = Counter(token for token in tokens if token not in STOPWORDS)
    concepts = [token.replace("-", " ") for token, _ in ranked.most_common(6)]
    return [concept.title() for concept in concepts]


def extract_rules(body: str, lang: str, strings: Strings) -> list[dict[str, str]]:
    if lang == "zh":
        sentences = [part.strip() for part in re.split(r"(?<=[。！？])", normalize_whitespace(body)) if part.strip()]
        rules = []
        for sentence in sentences:
            if "当" in sentence and ("应该" in sentence or "必须" in sentence):
                match = re.search(r"当(.+)", sentence)
                when_part = match.group(1).strip().strip("。") if match else strings.rule_source_conditions
                do_part = sentence.strip().rstrip("。")
                rules.append({"when": when_part[:90], "do": do_part[:120]})
            elif sentence.startswith("使用") or sentence.startswith("优先"):
                rules.append({"when": strings.rule_when_context, "do": sentence.strip().rstrip("。")[:120]})
        return rules[:5]

    sentences = re.split(r"(?<=[.!?])\s+", normalize_whitespace(body))
    rules = []
    for sentence in sentences:
        lowered = sentence.lower()
        if "when " in lowered and (" should " in lowered or " must " in lowered):
            match = re.search(r"(?i)\bwhen\b(.+)", sentence)
            when_part = match.group(1).strip().strip(".") if match else strings.rule_source_conditions
            do_part = sentence.strip().rstrip(".")
            rules.append({"when": when_part[:90], "do": do_part[:120]})
        elif lowered.startswith("use ") or lowered.startswith("prefer "):
            rules.append({"when": strings.rule_when_context, "do": sentence.strip().rstrip(".")[:120]})
    return rules[:5]


def render_chapter(
    chapter: Chapter,
    summary: str,
    concepts: list[str],
    rules: list[dict[str, str]],
    takeaways: list[str],
    strings: Strings,
) -> str:
    concept_lines = (
        "\n".join(f"- **{concept}**: {summary}" for concept in concepts[:4])
        or f"- **{strings.core_idea}**: {strings.review_source}"
    )
    rule_lines = (
        "\n".join(f"- {strings.rule_prefix.format(when=rule['when'], do=rule['do'])}" for rule in rules[:3])
        or f"- {strings.rule_fallback}"
    )
    takeaway_lines = "\n".join(f"1. {item}" for item in takeaways[:3]) or f"1. {strings.takeaway_read_summary}"
    return (
        f"# {strings.chapter_heading.format(number=chapter.number, title=chapter.title)}\n\n"
        f"## {strings.core_idea_heading}\n{summary}\n\n"
        f"## {strings.frameworks_heading}\n{concept_lines}\n\n"
        f"## {strings.decision_rules_heading}\n{rule_lines}\n\n"
        f"## {strings.takeaways_heading}\n{takeaway_lines}\n"
    )


def render_evidence_section(
    chapter: Chapter,
    summary: str,
    concepts: list[str],
    rules: list[dict[str, str]],
    strings: Strings,
) -> str:
    concept_line = ", ".join(concepts[:5]) or strings.evidence_core_idea
    rule_line = (
        "; ".join(strings.rule_joiner.format(when=rule["when"], do=rule["do"]) for rule in rules[:2])
        or strings.evidence_no_rules
    )
    excerpt = normalize_whitespace(chapter.body)[:240]
    return (
        f"## Ch {chapter.number}: {chapter.title}\n\n"
        f"**{strings.evidence_summary}:** {summary}\n\n"
        f"**{strings.evidence_concepts}:** {concept_line}\n\n"
        f"**{strings.evidence_rules}:** {rule_line}\n\n"
        f"**{strings.evidence_excerpt}:** {excerpt}...\n"
    )


def render_skill(
    skill_slug: str,
    title: str,
    author: str,
    chapters: list[tuple[int, str, str, str]],
    topic_rows: list[str],
    strings: Strings,
) -> str:
    chapter_index = "\n".join(
        f"| [ch{number:02d}](chapters/{filename}) | {chapter_title} | {concepts or strings.core_ideas} |"
        for number, chapter_title, filename, concepts in chapters
    )
    topic_index = "\n".join(topic_rows or [f"- **{strings.topic_overview}** -> ch01"])
    return (
        f"---\n"
        f"name: {skill_slug}\n"
        f'description: "{strings.skill_description.format(title=title)}"\n'
        f"---\n\n"
        f"# {title}\n\n"
        f"**{strings.author_label}:** {author}\n\n"
        f"## {strings.how_to_use}\n\n"
        f"- {strings.use_topic_jump}\n"
        f"- {strings.use_evidence_map}\n"
        f"- {strings.use_cheatsheet}\n\n"
        f"## {strings.chapter_index}\n\n"
        f"| {strings.chapter_col} | {strings.title_col} | {strings.key_concepts_col} |\n"
        f"|---|---|---|\n"
        f"{chapter_index}\n\n"
        f"## {strings.topic_index}\n\n"
        f"{topic_index}\n\n"
        f"## {strings.supporting_files}\n\n"
        f"- [references/concepts.md](references/concepts.md)\n"
        f"- [references/cheatsheet.md](references/cheatsheet.md)\n"
        f"- [references/evidence-map.md](references/evidence-map.md)\n"
    )


def slugify(value: str, fallback: str = "section") -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-") or fallback


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen = set()
    ordered = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def render_validation_report(report: dict, source_path: Path, skill_slug: str, strings: Strings) -> str:
    checks = "\n".join(
        f"- **{name}**: {strings.validation_pass if passed else strings.validation_fail}"
        for name, passed in report["checks"].items()
    )
    missing = "\n".join(f"- `{item}`" for item in report["missing"]) or f"- {strings.validation_none}"
    broken_links = "\n".join(f"- `{item}`" for item in report["broken_links"]) or f"- {strings.validation_none}"
    status = strings.validation_pass if report["ok"] else strings.validation_fail
    return (
        f"# {strings.validation_title}\n\n"
        f"- **{strings.validation_skill_slug}**: `{skill_slug}`\n"
        f"- **{strings.validation_source}**: `{source_path}`\n"
        f"- **{strings.validation_score}**: {report['score']}\n"
        f"- **{strings.validation_status}**: {status}\n\n"
        f"## {strings.validation_checks}\n\n"
        f"{checks}\n\n"
        f"## {strings.validation_missing}\n\n"
        f"{missing}\n\n"
        f"## {strings.validation_broken}\n\n"
        f"{broken_links}\n"
    )


def render_validation_html(
    report: dict,
    source_path: Path,
    skill_slug: str,
    strings: Strings,
    lang: str,
) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{name}</td>"
        f"<td class=\"{'pass' if passed else 'fail'}\">"
        f"{strings.validation_pass if passed else strings.validation_fail}"
        f"</td>"
        "</tr>"
        for name, passed in report["checks"].items()
    )
    missing = "".join(f"<li><code>{item}</code></li>" for item in report["missing"]) or f"<li>{strings.validation_none}</li>"
    broken = "".join(f"<li><code>{item}</code></li>" for item in report["broken_links"]) or f"<li>{strings.validation_none}</li>"
    status_class = "pass" if report["ok"] else "fail"
    status_label = strings.validation_pass if report["ok"] else strings.validation_fail
    return f"""<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{strings.html_title}</title>
    <style>
      :root {{
        --bg: #f4efe7;
        --panel: #fff9f0;
        --ink: #1f2933;
        --muted: #6b7280;
        --line: #d7cfc1;
        --pass: #1f7a4d;
        --fail: #b8412e;
        --accent: #c96f2d;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Georgia, "Times New Roman", serif;
        background:
          radial-gradient(circle at top left, rgba(201,111,45,.18), transparent 28rem),
          linear-gradient(180deg, #fbf7f1 0%, var(--bg) 100%);
        color: var(--ink);
      }}
      main {{
        max-width: 980px;
        margin: 0 auto;
        padding: 48px 20px 64px;
      }}
      .hero {{
        background: rgba(255,255,255,.72);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(215,207,193,.9);
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 18px 50px rgba(63, 42, 23, 0.08);
      }}
      h1, h2 {{ margin: 0 0 12px; }}
      p {{ color: var(--muted); line-height: 1.6; }}
      .score {{
        display: inline-flex;
        align-items: center;
        gap: 12px;
        margin-top: 18px;
        padding: 10px 14px;
        border-radius: 999px;
        background: #fff;
        border: 1px solid var(--line);
      }}
      .score strong {{
        font-size: 1.15rem;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 18px;
        margin-top: 24px;
      }}
      .card {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 20px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
      }}
      th, td {{
        padding: 12px 10px;
        border-bottom: 1px solid var(--line);
        text-align: left;
      }}
      code {{
        font-family: "SFMono-Regular", Menlo, monospace;
        font-size: .92rem;
      }}
      .pass {{ color: var(--pass); }}
      .fail {{ color: var(--fail); }}
      .badge {{
        display: inline-block;
        margin-top: 6px;
        padding: 6px 10px;
        border-radius: 999px;
        background: {'rgba(31,122,77,.12)' if report["ok"] else 'rgba(184,65,46,.12)'};
        color: {'var(--pass)' if report["ok"] else 'var(--fail)'};
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        font-size: .75rem;
      }}
      ul {{ margin: 12px 0 0; padding-left: 20px; }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <h1>{strings.validation_title}</h1>
        <p>{strings.html_intro}</p>
        <div class="score">
          <strong>{report["score"]}/100</strong>
          <span class="badge {status_class}">{status_label}</span>
        </div>
        <div class="grid">
          <div class="card">
            <h2>{strings.validation_source}</h2>
            <p><code>{source_path}</code></p>
          </div>
          <div class="card">
            <h2>{strings.validation_skill_slug}</h2>
            <p><code>{skill_slug}</code></p>
          </div>
          <div class="card">
            <h2>{strings.html_coverage}</h2>
            <p>{strings.html_chapters.format(chapter_count=report["chapter_count"], evidence_sections=report["evidence_sections"])}</p>
          </div>
        </div>
      </section>
      <section class="card" style="margin-top: 22px;">
        <h2>{strings.validation_checks}</h2>
        <table>
          <thead>
            <tr><th>{strings.html_check_col}</th><th>{strings.html_status_col}</th></tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </section>
      <section class="grid">
        <div class="card">
          <h2>{strings.validation_missing}</h2>
          <ul>{missing}</ul>
        </div>
        <div class="card">
          <h2>{strings.validation_broken}</h2>
          <ul>{broken}</ul>
        </div>
      </section>
    </main>
  </body>
</html>
"""


def build_corpus(extracted_sources: list[tuple[Path, str]]) -> str:
    parts = []
    for source_path, source_text in extracted_sources:
        parts.append(f"[[SOURCE: {source_path.name}]]\n{source_text.strip()}")
    return "\n\n".join(parts)


def load_manifest(skill_dir: Path) -> dict:
    manifest_path = skill_dir / "bookskill-manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found in skill directory: {skill_dir}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def dedupe_paths(paths: list[Path]) -> list[Path]:
    seen = set()
    ordered = []
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            ordered.append(resolved)
    return ordered


def publish_compiled_skill(staging_dir: Path, target_dir: Path) -> None:
    if staging_dir.resolve() == target_dir.resolve():
        raise ValueError("Staging directory and target directory must be different.")

    if not staging_dir.exists():
        raise FileNotFoundError(f"Staging directory not found: {staging_dir}")

    if not target_dir.exists():
        staging_dir.rename(target_dir)
        return

    backup_dir = target_dir.parent / f".{target_dir.name}.backup-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
    target_dir.rename(backup_dir)
    try:
        staging_dir.rename(target_dir)
    except Exception:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        backup_dir.rename(target_dir)
        raise
    else:
        shutil.rmtree(backup_dir)
