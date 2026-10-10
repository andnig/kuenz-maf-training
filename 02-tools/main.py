"""Einstiegspunkt des offiziellen Basic-Responses-Samples, mit unseren Instructions.

Lokal vom Repository-Hauptordner: python 02-tools/main.py
Die direkte Übung mit Streaming bleibt in agent.py.
"""
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def erstelle_agent():
    load_dotenv()
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )
    return Agent(client=client, name="HelloAgent",
                 instructions="Du bist ein hilfreicher Assistent. Antworte kurz und auf Deutsch.",
                 default_options={"store": False})


if __name__ == "__main__":
    ResponsesHostServer(erstelle_agent).run()
