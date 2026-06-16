# BookSkill Studio

[中文文档](README.zh-CN.md)

Turn any book or long doc into an evidence-backed agent skill in under five minutes.

BookSkill Studio is a small, deterministic CLI for turning source material into:

- an installable `SKILL.md`
- chapter-sized companion files
- traceable evidence maps
- machine-readable validation output
- a one-command local install flow

## Demo Preview

![BookSkill Studio demo preview](assets/demo-terminal-v3.png)

## Before / After

**Before:** a long book or document folder that an agent has to rediscover every session.

**After:** a structured skill package with:

- `SKILL.md`
- `chapters/`
- `references/cheatsheet.md`
- `references/evidence-map.md`
- `validation-report.html`
- `validation-report.json`

## Quick Start

Try the built-in demo:

```bash
cd bookskill-studio
python3 -m pip install -e .
python3 -m bookskill_studio doctor
python3 -m bookskill_studio demo --output demo-output
python3 -m bookskill_studio validate demo-output
python3 -m bookskill_studio install demo-output --target codex
python3 -m bookskill_studio open-report demo-output
```

Compile your own file:

```bash
python3 -m bookskill_studio run examples/demo-book.md --output my-book-skill --install --target codex
python3 -m bookskill_studio run my-book.md --output my-book-skill --lang zh
```

Use `--lang auto` (default), `--lang en`, or `--lang zh` to control generated skill language. See [README.zh-CN.md](README.zh-CN.md) for Chinese docs.

Fold in a new source later:

```bash
python3 -m bookskill_studio update my-book-skill docs/new-notes.md
```

Open the HTML validation report directly:

```bash
python3 -m bookskill_studio open-report my-book-skill
```

This MVP supports `.md`, `.txt`, `.epub`, and `.pdf`.
PDF support uses `pdftotext`, so run `doctor` first if you plan to compile PDFs.

If you only remember one command, start here:

```bash
python3 -m bookskill_studio demo --output demo-output
```

## Demo Output

```text
demo-output/
  SKILL.md
  chapters/
    ch01-why-books-need-compile-steps.md
    ch02-design-for-reuse.md
    ch03-build-trust-with-evidence.md
  references/
    cheatsheet.md
    concepts.md
    evidence-map.md
  bookskill-manifest.json
  validation-report.md
  validation-report.html
  validation-report.json
```

## What This MVP Does

- Supports `.md`, `.txt`, `.epub`, and `.pdf` inputs.
- Detects chapters from Markdown headings or `Chapter` markers.
- Generates a small, installable skill structure.
- Produces an evidence map so concepts point back to chapter sources.
- Produces machine-readable, Markdown, and HTML validation reports.
- Writes a small manifest with source path, chapter count, and validation status.
- Validates structure, frontmatter, links, and chapter coverage.
- Can install the compiled skill into a local Codex, Claude, Cursor, or generic agent skill home.

## CLI

```bash
python3 -m bookskill_studio doctor
python3 -m bookskill_studio demo --output demo-output
python3 -m bookskill_studio run <book.md> --output outdir
python3 -m bookskill_studio validate <skill-dir>
python3 -m bookskill_studio install <skill-dir> --target codex
python3 -m bookskill_studio open-report <skill-dir>
python3 -m bookskill_studio run <book.md> --output outdir --install --target codex
python3 -m bookskill_studio update <skill-dir> <new-source.md>
```

## Why This Exists

Most book-to-skill experiments stop at generation. This repo aims one layer higher:

- deterministic output structure
- built-in demo
- validator-first workflow
- evidence-backed concepts
- one-command local install
- inline compile-plus-install flow
- fold-in update flow
- screenshot-friendly validation HTML
- GitHub-ready project skeleton

## Development

Run tests:

```bash
python3 -m pytest
```

## Release Checklist

Use this before publishing a tag or announcing the repo:

- [ ] `python3 -m pytest`
- [ ] `python3 -m bookskill_studio doctor`
- [ ] `python3 -m bookskill_studio demo --output demo-output`
- [ ] `python3 -m bookskill_studio validate demo-output`
- [ ] `python3 -m bookskill_studio open-report demo-output`
- [ ] `python3 -m bookskill_studio install demo-output --skills-home /tmp/test-skills`
- [ ] confirm README first screen reads clearly on GitHub
- [ ] add the GitHub repository URL and topic tags
- [ ] create a `v0.1.0` release note

Suggested GitHub description and topic tags live in [GITHUB_METADATA.md](GITHUB_METADATA.md).

Run the GitHub Actions equivalent locally:

```bash
python3 -m bookskill_studio doctor
python3 -m bookskill_studio demo --output demo-output
python3 -m bookskill_studio validate demo-output
python3 -m bookskill_studio install demo-output --skills-home /tmp/test-skills
python3 -m pytest
```
