"""Eigene Übungsdateien sichern; Anmeldedaten und .env bleiben im Codespace."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
output = root / "mein-training.zip"
excluded = {".git", ".venv", ".env", ".azure", ".pytest_cache", "__pycache__", ".checkpoints"}
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in excluded for part in relative.parts) or path.is_symlink() or not path.is_file() or path == output:
            continue
        if path.suffix in {".key", ".pem", ".pfx", ".p12"}:
            continue
        archive.write(path, relative)
print("mein-training.zip erstellt. Explorer: Rechtsklick → Download.")
