"""Vorabcheck ohne Azure-Anmeldung oder Modellkosten."""
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

assert sys.version_info[:2] == (3, 13), "Python 3.13 erforderlich"
for name, expected in {"agent-framework-core": "1.19.0", "agent-framework-foundry": "1.13.1"}.items():
    actual = importlib.metadata.version(name)
    assert actual == expected, f"{name}: {actual} statt {expected}"
import agent_framework
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
assert Path(".env").is_file(), ".env fehlt"
subprocess.run(["uv", "--version"], check=True)
subprocess.run(["az", "version", "--query", '\"azure-cli\"', "-o", "tsv"], check=True)
print(json.dumps({"umgebung": "OK", "python": sys.version.split()[0], "MAF": "1.19.0", "anmeldung": "erfolgt in Übung 8"}, ensure_ascii=False))
