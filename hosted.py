"""Startet einen MAF-Agenten als Foundry Hosted Agent.

Foundry führt diese Datei im Container aus (siehe deploy.py). Sie lädt die Funktion
erstelle_agent() aus der Datei in AGENT_DATEI (Standard: agent.py) und stellt den
Agenten über die Responses-API bereit. Ein Workflow wird mit workflow.as_agent() zum Agenten.

Lokal ausprobieren:
    uv run python hosted.py
    curl -s localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Hallo"}'
"""

import importlib.util
import os
import sys
from pathlib import Path

from agent_framework_foundry_hosting import ResponsesHostServer
from dotenv import load_dotenv


def lade_agent():
    datei = Path(__file__).resolve().parent / os.getenv("AGENT_DATEI", "agent.py")
    sys.path.insert(0, str(datei.parent))
    spec = importlib.util.spec_from_file_location(datei.stem, datei)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul.erstelle_agent()


if __name__ == "__main__":
    load_dotenv()
    ResponsesHostServer(lade_agent()).run()
