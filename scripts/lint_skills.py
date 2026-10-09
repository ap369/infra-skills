#!/usr/bin/env python3
"""Lint every managing-*/ skill. Run from anywhere: python3 scripts/lint_skills.py

Errors (exit 1):
  - SKILL.md frontmatter missing name/description, name != directory, bad name format
  - description over 1024 chars or not starting with "Use when"
  - a file referenced in SKILL.md's References section doesn't exist,
    or a file in references/ isn't referenced (orphan)
  - shared copies out of sync (scripts/sync_shared.py --check)
  - skill missing from README (table row and symlink lines)
  - no tests/<skill>.md scenario file
  - SKILL.md over the hard word limit
Warnings: SKILL.md over the soft word limit.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SOFT_WORDS, HARD_WORDS = 500, 600
REQUIRED_REFS = {"change-gate.md", "best-practices.md", "incident-comms.md", "upgrade-checklist.md", "upgrades-and-migration.md"}


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def main():
    errors, warnings = [], []
    readme = (ROOT / "README.md").read_text()
    skills = sorted(p for p in ROOT.glob("managing-*") if p.is_dir())
    if not skills:
        errors.append("no managing-* skills found")
    for skill in skills:
        name = skill.name
        md = skill / "SKILL.md"
        if not md.exists():
            errors.append(f"{name}: SKILL.md missing")
            continue
        text = md.read_text()
        fm = frontmatter(text)
        if fm.get("name") != name:
            errors.append(f"{name}: frontmatter name {fm.get('name')!r} != directory")
        if not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{name}: name must match {NAME_RE.pattern} and be <= 64 chars")
        desc = fm.get("description", "")
        if not desc.startswith("Use when"):
            errors.append(f"{name}: description must start with 'Use when'")
        if len(desc) > 1024:
            errors.append(f"{name}: description is {len(desc)} chars (> 1024)")
        words = len(text.split())
        if words > HARD_WORDS:
            errors.append(f"{name}: SKILL.md is {words} words (> {HARD_WORDS})")
        elif words > SOFT_WORDS:
            warnings.append(f"{name}: SKILL.md is {words} words (> {SOFT_WORDS} target)")
        refs_section = text.split("## References", 1)[1] if "## References" in text else ""
        mentioned = set(re.findall(r"([a-z0-9-]+\.md)", refs_section))
        present = {p.name for p in (skill / "references").glob("*.md")}
        for missing in sorted(mentioned - present):
            errors.append(f"{name}: References lists {missing}, which doesn't exist")
        for orphan in sorted(present - mentioned):
            errors.append(f"{name}: references/{orphan} is not listed in SKILL.md References")
        for req in sorted(REQUIRED_REFS - present):
            errors.append(f"{name}: required reference {req} missing")
        if not (ROOT / "tests" / f"{name}.md").exists():
            errors.append(f"{name}: tests/{name}.md missing")
        if f"`{name}`" not in readme:
            errors.append(f"{name}: no README table row")
        for target in ("~/.claude/skills", "~/.config/opencode/skills"):
            if f"{target}/{name}" not in readme:
                errors.append(f"{name}: README missing symlink line for {target}")
    sync = subprocess.run([sys.executable, str(ROOT / "scripts/sync_shared.py"), "--check"], capture_output=True, text=True)
    if sync.returncode != 0:
        errors.append("shared copies out of sync: " + sync.stdout.strip() + " (run python3 scripts/sync_shared.py)")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(skills)} skills checked, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
