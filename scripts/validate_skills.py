#!/usr/bin/env python3
"""Validate publication readiness for the PFC Codex skill repository."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

ABS_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]|/mnt/[A-Za-z0-9._-]+(?:/|$)")
EXCLUDED_DIRS = {".git", ".tmp", ".pytest_cache", "__pycache__", ".venv", "venv"}
SECRET_RE = re.compile(
    r"(?:ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,})"
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BINARY_RISK_SUFFIXES = {".exe", ".dll", ".sav", ".p2sav", ".p3sav", ".p2prj", ".p3prj"}
OVERSIZE_BYTES = 5_000_000


@dataclass
class Finding:
    level: str
    path: Path
    message: str
    line: int | None = None

    def format(self) -> str:
        rel = self.path.relative_to(ROOT) if self.path.is_absolute() else self.path
        loc = f":{self.line}" if self.line else ""
        return f"{self.level}: {rel}{loc} - {self.message}"


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    data: dict[str, str] = {}
    current_key: str | None = None
    for raw in text[4:end].splitlines():
        if raw.startswith((" ", "\t")) and current_key:
            data[current_key] = (data[current_key] + " " + raw.strip()).strip()
            continue
        if ":" not in raw:
            current_key = None
            continue
        key, value = raw.split(":", 1)
        current_key = key.strip()
        data[current_key] = value.strip().strip('"').strip(">|- ")
    return data


def local_link_target(source: Path, raw: str) -> Path | None:
    target = raw.split("#", 1)[0].strip()
    if not target or re.match(r"(?:https?://|mailto:)", target):
        return None
    return (source.parent / target).resolve()


def validate_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        findings.append(Finding("ERROR", skill_dir, "missing SKILL.md"))
        return findings

    text = read_text(skill_file)
    if text is None:
        findings.append(Finding("ERROR", skill_file, "SKILL.md must be UTF-8 text"))
        return findings

    fm = frontmatter(text)
    if fm is None:
        findings.append(Finding("ERROR", skill_file, "missing YAML frontmatter"))
    else:
        if not fm.get("name"):
            findings.append(Finding("ERROR", skill_file, "frontmatter missing name"))
        if not fm.get("description"):
            findings.append(Finding("ERROR", skill_file, "frontmatter missing description"))
        elif len(fm["description"]) < 40:
            findings.append(Finding("WARN", skill_file, "description is very short; add trigger/use-case detail"))

    body = text.split("---", 2)[-1] if text.startswith("---") else text
    checks = {
        "When to use": ("when to use", "use this skill", "when the user"),
        "Required inputs": ("required inputs", "inputs"),
        "Workflow": ("workflow", "checklist", "lifecycle"),
        "Output contract": ("output contract", "outputs", "deliver"),
        "Local contents": ("local contents", "contents"),
    }
    lower = body.lower()
    for label, needles in checks.items():
        if not any(n in lower for n in needles):
            findings.append(Finding("WARN", skill_file, f"missing or weak section: {label}"))

    return findings


def iter_repository_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        yield path


def validate_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    suffix = path.suffix.lower()
    size = path.stat().st_size
    if size > OVERSIZE_BYTES:
        findings.append(Finding("WARN", path, f"large file ({size} bytes); confirm it is source/reference, not output"))
    if suffix in BINARY_RISK_SUFFIXES:
        findings.append(Finding("ERROR", path, "publication-risk binary or generated PFC state; remove or document externally"))

    text = read_text(path)
    if text is None:
        return findings

    skip_absolute_path_scan = path.resolve() == Path(__file__).resolve()
    for i, line in enumerate(text.splitlines(), 1):
        if not skip_absolute_path_scan and ABS_PATH_RE.search(line):
            findings.append(Finding("ERROR", path, "private absolute path; replace with relative path or placeholder", i))
        if SECRET_RE.search(line):
            findings.append(Finding("ERROR", path, "possible leaked credential/token", i))

    if suffix in {".md", ".markdown"}:
        for match in LINK_RE.finditer(text):
            target = local_link_target(path, match.group(1))
            if target is not None and not target.exists():
                line = text[: match.start()].count("\n") + 1
                findings.append(Finding("ERROR", path, f"broken local Markdown link: {match.group(1)}", line))

    return findings


def generate_index() -> str:
    rows = []
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        text = read_text(skill_file) or ""
        fm = frontmatter(text) or {}
        desc = fm.get("description", "").replace("\n", " ").strip()
        files = sum(1 for p in skill_dir.rglob("*") if p.is_file())
        refs = len(list((skill_dir / "references").glob("*"))) if (skill_dir / "references").exists() else 0
        scripts = len(list((skill_dir / "scripts").rglob("*"))) if (skill_dir / "scripts").exists() else 0
        rows.append((skill_dir.name, fm.get("name", ""), files, refs, scripts, desc))

    lines = [
        "# Skill Index",
        "",
        "Generated by `scripts/validate_skills.py --write-index`.",
        "",
        "| Slug | Name | Files | References | Scripts | Description |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for slug, name, files, refs, scripts, desc in rows:
        desc = desc.replace("|", r"\|")
        lines.append(f"| `{slug}` | `{name}` | {files} | {refs} | {scripts} | {desc} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-index", action="store_true", help="rewrite references/skill-index.md")
    args = parser.parse_args()

    if args.write_index:
        index_path = ROOT / "references" / "skill-index.md"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(generate_index(), encoding="utf-8")
        print(f"wrote {index_path.relative_to(ROOT)}")

    findings: list[Finding] = []
    if not SKILLS_DIR.exists():
        print(f"ERROR: missing skills directory: {SKILLS_DIR}", file=sys.stderr)
        return 2

    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        findings.extend(validate_skill(skill_dir))
    for path in sorted(iter_repository_files(ROOT)):
        findings.extend(validate_file(path))

    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARN"]
    for finding in findings:
        print(finding.format())
    print(f"\nValidation summary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
