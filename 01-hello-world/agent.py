"""Hello World: dein erster Agent mit dem Microsoft Agent Framework (MAF).

Der Agent schickt eine Frage an das Modell in Microsoft Foundry und gibt die
Antwort aus. Mehr nicht. Tools, Gedächtnis und Workflows kommen später dazu.

Starten im Projekt-Hauptordner (Terminal → New Terminal):
    uv run python 01-hello-world/agent.py
    uv run python 01-hello-world/agent.py "Deine eigene Frage"

Arbeite die TODOs der Reihe nach ab. Jedes TODO sagt dir, was du tust und warum.
"""

import asyncio
import os
import sys

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv


async def main() -> None:
    # TODO 1 · Konfiguration aus .env
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
        raise SystemExit("TODO 1: .env fehlt oder ist leer. Führe aus: cp .env.example .env")

    # TODO 2 · Anmeldung
    # Statt eines API-Schlüssels verwendet der Code deine Azure-Anmeldung.
    #   1. Im Terminal anmelden (einmal je Codespace):
    #        az login --use-device-code --tenant 42abcb50-0ca4-44ec-b66c-80926c94af9d
    #      Den angezeigten Code im Browser eingeben und dein Trainingskonto wählen.
    #   2. Ersetze unten None durch AzureCliCredential().
    #      Damit holt sich Python die Anmeldung aus der Azure CLI.
    credential = None

    # Der Modellclient verbindet deinen Code mit dem Modell in Foundry:
    # Projektadresse + Deploymentname + Anmeldung. Hier ist nichts zu tun.
    client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)

    # TODO 3 · Der Agent: Name und Instructions
    # Der Agent verbindet den Modellclient mit Instructions, also den festen
    # Anweisungen, die bei jeder Frage mitgeschickt werden.
    #   - name: ein kurzer Name ohne Leerzeichen, z. B. "HelloAgent".
    #   - instructions: Rolle und Antwortstil, z. B.
    #     "Du bist ein hilfreicher Assistent. Antworte kurz und auf Deutsch."
    agent = Agent(
        client=client,
        name="TODO",
        instructions="TODO",
    )

    question = " ".join(sys.argv[1:]) or "Was ist ein Agent? Antworte in zwei Sätzen."

    # TODO 4 · Ausführen und Instructions ausprobieren
    # agent.run() schickt Instructions und Frage an das Modell und wartet,
    # bis die ganze Antwort da ist. Erst dann wird sie ausgegeben.
    #   1. Starten: uv run python 01-hello-world/agent.py
    #   2. Instructions ändern (z. B. "Antworte immer in genau einem Satz."),
    #      speichern, erneut starten und die Antworten vergleichen.
    response = await agent.run(question)
    print(response.text)

    # TODO 5 · Streaming mit KI-Unterstützung
    # Ohne Streaming erscheint die Antwort erst, wenn sie fertig ist. Mit Streaming
    # erscheint sie Stück für Stück, so wie in einem Chat.
    #   1. Öffne Copilot Chat (Sprechblasen-Symbol oben) und schreibe:
    #        "Ändere in 01-hello-world/agent.py den Aufruf von agent.run auf
    #         Streaming. Verwende Microsoft Agent Framework 1.19:
    #         agent.run(question, stream=True) und gib jedes Update sofort aus."
    #   2. Lies den Vorschlag, bevor du ihn übernimmst: Was ändert sich?
    #   3. Starte erneut und beobachte, wie die Antwort erscheint.


if __name__ == "__main__":
    asyncio.run(main())
