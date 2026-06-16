from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_demo_pipeline(tmp_path: Path) -> None:
    output_dir = tmp_path / "demo-output"
    subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "demo", "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
    )
    report = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert (output_dir / "SKILL.md").exists()
    assert (output_dir / "references" / "evidence-map.md").exists()
    assert (output_dir / "validation-report.html").exists()
    assert (output_dir / "bookskill-manifest.json").exists()


def test_validate_command_returns_zero_for_valid_output(tmp_path: Path) -> None:
    output_dir = tmp_path / "compiled"
    source = ROOT / "examples" / "demo-book.md"
    subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "run", str(source), "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "validate", str(output_dir)],
        cwd=ROOT,
        check=False,
    )
    assert result.returncode == 0


def test_doctor_command_returns_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "doctor"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["checks"]["markdown_supported"] is True


def test_epub_pipeline(tmp_path: Path) -> None:
    epub_path = tmp_path / "sample.epub"
    build_epub_fixture(epub_path)
    output_dir = tmp_path / "epub-output"
    subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "run", str(epub_path), "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
    )
    report = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert (output_dir / "validation-report.md").exists()
    assert (output_dir / "validation-report.html").exists()


def test_install_command_copies_skill_to_explicit_home(tmp_path: Path) -> None:
    output_dir = tmp_path / "compiled"
    skills_home = tmp_path / "skills-home"
    source = ROOT / "examples" / "demo-book.md"
    subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "run", str(source), "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bookskill_studio",
            "install",
            str(output_dir),
            "--skills-home",
            str(skills_home),
            "--name",
            "demo-installed",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    installed_path = Path(payload["installed_to"])
    assert installed_path == skills_home / "demo-installed"
    assert (installed_path / "SKILL.md").exists()


def test_run_with_install_flag_installs_after_compile(tmp_path: Path) -> None:
    output_dir = tmp_path / "compiled-inline"
    skills_home = tmp_path / "inline-home"
    source = ROOT / "examples" / "demo-book.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bookskill_studio",
            "run",
            str(source),
            "--output",
            str(output_dir),
            "--install",
            "--skills-home",
            str(skills_home),
            "--name",
            "inline-installed",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Installed to:" in result.stdout
    assert (skills_home / "inline-installed" / "SKILL.md").exists()


def test_update_command_folds_in_new_source(tmp_path: Path) -> None:
    output_dir = tmp_path / "compiled"
    source = ROOT / "examples" / "demo-book.md"
    supplement = tmp_path / "supplement.md"
    supplement.write_text(
        """# Supplement

## New Chapter

When a project needs fold-in support, prefer rebuilding from the full source set instead of patching individual files.
""",
        encoding="utf-8",
    )
    subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "run", str(source), "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bookskill_studio",
            "update",
            str(output_dir),
            str(supplement),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Folding in new source" in result.stdout
    manifest = json.loads((output_dir / "bookskill-manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["sources"]) == 2
    report = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["chapter_count"] >= 4


def test_open_report_command_returns_zero(tmp_path: Path) -> None:
    output_dir = tmp_path / "compiled"
    source = ROOT / "examples" / "demo-book.md"
    subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "run", str(source), "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "open-report", str(output_dir)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Opened report:" in result.stdout


def test_open_report_command_accepts_relative_path(tmp_path: Path) -> None:
    output_dir = tmp_path / "compiled"
    source = ROOT / "examples" / "demo-book.md"
    subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "run", str(source), "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "bookskill_studio", "open-report", "compiled"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Opened report:" in result.stdout


def test_chinese_pipeline(tmp_path: Path) -> None:
    source = tmp_path / "chinese-book.md"
    source.write_text(
        """# 示例书籍

作者：测试作者

## 第一章 为什么需要编译步骤

当团队需要长期复用一本书时，应该先把章节结构整理成可安装的 Skill 包。
优先使用结构化输出，便于后续校验与安装。

## 第二章 设计可复用结构

使用证据映射表，可以让每个概念都指回原文出处。
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "zh-output"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bookskill_studio",
            "run",
            str(source),
            "--output",
            str(output_dir),
            "--lang",
            "zh",
        ],
        cwd=ROOT,
        check=True,
    )
    skill_text = (output_dir / "SKILL.md").read_text(encoding="utf-8")
    manifest = json.loads((output_dir / "bookskill-manifest.json").read_text(encoding="utf-8"))
    report = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
    assert "如何使用本 Skill" in skill_text
    assert manifest["lang"] == "zh"
    assert report["ok"] is True


def test_chinese_validation_report(tmp_path: Path) -> None:
    source = tmp_path / "chinese-book.md"
    source.write_text(
        """# 示例书籍

## 第一章

当团队需要长期复用一本书时，应该先把章节结构整理成可安装的 Skill 包。
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "zh-output"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bookskill_studio",
            "run",
            str(source),
            "--output",
            str(output_dir),
            "--lang",
            "zh",
        ],
        cwd=ROOT,
        check=True,
    )
    html = (output_dir / "validation-report.html").read_text(encoding="utf-8")
    assert "校验报告" in html
    assert "必需文件" in html
    assert "通过" in html


def build_epub_fixture(epub_path: Path) -> None:
    with zipfile.ZipFile(epub_path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
""",
        )
        archive.writestr(
            "OEBPS/content.xhtml",
            """<html xmlns="http://www.w3.org/1999/xhtml"><body>
<h1>EPUB Demo Book</h1>
<h2>Chapter 1</h2>
<p>When trust matters, teams should preserve evidence for every generated concept.</p>
<h2>Chapter 2</h2>
<p>Use structured output when you need a validator-friendly package.</p>
</body></html>""",
        )
