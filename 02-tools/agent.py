"""Ausgangspunkt für Schritt 2: das fertige Hello World aus 01 (mit Streaming).

Der Agent schickt eine Frage an das Modell in Microsoft Foundry und gibt die
Antwort aus. Mehr nicht. Tools, Gedächtnis und Workflows kommen später dazu.

Starten im Projekt-Hauptordner (Terminal → New Terminal):
    uv run python 02-tools/agent.py
    uv run python 02-tools/agent.py "Deine eigene Frage"

"""

import asyncio
import os
import sys

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv


async def main() -> None:
    # 1 · Konfiguration: Projektadresse und Deploymentname aus .env
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model = os.getenv("FOUNDRY_MODEL")
    if not endpoint or not model:
        raise SystemExit(".env fehlt oder ist leer. Führe aus: cp .env.example .env")

    # 2 · Anmeldung über die Azure CLI (az login), kein API-Schlüssel
    credential = AzureCliCredential()

    # 3 · Modellclient: Verbindung zum Modell in Foundry
    client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)

    # 4 · Agent: Modellclient + Name + Instructions
    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="Du bist ein hilfreicher Assistent. Antworte kurz und auf Deutsch.",
    )

    question = " ".join(sys.argv[1:]) or "Was ist ein Agent? Antworte in zwei Sätzen."

    # 5 · Aufruf mit Streaming: jedes Stück der Antwort sofort ausgeben
    async for update in agent.run(question, stream=True):
        print(update.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
