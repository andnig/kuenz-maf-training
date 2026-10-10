"""Ausgangspunkt für Ü9: direkter Agentaufruf aus dem offiziellen Basic-Responses-Projekt.

Vom Repository-Hauptordner mit aktivierter .venv starten:
    python 02-tools/agent.py
"""
import asyncio
import os
import sys

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv


async def main() -> None:
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    if not endpoint or not model:
        raise SystemExit(".env fehlt oder ist leer. Führe im Hauptordner aus: cp .env.example .env")

    async with AzureCliCredential() as credential:
        client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)
        agent = Agent(client=client, name="HelloAgent",
                      instructions="Du bist ein hilfreicher Assistent. Antworte kurz und auf Deutsch.")
        question = " ".join(sys.argv[1:]) or "Was ist ein Agent? Antworte in zwei Sätzen."
        async for update in agent.run(question, stream=True):
            print(update.text, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
