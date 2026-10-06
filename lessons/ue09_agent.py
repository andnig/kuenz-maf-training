from agent_framework import Agent
from training_tools import lade_anforderungskatalog, lade_spezifikation
from lessons.runtime import run


def build_agent(client, middleware=None):
    # TODO Ü9: eigener Agent, präzise Instructions, beide Tools, optionale Middleware.
    # Kein eigener Vergleich im Prompt; unbekannte IDs vom Tool zurückweisen lassen.
    raise NotImplementedError("Ü9: Agent zusammensetzen")


async def main(client, prompt):
    response = await build_agent(client).run(prompt or "Lade R-03 für A-100 und die Spezifikation Version 1.")
    print(response.text)


if __name__ == "__main__":
    run(main)
