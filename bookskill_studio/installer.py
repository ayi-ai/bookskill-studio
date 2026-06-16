from __future__ import annotations

import shutil
from pathlib import Path


SKILL_HOME_CANDIDATES = {
    "codex": Path.home() / ".codex" / "skills",
    "claude": Path.home() / ".claude" / "skills",
    "cursor": Path.home() / ".cursor" / "skills",
    "agents": Path.home() / ".agents" / "skills",
}


def detect_skill_homes() -> dict[str, str]:
    return {name: str(path) for name, path in SKILL_HOME_CANDIDATES.items() if path.exists()}


def choose_default_skill_home() -> Path:
    existing = [path for path in SKILL_HOME_CANDIDATES.values() if path.exists()]
    if existing:
        return existing[0]
    return SKILL_HOME_CANDIDATES["codex"]


def install_skill(
    compiled_skill_dir: Path,
    explicit_home: Path | None = None,
    target: str | None = None,
    installed_name: str | None = None,
) -> Path:
    if not compiled_skill_dir.exists():
        raise ValueError(f"Compiled skill directory does not exist: {compiled_skill_dir}")
    if target and target not in SKILL_HOME_CANDIDATES:
        supported = ", ".join(sorted(SKILL_HOME_CANDIDATES))
        raise ValueError(f"Unknown target '{target}'. Supported targets: {supported}")

    skill_home = explicit_home
    if skill_home is None and target:
        skill_home = SKILL_HOME_CANDIDATES[target]
    if skill_home is None:
        skill_home = choose_default_skill_home()

    skill_home.mkdir(parents=True, exist_ok=True)
    destination_name = installed_name or compiled_skill_dir.name
    destination = skill_home / destination_name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(compiled_skill_dir, destination)
    return destination

