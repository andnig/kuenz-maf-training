"""Lokales Diff ohne Git-Remote oder Repository; Starter-Baseline bleibt unveränderlich."""
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    baseline = json.loads((ROOT / "baseline.json").read_text())
    changed = 0
    for path, before in baseline.items():
        current = ROOT / path
        after = current.read_text() if current.exists() else ""
        if before != after:
            changed += 1
            print("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                              fromfile="starter/" + path, tofile="dein-code/" + path)))
    print(f"Geänderte Übungsdateien: {changed}")


if __name__ == "__main__":
    main()
