"""Schritt 2: Der Agent bekommt Tools und antwortet aus unseren Daten.

Starten im Projekt-Hauptordner:
    python 03-session-middleware/agent.py "Was gilt für R-03 bei A-100?"
"""

import asyncio
import os
import sys

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

from tools import aktuelle_uhrzeit, lade_anforderungskatalog, lade_pruefauftrag, lade_spezifikation


async def main() -> None:
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    if not endpoint or not model:
        raise SystemExit(".env fehlt oder ist leer. Führe aus: cp .env.example .env")

    credential = AzureCliCredential()
    client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)

    agent = Agent(
        client=client,
        name="PruefAgent",
        instructions=(
            "Du hilfst bei der Prüfung von Kundenspezifikationen. "
            "Beantworte Fragen zu Prüfaufträgen, Anforderungen und Spezifikationen nur mit den Tools. "
            "Liefert ein Tool einen Fehler, sag das und erfinde nichts. Antworte kurz und auf Deutsch."
        ),
        tools=[aktuelle_uhrzeit, lade_pruefauftrag, lade_anforderungskatalog, lade_spezifikation],
    )

    question = " ".join(sys.argv[1:]) or "Was gilt für R-03 bei A-100?"
    async for update in agent.run(question, stream=True):
        print(update.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
