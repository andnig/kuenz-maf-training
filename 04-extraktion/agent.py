"""Schritt 3: Gespräch mit Gedächtnis (Session) und sichtbaren Toolaufrufen (Middleware).

Starten im Projekt-Hauptordner:
    uv run python 04-extraktion/agent.py
Beenden mit einer leeren Eingabe.
"""

import asyncio
import os
import time

from agent_framework import Agent, FunctionInvocationContext, function_middleware
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

from tools import aktuelle_uhrzeit, lade_anforderungskatalog, lade_pruefauftrag, lade_spezifikation


@function_middleware
async def zeige_toolaufruf(context: FunctionInvocationContext, call_next) -> None:
    start = time.perf_counter()
    await call_next()
    print(f"  [Tool {context.function.name}, {time.perf_counter() - start:.2f} s]")


async def main() -> None:
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model = os.getenv("FOUNDRY_MODEL")
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
        middleware=[zeige_toolaufruf],
    )

    session = agent.create_session()
    while True:
        frage = input("Du: ").strip()
        if not frage:
            break
        response = await agent.run(frage, session=session)
        print(f"Agent: {response.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
