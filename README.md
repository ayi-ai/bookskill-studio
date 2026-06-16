# BookSkill Studio

<p align="center">
  <a href="https://github.com/ayi-ai/bookskill-studio/actions/workflows/ci.yml"><img src="https://github.com/ayi-ai/bookskill-studio/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/ayi-ai/bookskill-studio/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ayi-ai/bookskill-studio?label=license" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <a href="https://github.com/ayi-ai/bookskill-studio/releases"><img src="https://img.shields.io/github/v/release/ayi-ai/bookskill-studio?label=release" alt="Release"></a>
  <img src="https://img.shields.io/badge/lang-en%20%7C%20zh-auto-orange" alt="Languages">
  <img src="https://img.shields.io/badge/install-codex%20%7C%20claude%20%7C%20cursor-blue" alt="Install targets">
</p>

<p align="center">
  <a href="#english"><strong>English</strong></a>
  &nbsp;·&nbsp;
  <a href="#zh"><strong>中文</strong></a>
</p>

<table>
  <tr>
    <td width="50%" valign="top">
      <strong>Turn any book or long doc into an evidence-backed agent skill in under five minutes.</strong><br><br>
      Deterministic CLI · built-in demo · validator · one-command install · <code>--lang en|zh|auto</code>
    </td>
    <td width="50%" valign="top">
      <strong>把任意书籍或长文档，在 5 分钟内编译成可追溯的 Agent Skill。</strong><br><br>
      确定性 CLI · 内置 demo · 校验报告 · 一键安装 · 支持 <code>--lang en|zh|auto</code>
    </td>
  </tr>
</table>

> GitHub 会根据浏览器语言自动显示 [README.zh-CN.md](README.zh-CN.md)。下方同页可直接看中英文全文。

<a id="english"></a>

## English

BookSkill Studio is a small, deterministic CLI for turning source material into:

- an installable `SKILL.md`
- chapter-sized companion files
- traceable evidence maps
- machine-readable validation output
- a one-command local install flow

### Demo Preview

<p align="center">
  <img src="assets/demo-flow.svg" alt="Book to skill flow" width="920" />
</p>

<table>
  <tr>
    <td width="58%" align="center" valign="top">
      <strong>CLI run</strong><br><br>
      <img src="assets/demo-terminal-v3.png" alt="BookSkill Studio terminal demo" width="100%" />
    </td>
    <td width="42%" align="center" valign="top">
      <strong>Validation report</strong><br><br>
      <img src="assets/demo-report-preview.svg" alt="Validation report preview" width="100%" />
    </td>
  </tr>
</table>

<p align="center"><sub>Animated GIF optional: install <a href="https://github.com/charmbracelet/vhs">vhs</a> and run <code>./scripts/generate-demo-gif.sh</code></sub></p>

### Before / After

**Before:** a long book or document folder that an agent has to rediscover every session.

**After:** a structured skill package with:

- `SKILL.md`
- `chapters/`
- `references/cheatsheet.md`
- `references/evidence-map.md`
- `validation-report.html`
- `validation-report.json`

### Quick Start

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

Use `--lang auto` (default), `--lang en`, or `--lang zh` to control generated skill language.

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

### Demo Output

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

### What This MVP Does

- Supports `.md`, `.txt`, `.epub`, and `.pdf` inputs.
- Detects chapters from Markdown headings or `Chapter` markers.
- Generates a small, installable skill structure.
- Produces an evidence map so concepts point back to chapter sources.
- Produces machine-readable, Markdown, and HTML validation reports.
- Writes a small manifest with source path, chapter count, and validation status.
- Validates structure, frontmatter, links, and chapter coverage.
- Can install the compiled skill into a local Codex, Claude, Cursor, or generic agent skill home.

### CLI

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

### Why This Exists

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

### Development

Run tests:

```bash
python3 -m pytest
```

### Release Checklist

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

---

<a id="zh"></a>

## 中文

BookSkill Studio 是一个轻量 CLI，能把源材料变成：

- 可安装的 `SKILL.md`
- 按章节拆分的配套文件
- 可追溯的证据映射
- 机器可读的校验报告
- 一键本地安装

### 快速开始

运行内置 demo：

```bash
cd bookskill-studio
python3 -m pip install -e .
python3 -m bookskill_studio doctor
python3 -m bookskill_studio demo --output demo-output
python3 -m bookskill_studio validate demo-output
python3 -m bookskill_studio install demo-output --target cursor
python3 -m bookskill_studio open-report demo-output
```

编译中文书籍：

```bash
python3 -m bookskill_studio run my-book.md --output my-book-skill --lang zh
python3 -m bookskill_studio run my-book.md --output my-book-skill --lang auto
```

### 语言支持

| 参数 | 说明 |
|---|---|
| `--lang auto` | 默认。按正文中文/英文字符比例自动选择 |
| `--lang zh` | 生成中文 Skill 模板、速查表、校验报告 |
| `--lang en` | 生成英文输出 |

中文源材料额外支持：

- Markdown 二级标题、`第X章` 章节识别
- 中文概念提取
- 「当…应该/必须…」规则识别
- 中文校验报告 HTML

### 支持的输入格式

`.md`、`.txt`、`.epub`、`.pdf`

PDF 依赖 `pdftotext`，使用前请先运行 `doctor`。

### CLI

```bash
python3 -m bookskill_studio doctor
python3 -m bookskill_studio demo --output demo-output [--lang zh]
python3 -m bookskill_studio run <book.md> --output outdir [--lang auto]
python3 -m bookskill_studio validate <skill-dir>
python3 -m bookskill_studio install <skill-dir> --target cursor
python3 -m bookskill_studio open-report <skill-dir>
python3 -m bookskill_studio update <skill-dir> <new-source.md>
```

### 开发

```bash
python3 -m pytest
```

<p align="center"><a href="#english">↑ Back to English</a></p>
