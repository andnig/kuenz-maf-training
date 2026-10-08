"""Schritt 4: Das Modell liest die Spezifikation und liefert Angaben in einem festen Schema.

Starten im Projekt-Hauptordner:
    uv run python 04-extraktion/extraktion.py 1
    uv run python 04-extraktion/extraktion.py 2
"""

import asyncio
import os
import sys
from typing import Literal

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from tools import lade_anforderungskatalog, lade_spezifikation


class Fundstelle(BaseModel):
    abschnitt: str = Field(description="Abschnittsnummer ohne §, z. B. 3.2 oder A.1")
    zitat: str = Field(description="Wörtlicher Ausschnitt aus genau diesem Abschnitt, 3 bis 12 Wörter")
    werte: list[str] = Field(description="Werte aus dem Zitat im Format, das die Anweisung je Anforderung vorgibt")


class Angabe(BaseModel):
    requirement_id: str = Field(description="R-01 bis R-06")
    fundstellen: list[Fundstelle] = Field(description="Leer, wenn die Spezifikation dazu nichts sagt")
    bewertung_vorschlag: Literal["erfüllt", "abweichend", "unklar"] | None = Field(description="Nur für R-06, sonst null")
    begruendung: str = Field(description="Ein Satz: was steht wo, oder warum nichts gefunden wurde")


class Extraktion(BaseModel):
    angaben: list[Angabe]


ANWEISUNG = """Du liest eine Kundenspezifikation und suchst Angaben zu den Anforderungen R-01 bis R-06.
Du entscheidest NICHT, ob eine Anforderung erfüllt ist; das macht danach der Code. Ausnahme: R-06.

- Verwende nur den gelieferten Text, kein Vorwissen. Lies das ganze Dokument bis zum Ende, auch den Anhang (Abschnitte A.x).
- Liefere für jede Anforderung R-01 bis R-06 genau einen Eintrag.
- Eine Fundstelle besteht aus Abschnittsnummer und einem wörtlichen Zitat, genau wie im Text.
- Nimm nur Angaben, die genau den Gegenstand der Anforderung betreffen.
- Nennt das Dokument an mehreren Stellen unterschiedliche Werte, liefere ALLE diese Fundstellen.
- Findest du nichts, bleibt fundstellen leer. Erfinde nichts.
- Format der werte: R-01 Sprachcodes wie ["DE", "EN"] · R-02 Zahl in t wie ["41"] · R-03 Versionsnummer wie ["1.4"]
  · R-04 Zahl in ms wie ["30"] · R-05 Minimum und Maximum in °C wie ["-20", "40"] · R-06 [] und dazu bewertung_vorschlag.
"""


def baue_prompt(document_version: str) -> str:
    katalog = lade_anforderungskatalog("A-100")
    spezifikation = lade_spezifikation(document_version)
    anforderungen = "\n".join(f"{a['requirement_id']} {a['thema']}: {a['soll']}" for a in katalog["requirements"])
    text = "\n".join(f"§{a['abschnitt']} {a['titel']}: {a['text']}" for a in spezifikation["abschnitte"])
    return f"Anforderungen:\n{anforderungen}\n\nSpezifikation SPEC-001 Version {document_version}:\n{text}"


async def extrahiere(agent: Agent, document_version: str) -> Extraktion:
    response = await agent.run(baue_prompt(document_version), options={"response_format": Extraktion, "reasoning": {"effort": "medium"}})
    return response.value


def zitat_im_text(fundstelle: Fundstelle, spezifikation: dict) -> bool:
    for abschnitt in spezifikation["abschnitte"]:
        if abschnitt["abschnitt"] == fundstelle.abschnitt.strip("§ "):
            return fundstelle.zitat in abschnitt["text"]
    return False


async def main() -> None:
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model = os.getenv("FOUNDRY_MODEL")
    if not endpoint or not model:
        raise SystemExit(".env fehlt oder ist leer. Führe aus: cp .env.example .env")

    credential = AzureCliCredential()
    client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)
    agent = Agent(client=client, name="Extraktion", instructions=ANWEISUNG)

    version = sys.argv[1] if len(sys.argv) > 1 else "1"
    extraktion = await extrahiere(agent, version)
    spezifikation = lade_spezifikation(version)
    for angabe in extraktion.angaben:
        print(f"{angabe.requirement_id}: {angabe.begruendung}")
        for f in angabe.fundstellen:
            pruefung = "im Text" if zitat_im_text(f, spezifikation) else "NICHT im Text"
            print(f"   §{f.abschnitt} „{f.zitat}“ → {f.werte} ({pruefung})")


if __name__ == "__main__":
    asyncio.run(main())
