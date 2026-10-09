#!/usr/bin/env python3
"""Copy shared content into every skill so each skill stays self-contained.

- shared/change-gate-core.md -> <skill>/references/change-gate.md (above MARKER;
  the platform notes below MARKER are kept as-is)
- shared/incident-comms.md     -> <skill>/references/incident-comms.md (whole file)
- shared/upgrade-checklist.md -> <skill>/references/upgrade-checklist.md (whole file)

Run from the repo root: python3 scripts/sync_shared.py [--check]
--check exits 1 if any copy is out of date (used by CI).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKER = "<!-- PLATFORM NOTES BELOW: edit freely. Everything above is synced from shared/change-gate-core.md -->"


def expected_gate(core: str, current: str) -> str:
    notes = current.split(MARKER, 1)[1] if MARKER in current else "\n\n## Platform notes\n\n(none yet)\n"
    return core.rstrip("\n") + "\n\n" + MARKER + notes


def main() -> int:
    check = "--check" in sys.argv
    core = (ROOT / "shared/change-gate-core.md").read_text()
    whole_files = {name: (ROOT / "shared" / name).read_text() for name in ("incident-comms.md", "upgrade-checklist.md")}
    stale = []
    for skill in sorted(ROOT.glob("managing-*")):
        refs = skill / "references"
        gate = refs / "change-gate.md"
        targets = {
            gate: expected_gate(core, gate.read_text() if gate.exists() else ""),
        }
        targets.update({refs / name: text for name, text in whole_files.items()})
        for path, want in targets.items():
            have = path.read_text() if path.exists() else None
            if have != want:
                stale.append(str(path.relative_to(ROOT)))
                if not check:
                    path.write_text(want)
    if stale:
        print(("Out of date: " if check else "Updated: ") + ", ".join(stale))
        return 1 if check else 0
    print("All shared copies in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
