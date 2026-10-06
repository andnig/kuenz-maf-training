"""Versionierter Fachvertrag; technische äußere IDs werden erst vom Gateway vergeben."""
import json
import os
from dataclasses import asdict
from contextvars import ContextVar
from datetime import datetime, timezone
from uuid import UUID, uuid4

from training_tools import anforderungskatalog_laden, pruefauftrag_laden

CONTRACT_VERSION = "kuenz.review/1"
PLATFORM_BINDING = ContextVar("kuenz_platform_binding", default=None)


def result_record(result):
    return {
        "contract_version": CONTRACT_VERSION,
        **asdict(result.kontext),
        "run_id": str(uuid4()),
        "processing_status": "completed",
        "agent_name": os.getenv("FOUNDRY_AGENT_NAME", "local"),
        "agent_version": os.getenv("FOUNDRY_AGENT_VERSION", "local"),
        "code_version": os.getenv("APP_VERSION", "hosted-20261005"),
        "sandbox_id": os.getenv("FOUNDRY_AGENT_SESSION_ID"),
        "response_id": (PLATFORM_BINDING.get() or {}).get("response_id"),
        "conversation_id": (PLATFORM_BINDING.get() or {}).get("conversation_id"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "extraktion": result.extraktion_quelle,
        "befunde": result.befunde,
        "klaerungspunkte": [b for b in result.befunde if b["status"] != "erfüllt"],
        "human_approval_status": "not_requested",
        "dataverse_callback_status": "not_requested",
    }


def output_text(response):
    return "\n".join(c["text"] for i in response.get("output", [])
                     for c in i.get("content", []) if c.get("type") == "output_text")


def validate_record(record, expected_review_id):
    """Fachliche Identität und vollständige Liste validieren, niemals Modelltext reparieren."""
    if not expected_review_id or record.get("review_id") != expected_review_id.upper():
        raise ValueError("Falsche oder fehlende review_id-Bindung; keine Freigabe.")
    context = pruefauftrag_laden(expected_review_id)
    for field in ("asset_id", "document_id", "document_version", "catalog_id", "catalog_version"):
        if record.get(field) != context[field]:
            raise ValueError(f"Falsche {field}-Bindung; keine Freigabe.")
    try:
        run_id = UUID(record["run_id"])
        if run_id.version != 4 or str(run_id) != record['run_id']:
            raise ValueError('run_id muss kanonische UUID4 sein.')
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise ValueError("Gültige run_id fehlt.") from error
    for field in ('agent_name', 'agent_version', 'code_version'):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f'Gültige {field}-Bindung fehlt.')
    requirements = [r["requirement_id"] for r in anforderungskatalog_laden(context["asset_id"])["requirements"]]
    findings = record.get("befunde")
    if not isinstance(findings, list) or not all(isinstance(b, dict) for b in findings) or [b.get("requirement_id") for b in findings] != requirements:
        raise ValueError("Befunde fehlen, sind doppelt oder enthalten fremde Anforderungen.")
    if any(b.get("status") not in {"erfüllt", "abweichend", "unklar"} for b in findings):
        raise ValueError("Ungültiger Befundstatus.")
    if record.get("klaerungspunkte") != [b for b in findings if b["status"] != "erfüllt"]:
        raise ValueError("Klärungspunkte stimmen nicht mit den Befunden überein.")
    if record.get("human_approval_status") != "not_requested" or record.get("dataverse_callback_status") != "not_requested":
        raise ValueError("KI-Ergebnis darf keine Menschenentscheidung oder Rückrufbestätigung setzen.")


def bind_response(response, headers, expected_review_id=None, *, expected_agent=None):
    """Binde genau eine gespeicherte Response. Kein Modellaufruf, keine Textrekonstruktion."""
    if response.get("status") != "completed":
        raise ValueError("Response ist nicht technisch abgeschlossen.")
    text = output_text(response)
    record = json.loads(text)
    if not isinstance(record, dict):
        raise ValueError('Ergebnis ist kein Vertragsobjekt.')
    if record.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("Nicht unterstützter Ergebnisvertrag.")
    if record.get("processing_status") != "completed":
        raise ValueError(record.get("message", "Kein abgeschlossenes Prüfergebnis."))
    validate_record(record, expected_review_id)
    if expected_agent is not None and record['agent_name'] != expected_agent:
        raise ValueError('Falsche Agent-Bindung im Ergebnis.')
    if not response.get("id") or not record.get("run_id"):
        raise ValueError("Technische Response-ID oder fachliche run_id fehlt.")
    if record.get("response_id") and record["response_id"] != response["id"]:
        raise ValueError("Innere und äußere Response-ID stimmen nicht überein.")
    h = {k.lower(): v for k, v in headers.items()}
    if h.get('x-ms-agent-version') and h['x-ms-agent-version'] != record['agent_version']:
        raise ValueError('Innere und äußere Agentversion stimmen nicht überein.')
    return {"response_id": response["id"], "conversation_id": response.get("conversation"),
             "session_id": response.get("agent_session_id"), "sandbox_id": h.get("x-agent-session-id"),
            "agent_version": h.get("x-ms-agent-version") or record["agent_version"],
            "result": record}
