"""Dieses Projekt als Foundry Hosted Agent bereitstellen und aufrufen.

    uv run python deploy.py deploy  <agentname> [--datei agent.py]
    uv run python deploy.py invoke  <agentname> "Deine Frage"
    uv run python deploy.py status  <agentname> <response_id>
    uv run python deploy.py delete  <agentname>

deploy lädt den Projektordner als ZIP hoch; Foundry installiert die Pakete und startet
hosted.py. Projektadresse und Modell kommen aus .env. Angemeldet wird mit az login.
"""

import argparse
import hashlib
import io
import json
import os
import stat
import time
import tomllib
import zipfile
from pathlib import Path

import requests
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeConfiguration, HostedAgentDefinition, ProtocolVersionRecord
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

PROJEKT = Path(__file__).resolve().parent
NICHT_HOCHLADEN = {".git", ".venv", ".env", "__pycache__", ".pytest_cache", ".devcontainer", "uv.lock", "pyproject.toml"}


def packe_projekt() -> bytes:
    """Alle Projektdateien außer .env und Umgebung, dazu requirements.txt aus pyproject.toml."""
    pakete = tomllib.loads((PROJEKT / "pyproject.toml").read_text())["project"]["dependencies"]
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as archiv:
        dateien = {"requirements.txt": "\n".join(pakete).encode() + b"\n"}
        for datei in sorted(PROJEKT.rglob("*")):
            teile = datei.relative_to(PROJEKT).parts
            if datei.is_file() and not set(teile) & NICHT_HOCHLADEN and datei.suffix != ".zip":
                dateien[datei.relative_to(PROJEKT).as_posix()] = datei.read_bytes()
        for name, inhalt in dateien.items():
            eintrag = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            eintrag.create_system = 3
            eintrag.external_attr = (stat.S_IFREG | 0o644) << 16
            archiv.writestr(eintrag, inhalt, zipfile.ZIP_DEFLATED)
    return puffer.getvalue()


def deploy(client, agent, datei, agent_url, kopf):
    code = packe_projekt()
    umgebung = {"FOUNDRY_PROJECT_ENDPOINT": os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                "FOUNDRY_MODEL": os.environ["FOUNDRY_MODEL"], "AGENT_DATEI": datei}
    try:
        umgebung["APPLICATIONINSIGHTS_CONNECTION_STRING"] = client.telemetry.get_application_insights_connection_string()
    except Exception:
        print("Kein Application Insights am Projekt; der Agent läuft ohne Tracing.")
    zip_datei = io.BytesIO(code)
    zip_datei.name = "agent.zip"
    version = client.agents.create_version_from_code(
        agent_name=agent,
        definition=HostedAgentDefinition(
            cpu="0.5", memory="1Gi", environment_variables=umgebung,
            code_configuration=CodeConfiguration(runtime="python_3_13", entry_point=["python", "hosted.py"],
                                                 dependency_resolution="remote_build"),
            protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")]),
        code=zip_datei, code_zip_sha256=hashlib.sha256(code).hexdigest()).version
    print(f"{agent} Version {version} wird gebaut …")
    while (status := client.agents.get_version(agent_name=agent, agent_version=version)["status"]) not in ("active", "failed"):
        time.sleep(10)
    print(f"{agent} Version {version}: {status}")
    if status == "active":
        # Der Endpunkt bedient sonst weiter die bisherige Version.
        regel = {"version_selection_rules": [{"type": "FixedRatio", "agent_version": version, "traffic_percentage": 100}]}
        antwort = requests.patch(f"{agent_url}?api-version=v1", headers={**kopf, "Content-Type": "application/merge-patch+json"},
                                 json={"agent_endpoint": {"version_selector": regel}}, timeout=60)
        antwort.raise_for_status()
        print(f"Aufrufe gehen jetzt an Version {version}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("befehl", choices=["deploy", "invoke", "status", "delete"])
    parser.add_argument("agent")
    parser.add_argument("text", nargs="?", help="Frage (invoke) oder response_id (status)")
    parser.add_argument("--datei", default="agent.py", help="Datei mit erstelle_agent(), relativ zum Projektordner")
    a = parser.parse_args()
    load_dotenv(PROJEKT / ".env")
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"].rstrip("/")
    credential = AzureCliCredential()
    client = AIProjectClient(endpoint=endpoint, credential=credential)
    token = credential.get_token("https://ai.azure.com/.default").token
    kopf = {"Authorization": f"Bearer {token}"}
    agent_url = f"{endpoint}/agents/{a.agent}"
    responses_url = f"{agent_url}/endpoint/protocols/openai/responses"

    if a.befehl == "deploy":
        deploy(client, a.agent, a.datei, agent_url, kopf)
    elif a.befehl == "invoke":
        antwort = requests.post(f"{responses_url}?api-version=v1", headers=kopf, json={"input": a.text}, timeout=300)
        antwort.raise_for_status()
        ergebnis = antwort.json()
        print(json.dumps({"response_id": ergebnis["id"], "status": ergebnis["status"],
                          "agent": ergebnis.get("agent_reference")}, ensure_ascii=False))
        print(ergebnis["output"][-1]["content"][0]["text"])
    elif a.befehl == "status":
        antwort = requests.get(f"{responses_url}/{a.text}?api-version=v1", headers=kopf, timeout=60)
        antwort.raise_for_status()
        ergebnis = antwort.json()
        print(json.dumps({"response_id": ergebnis["id"], "status": ergebnis["status"],
                          "agent": ergebnis.get("agent_reference")}, ensure_ascii=False))
        print(ergebnis["output"][-1]["content"][0]["text"])
    else:
        antwort = requests.delete(f"{agent_url}?api-version=v1&force=true", headers=kopf, timeout=90)
        antwort.raise_for_status()
        print(f"{a.agent} gelöscht.")


if __name__ == "__main__":
    main()
