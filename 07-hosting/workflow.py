"""Schritt 5: Die Prüfung als Workflow aus vier festen Schritten (Ausgangspunkt für 07-hosting).

Starten im Projekt-Hauptordner:
    uv run python 07-hosting/workflow.py PR-001
    uv run python 07-hosting/workflow.py PR-201
"""

import asyncio
import json
import os
import sys
from typing import Never

from agent_framework import Agent, Executor, WorkflowBuilder, WorkflowContext, handler
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

from extraktion import ANWEISUNG, extrahiere
from regeln import bewerte
from tools import lade_anforderungskatalog, lade_json, lade_pruefauftrag, lade_spezifikation


class AuftragLaden(Executor):
    @handler
    async def laden(self, review_id: str, ctx: WorkflowContext[dict]) -> None:
        await ctx.send_message({"auftrag": lade_pruefauftrag(review_id)})


class AngabenExtrahieren(Executor):
    def __init__(self, agent: Agent):
        super().__init__(id="angaben_extrahieren")
        self.agent = agent

    @handler
    async def extrahieren(self, daten: dict, ctx: WorkflowContext[dict]) -> None:
        extraktion = await extrahiere(self.agent, daten["auftrag"]["document_version"])
        await ctx.send_message({**daten, "angaben": extraktion.model_dump()["angaben"]})


class Vergleichen(Executor):
    @handler
    async def vergleichen(self, daten: dict, ctx: WorkflowContext[dict]) -> None:
        auftrag = daten["auftrag"]
        katalog = lade_anforderungskatalog(auftrag["asset_id"])
        spezifikation = lade_spezifikation(auftrag["document_version"])
        angaben = {a["requirement_id"]: a for a in daten["angaben"]}
        leer = {"fundstellen": [], "bewertung_vorschlag": None}
        befunde = [bewerte(a, angaben.get(a["requirement_id"], leer), spezifikation) for a in katalog["requirements"]]
        await ctx.send_message({**daten, "befunde": befunde})


class ErgebnisAusgeben(Executor):
    @handler
    async def ausgeben(self, daten: dict, ctx: WorkflowContext[Never, dict]) -> None:
        auftrag = daten["auftrag"]
        await ctx.yield_output({
            "review_id": auftrag["review_id"],
            "asset_id": auftrag["asset_id"],
            "document_id": auftrag["document_id"],
            "document_version": auftrag["document_version"],
            "befunde": daten["befunde"],
            "klaerungspunkte": [b for b in daten["befunde"] if b["status"] != "erfüllt"],
        })


def baue_workflow(agent: Agent):
    schritte = [AuftragLaden(id="auftrag_laden"), AngabenExtrahieren(agent),
                Vergleichen(id="vergleichen"), ErgebnisAusgeben(id="ergebnis_ausgeben")]
    return WorkflowBuilder(name="spezifikationspruefung", start_executor=schritte[0]).add_chain(schritte).build()


def mit_referenz_vergleichen(ergebnis: dict) -> None:
    for pruefung in lade_json("referenzbefunde.json")["pruefungen"]:
        if ergebnis["review_id"] in pruefung["review_ids"]:
            soll = {b["requirement_id"]: b["status"] for b in pruefung["befunde"]}
            for befund in ergebnis["befunde"]:
                zeichen = "✓" if befund["status"] == soll[befund["requirement_id"]] else "✗"
                print(f"{zeichen} {befund['requirement_id']}: {befund['status']} (Referenz: {soll[befund['requirement_id']]})")


async def main() -> None:
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model = os.getenv("FOUNDRY_MODEL")
    if not endpoint or not model:
        raise SystemExit(".env fehlt oder ist leer. Führe aus: cp .env.example .env")

    credential = AzureCliCredential()
    client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)
    agent = Agent(client=client, name="Extraktion", instructions=ANWEISUNG)

    review_id = sys.argv[1] if len(sys.argv) > 1 else "PR-001"
    result = await baue_workflow(agent).run(review_id)
    ergebnis = result.get_outputs()[0]
    print(json.dumps(ergebnis, ensure_ascii=False, indent=2))
    mit_referenz_vergleichen(ergebnis)


if __name__ == "__main__":
    asyncio.run(main())
