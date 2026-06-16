from __future__ import annotations

import argparse
import json
import shutil
import webbrowser
from pathlib import Path

from bookskill_studio.compiler import compile_book, load_manifest, update_book, write_validation_reports
from bookskill_studio.doctor import run_doctor
from bookskill_studio.extractor import SUPPORTED_EXTENSIONS
from bookskill_studio.installer import install_skill
from bookskill_studio.validator import validate_skill_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile books into evidence-backed agent skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    lang_help = "Output language: en, zh, or auto (detect from source text)."

    demo = subparsers.add_parser("demo", help="Run the built-in demo book.")
    demo.add_argument("--output", default="demo-output", help="Output directory.")
    demo.add_argument("--lang", choices=["en", "zh", "auto"], default="auto", help=lang_help)
    add_install_arguments(demo)

    run = subparsers.add_parser("run", help="Compile a book into a skill.")
    run.add_argument("input", help="Input .md, .txt, .epub, or .pdf file.")
    run.add_argument("--output", required=True, help="Output directory.")
    run.add_argument("--skill-name", help="Optional skill slug override.")
    run.add_argument("--lang", choices=["en", "zh", "auto"], default="auto", help=lang_help)
    add_install_arguments(run)

    validate = subparsers.add_parser("validate", help="Validate a generated skill directory.")
    validate.add_argument("path", help="Path to the generated skill directory.")
    validate.add_argument("--lang", choices=["en", "zh", "auto"], default="auto", help=lang_help)

    install = subparsers.add_parser("install", help="Install a compiled skill into a local agent skill home.")
    install.add_argument("path", help="Path to the compiled skill directory.")
    install.add_argument("--target", choices=["codex", "claude", "cursor", "agents"], help="Install into a known skill home.")
    install.add_argument("--skills-home", help="Explicit skill home override.")
    install.add_argument("--name", help="Installed folder name override.")

    update = subparsers.add_parser("update", help="Fold a new source into an existing compiled skill directory.")
    update.add_argument("skill_dir", help="Existing compiled skill directory.")
    update.add_argument("input", help="New .md, .txt, .epub, or .pdf source.")
    update.add_argument("--skill-name", help="Optional skill slug override.")
    update.add_argument("--lang", choices=["en", "zh", "auto"], default="auto", help=lang_help)

    open_report = subparsers.add_parser("open-report", help="Open the generated HTML validation report in a browser.")
    open_report.add_argument("path", help="Path to the compiled skill directory.")

    subparsers.add_parser("doctor", help="Check local environment and supported extractors.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "demo":
        demo_source = Path(__file__).resolve().parent.parent / "examples" / "demo-book.md"
        return run_compile(
            demo_source,
            Path(args.output),
            None,
            lang=args.lang,
            install=args.install,
            target=args.target,
            skills_home=args.skills_home,
            install_name=args.name,
        )
    if args.command == "run":
        return run_compile(
            Path(args.input),
            Path(args.output),
            args.skill_name,
            lang=args.lang,
            install=args.install,
            target=args.target,
            skills_home=args.skills_home,
            install_name=args.name,
        )
    if args.command == "validate":
        return run_validate(Path(args.path), args.lang)
    if args.command == "install":
        destination = install_skill(
            compiled_skill_dir=Path(args.path),
            explicit_home=Path(args.skills_home) if args.skills_home else None,
            target=args.target,
            installed_name=args.name,
        )
        print(json.dumps({"ok": True, "installed_to": str(destination)}, indent=2, ensure_ascii=True))
        return 0
    if args.command == "update":
        return run_update(Path(args.skill_dir), Path(args.input), args.skill_name, lang=args.lang)
    if args.command == "open-report":
        return run_open_report(Path(args.path))
    if args.command == "doctor":
        report = run_doctor()
        print(json.dumps(report, indent=2, ensure_ascii=True))
        return 0 if report["ok"] else 1
    parser.error("Unsupported command")
    return 2


def add_install_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--install", action="store_true", help="Install the compiled skill after generation.")
    subparser.add_argument("--target", choices=["codex", "claude", "cursor", "agents"], help="Install target when using --install.")
    subparser.add_argument("--skills-home", help="Explicit install destination when using --install.")
    subparser.add_argument("--name", help="Installed folder name override when using --install.")


def run_compile(
    input_path: Path,
    output_dir: Path,
    skill_name: str | None,
    lang: str,
    install: bool,
    target: str | None,
    skills_home: str | None,
    install_name: str | None,
) -> int:
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise SystemExit(f"Unsupported input type. Supported extensions: {supported}")

    if output_dir.exists():
        shutil.rmtree(output_dir)

    print("[1/4] Reading source")
    print(f"       Source: {input_path}")
    print("[2/4] Compiling skill package")
    report = compile_book(input_path, output_dir, skill_name, lang=lang)
    print("[3/4] Writing validation report")
    print(f"[4/4] Finished with score {report['score']}")
    print(f"       Output: {output_dir}")
    if install:
        destination = install_skill(
            compiled_skill_dir=output_dir,
            explicit_home=Path(skills_home) if skills_home else None,
            target=target,
            installed_name=install_name,
        )
        print(f"       Installed to: {destination}")
    return 0 if report["ok"] else 1


def run_update(skill_dir: Path, input_path: Path, skill_name: str | None, lang: str = "auto") -> int:
    if not skill_dir.exists():
        raise SystemExit(f"Skill directory not found: {skill_dir}")
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise SystemExit(f"Unsupported input type. Supported extensions: {supported}")

    print("[1/4] Reading existing skill")
    print(f"       Skill: {skill_dir}")
    print("[2/4] Folding in new source")
    report = update_book(skill_dir, input_path, skill_name, lang=lang)
    print("[3/4] Re-validating updated skill")
    print(f"[4/4] Finished with score {report['score']}")
    print(f"       Output: {skill_dir}")
    print(f"       Report: {skill_dir / 'validation-report.html'}")
    return 0 if report["ok"] else 1


def run_validate(skill_dir: Path, lang: str) -> int:
    report = validate_skill_dir(skill_dir)
    manifest_path = skill_dir / "bookskill-manifest.json"
    if manifest_path.exists():
        manifest = load_manifest(skill_dir)
        source_path = Path(manifest.get("source_path") or skill_dir)
        skill_slug = manifest.get("name") or skill_dir.name
        resolved_lang = lang if lang != "auto" else manifest.get("lang", "en")
    else:
        source_path = skill_dir
        skill_slug = skill_dir.name
        resolved_lang = "en" if lang == "auto" else lang
    write_validation_reports(
        skill_dir,
        report,
        source_path=source_path,
        skill_slug=skill_slug,
        lang=resolved_lang,
    )
    print(json.dumps(report, indent=2, ensure_ascii=(resolved_lang != "zh")))
    return 0 if report["ok"] else 1


def run_open_report(skill_dir: Path) -> int:
    report_path = (skill_dir.resolve() / "validation-report.html").resolve()
    if not report_path.exists():
        raise SystemExit(f"Validation report not found: {report_path}")
    opened = webbrowser.open(report_path.as_uri())
    print(f"Opened report: {report_path}")
    return 0 if opened else 0
