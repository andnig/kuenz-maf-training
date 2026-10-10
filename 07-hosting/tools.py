"""Tools für den Prüfagenten. Jedes Tool ist eine normale Python-Funktion mit @tool."""

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

from agent_framework import tool
from pydantic import Field

DATEN = Path(__file__).resolve().parent / "daten"


def lade_json(dateiname: str) -> dict:
    return json.loads((DATEN / dateiname).read_text(encoding="utf-8"))


@tool
def aktuelle_uhrzeit() -> str:
    """Gibt die aktuelle Uhrzeit zurück."""
    return datetime.now().strftime("%H:%M")


@tool
def lade_pruefauftrag(review_id: Annotated[str, Field(description="ID des Prüfauftrags, z. B. PR-001")]) -> dict:
    """Lädt einen Prüfauftrag: welche Anlage, welche Spezifikation in welcher Version, welcher Katalog."""
    for auftrag in lade_json("pruefauftraege.json")["pruefauftraege"]:
        if auftrag["review_id"] == review_id.strip().upper():
            return auftrag
    return {"fehler": f"Prüfauftrag {review_id} gibt es nicht."}


@tool
def lade_anforderungskatalog(
    asset_id: Annotated[str, Field(description="Anlage, z. B. A-100")],
    requirement_id: Annotated[str | None, Field(description="Optional eine einzelne Anforderung, z. B. R-03")] = None,
) -> dict:
    """Lädt die internen Anforderungen für eine Anlage, auf Wunsch nur eine einzelne Anforderung."""
    katalog = lade_json("anforderungskatalog.json")
    if asset_id.strip().upper() not in katalog["asset_ids"]:
        return {"fehler": f"Für die Anlage {asset_id} gibt es keinen Anforderungskatalog."}
    anforderungen = katalog["requirements"]
    if requirement_id:
        anforderungen = [a for a in anforderungen if a["requirement_id"] == requirement_id.strip().upper()]
        if not anforderungen:
            return {"fehler": f"Die Anforderung {requirement_id} gibt es nicht."}
    return {"catalog_id": katalog["catalog_id"], "version": katalog["version"], "requirements": anforderungen}


@tool
def lade_spezifikation(document_version: Annotated[str, Field(description="Version der Spezifikation SPEC-001: 1 oder 2")]) -> dict:
    """Lädt die Kundenspezifikation SPEC-001 in einer Version, Abschnitt für Abschnitt."""
    pfad = DATEN / f"spezifikation_v{document_version.strip()}.json"
    if not pfad.exists():
        return {"fehler": f"Die Spezifikation SPEC-001 in Version {document_version} gibt es nicht."}
    return json.loads(pfad.read_text(encoding="utf-8"))
