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
    # 1 · Konfiguration aus .env
    # Der Code braucht zwei Werte: die Adresse deines Foundry-Projekts und den
    # Namen des Modell-Deployments. Sie stehen nicht im Code, sondern in .env.
    #   1. Im Terminal, im Projekt-Hauptordner:  cp .env.example .env
    #   2. .env öffnen: FOUNDRY_PROJECT_ENDPOINT und FOUNDRY_MODEL sind gesetzt.
    # .env bleibt privat; .gitignore verhindert, dass sie committet wird.
    # load_dotenv() liest .env und stellt die Werte über os.getenv() bereit.
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model = os.getenv("FOUNDRY_MODEL")
    if not endpoint or not model:
        raise SystemExit(".env fehlt oder ist leer. Führe aus: cp .env.example .env")

    # 2 · Anmeldung
    # Statt eines API-Schlüssels verwendet der Code deine Azure-Anmeldung.
    #   1. Im Terminal anmelden (einmal je Codespace):
    #        az login --use-device-code --tenant 42abcb50-0ca4-44ec-b66c-80926c94af9d
    #      Den angezeigten Code im Browser eingeben und dein Trainingskonto wählen.
    #   2. Ersetze unten None durch AzureCliCredential().
    #      Damit holt sich Python die Anmeldung aus der Azure CLI.
    credential = AzureCliCredential()

    # Der Modellclient verbindet deinen Code mit dem Modell in Foundry:
    # Projektadresse + Deploymentname + Anmeldung. Hier ist nichts zu tun.
    client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)

    # 3 · Der Agent: Name und Instructions
    # Der Agent verbindet den Modellclient mit Instructions, also den festen
    # Anweisungen, die bei jeder Frage mitgeschickt werden.
    #   - name: ein kurzer Name ohne Leerzeichen, z. B. "HelloAgent".
    #   - instructions: Rolle und Antwortstil, z. B.
    #     "Du bist ein hilfreicher Assistent. Antworte kurz und auf Deutsch."
    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="Du bist ein hilfreicher Assistent. Antworte kurz und auf Deutsch.",
    )

    question = " ".join(sys.argv[1:]) or "Was ist ein Agent? Antworte in zwei Sätzen."

    # Streaming: Mit stream=True liefert agent.run() die Antwort in
    # Teilen (Updates). Jedes Update wird sofort ausgegeben, ohne Zeilenumbruch;
    # print() am Ende schließt die Zeile ab.
    async for update in agent.run(question, stream=True):
        print(update.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
