"""Gezielte Source-Deploy-/Responses-Verwaltung; kein azd/globaler Configwechsel."""
import argparse
import base64
import hashlib
import io
import json
import os
import re
import stat
import sys
import time
import zipfile
import uuid
from pathlib import Path

import requests
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeConfiguration, HostedAgentDefinition, ProtocolVersionRecord, VersionRefIndicator
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

SOURCE = Path(__file__).resolve().parent
if not (SOURCE / "hosted_main.py").exists():
    SOURCE = Path(__file__).resolve().parents[2] / "exercises/hosted-starter"
if SOURCE.exists():
    sys.path.insert(0, str(SOURCE))
else:
    SOURCE = Path(__file__).resolve().parent
    sys.path.insert(0, str(SOURCE))
from review_contract import bind_response, output_text

TELEMETRY_RESOURCE = ('/subscriptions/ffa3d9a7-70c4-4406-a641-74c9d0f56d90/resourceGroups/'
                      'rg-kuenz-training-2026/providers/Microsoft.Insights/components/appi-kuenz-training-2026')
TELEMETRY_KEY = 'TRAINING_APPINSIGHTS_CONNECTION_STRING'


def write_telemetry_env(path, value):
    """Keep the authorized exporter setting private; preserve unrelated lines."""
    if path.name != '.env' or path.is_symlink():
        raise ValueError('Telemetrie nur in einer lokalen regulären .env speichern, nie .env.example.')
    if not value or '\n' in value or '\r' in value:
        raise ValueError('Ungültige Telemetrie-Konfiguration; Wert wird nicht ausgegeben.')
    before = path.read_bytes() if path.exists() else b''
    pattern = re.compile(rb'^\s*(?:export\s+)?TRAINING_APPINSIGHTS_CONNECTION_STRING\s*=')
    lines = [line for line in before.splitlines(keepends=True) if not pattern.match(line)]
    content = b''.join(lines)
    if content and not content.endswith(b'\n'):
        content += b'\n'
    content += (TELEMETRY_KEY+'='+json.dumps(value)+'\n').encode()
    temporary = path.with_name('.env.telemetry-'+uuid.uuid4().hex)
    try:
        with os.fdopen(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as stream:
            stream.write(content)
        if (path.read_bytes() if path.exists() else b'') != before:
            raise ValueError('Parallele .env-Änderung; nicht überschrieben.')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def configure_telemetry(credential, path):
    token = credential.get_token('https://management.azure.com/.default').token
    response = requests.get('https://management.azure.com'+TELEMETRY_RESOURCE+'?api-version=2020-02-02',
                            headers={'Authorization': 'Bearer '+token}, timeout=90, allow_redirects=False)
    response.raise_for_status()
    resource = response.json()
    if resource['id'].lower() != TELEMETRY_RESOURCE.lower():
        raise ValueError('Falsches Application-Insights-Ziel.')
    write_telemetry_env(path, resource['properties']['ConnectionString'])
    return {'telemetry_resource': TELEMETRY_RESOURCE, 'source': 'ARM components/read (Reader)',
            'env_file': str(path), 'value': '[MASKED]', 'private_file': True,
            'next': 'deploy; bei erneutem Deployment neue Version in Ü14/Ü16 binden'}


def caller_binding(token):
    """Nur Kennung des von AzureCliCredential bezogenen Tokens; nie Token/Claims speichern."""
    try:
        part = token.split('.')[1]
        claims = json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))
        identity = '\n'.join([claims['tid'], claims['oid']])
    except (IndexError, KeyError, TypeError, ValueError) as error:
        raise ValueError('Aufruferbindung fehlt im Entra-Token.') from error
    if not claims['tid'] or not claims['oid']:
        raise ValueError('Aufruferbindung ist leer.')
    return hashlib.sha256(identity.encode()).hexdigest()


def package(source):
    """Allowlist statt Ausschlussliste: nie .env, Login, Checkpoints, Nachweise oder Lösungen."""
    allow = ["hosted_main.py", "review_contract.py", "training_tools.py", "pruefung.py", "pruefworkflow.py",
             "requirements.txt", "pruefservice/__init__.py", "pruefservice/workflow.py"]
    files = [source / name for name in allow]
    for folder in ["training_data", "referenz"]:
        files += sorted((source / folder).glob("*.json"))
    files += sorted((source / "lessons").glob("*.py"))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            if file.is_symlink() or not file.resolve().is_relative_to(source.resolve()):
                raise ValueError(f"Symlink nicht erlaubt: {file.name}")
            entry = zipfile.ZipInfo(file.relative_to(source).as_posix(), (2026, 10, 5, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, file.read_bytes())
    return buffer.getvalue()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["telemetry", "deploy", "invoke", "status", "activity", "versions", "route", "delete", "download"])
    p.add_argument('--env-file', type=Path, default=Path('.env'))
    p.add_argument("--agent")
    p.add_argument("--endpoint")
    p.add_argument("--source", type=Path, default=SOURCE)
    p.add_argument("--input", default="Prüfe PR-001")
    p.add_argument("--review-id", default="PR-001")
    p.add_argument("--receipt", type=Path)
    p.add_argument("--version")
    p.add_argument("--output", type=Path)
    p.add_argument("--confirm-delete", action="store_true")
    a = p.parse_args()
    load_dotenv(a.env_file)
    a.agent = a.agent or os.getenv('HOSTED_AGENT_NAME')
    a.endpoint = a.endpoint or os.getenv('FOUNDRY_PROJECT_ENDPOINT')
    if not a.endpoint or not re.fullmatch(r'https://[a-z0-9][a-z0-9-]*\.services\.ai\.azure\.com/api/projects/[A-Za-z0-9_-]+/?', a.endpoint):
        p.error('FOUNDRY_PROJECT_ENDPOINT: Azure-Foundry-Projekt-URL ohne Userinfo, Port, Query oder weitere Pfade erforderlich.')
    if not a.agent or not re.fullmatch(r"kuenz-pruefung-(?:trainer|training0[1-5])", a.agent):
        p.error("--agent: kuenz-pruefung-trainer oder kuenz-pruefung-training01…05 erforderlich.")
    credential = AzureCliCredential()
    if a.command == 'telemetry':
        result = configure_telemetry(credential, a.env_file)
        if a.output:
            a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    token = credential.get_token("https://ai.azure.com/.default").token
    headers = {"Authorization": f"Bearer {token}"}
    base = f"{a.endpoint.rstrip('/')}/agents/{a.agent}"
    protocol = base + "/endpoint/protocols/openai"
    client = AIProjectClient(endpoint=a.endpoint, credential=credential)
    if a.command == "deploy":
        code = package(a.source)
        env = {"FOUNDRY_PROJECT_ENDPOINT": a.endpoint, "FOUNDRY_MODEL": "training-chat",
               "AZURE_AI_MODEL_DEPLOYMENT_NAME": "training-chat", "APP_VERSION": "hosted-20261005"}
        connection = os.getenv("TRAINING_APPINSIGHTS_CONNECTION_STRING")
        if not connection:
            raise ValueError('Telemetrie fehlt: zuerst uv run python hosted.py telemetry --agent '+a.agent)
        env["TRAINING_APPINSIGHTS_CONNECTION_STRING"] = connection
        stream = io.BytesIO(code)
        stream.name = "agent.zip"
        created = client.agents.create_version_from_code(agent_name=a.agent,
            definition=HostedAgentDefinition(cpu="0.5", memory="1Gi", environment_variables=env,
                code_configuration=CodeConfiguration(runtime="python_3_13", entry_point=["python", "hosted_main.py"],
                    dependency_resolution="remote_build"),
                protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")]),
            code=stream, code_zip_sha256=hashlib.sha256(code).hexdigest())
        version = created.version
        deadline = time.monotonic() + 900
        while time.monotonic() < deadline:
            state = client.agents.get_version(agent_name=a.agent, agent_version=version)
            print(json.dumps({"agent": a.agent, "version": version, "status": state["status"]}), flush=True)
            if state["status"] == "active":
                break
            if state["status"] == "failed":
                raise RuntimeError("Remote Build fehlgeschlagen (Version error prüfen; keine Secrets loggen).")
            time.sleep(5)
        else:
            raise TimeoutError("Deploy nach 15 Minuten nicht active.")
        result = {"agent": a.agent, "version": version, "sha256": hashlib.sha256(code).hexdigest(), "status": "active"}
    elif a.command == "activity":
        r = requests.patch(base + "?api-version=v1", headers={**headers, "Content-Type": "application/merge-patch+json"},
            json={"agent_endpoint": {"protocol_configuration": {"responses": {}, "activity": {}},
                                     "authorization_schemes": [{"type": "Entra"}]}}, timeout=60)
        r.raise_for_status()
        result = {"http_status": r.status_code, "protocols": ["responses", "activity"], "authorization": "Entra"}
    elif a.command == "invoke":
        payload = {"input": a.input, "store": True}
        if a.version:
            selected = client.agents.create_session(agent_name=a.agent, version_indicator=VersionRefIndicator(agent_version=a.version))
            payload["agent_session_id"] = selected["agent_session_id"]
        r = requests.post(protocol + "/responses?api-version=v1", headers=headers,
                          json=payload, timeout=240, allow_redirects=False)
        r.raise_for_status()
        response = r.json()
        result = {"http_status": r.status_code, "body": response,
                    "session_id": response.get("agent_session_id"), "sandbox_id": r.headers.get("x-agent-session-id"), "agent": a.agent,
                    "endpoint": a.endpoint.rstrip('/'), "caller_binding": caller_binding(token)}
        result["binding"] = bind_response(response, r.headers, a.review_id, expected_agent=a.agent)
        if a.version and response.get('agent_session_id') != payload['agent_session_id']:
            raise ValueError('Tatsächlich verwendete Session weicht von der Versionsbindung ab.')
        if a.version and result["binding"]["result"]["agent_version"] != a.version:
            raise ValueError("Tatsächlich ausgeführte Version weicht von --version ab.")
        if a.receipt:
            a.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    elif a.command == "status":
        if not a.receipt:
            p.error("--receipt aus erfolgreichem invoke erforderlich; Status startet keine Prüfung.")
        old = json.loads(a.receipt.read_text())
        if old["agent"] != a.agent:
            raise ValueError("Falscher Agent im Beleg.")
        if old.get('endpoint') != a.endpoint.rstrip('/') or old.get('caller_binding') != caller_binding(token):
            raise ValueError('Falscher Endpunkt oder falsche Aufruferidentität im Beleg.')
        bind_response(old["body"], {"x-agent-session-id": old.get("sandbox_id")}, a.review_id, expected_agent=a.agent)
        if not re.fullmatch(r'caresp_[A-Za-z0-9]+', old['body']['id']):
            raise ValueError('Ungültiges Response-ID-Format im Beleg.')
        r = requests.get(protocol + f"/responses/{old['body']['id']}?api-version=v1", headers=headers, timeout=90, allow_redirects=False)
        r.raise_for_status()
        new = r.json()
        if new["id"] != old["body"]["id"] or output_text(new) != output_text(old["body"]):
            raise ValueError("Gespeicherter Befund verändert!")
        result = {"http_status": r.status_code, "same_stored_result": True,
                    "binding": bind_response(new, {"x-agent-session-id": old.get("sandbox_id")}, a.review_id, expected_agent=a.agent)}
    elif a.command == "versions":
        result = [{"version": v.version, "status": v["status"]} for v in client.agents.list_versions(agent_name=a.agent)]
    elif a.command == "route":
        if not a.version or not re.fullmatch(r"[0-9]+", a.version):
            p.error("--version mit expliziter aktiver Rückfallversion erforderlich.")
        state = client.agents.get_version(agent_name=a.agent, agent_version=a.version)
        if state["status"] != "active":
            raise ValueError("Nur eine aktive Version ist ein zulässiges Routingziel.")
        selector = {"version_selection_rules": [{"type": "FixedRatio", "agent_version": a.version,
                                                 "traffic_percentage": 100}]}
        r = requests.patch(base + "?api-version=v1", headers={**headers, "Content-Type": "application/merge-patch+json"},
                           json={"agent_endpoint": {"version_selector": selector}}, timeout=60)
        r.raise_for_status()
        check = requests.get(base + "?api-version=v1", headers=headers, timeout=60)
        check.raise_for_status()
        if check.json()["agent_endpoint"]["version_selector"] != selector:
            raise ValueError("Routing-Kontrollabruf stimmt nicht überein.")
        result = {"agent": a.agent, "routed_version": a.version, "control_get": 200}
    elif a.command == "download":
        if not a.output:
            p.error("--output für ZIP erforderlich")
        a.output.write_bytes(b"".join(client.agents.download_code(agent_name=a.agent, agent_version=a.version)))
        result = {"sha256": hashlib.sha256(a.output.read_bytes()).hexdigest()}
    else:
        if not a.confirm_delete:
            p.error("--confirm-delete erforderlich (löscht nur diesen Agenten samt Sessions).")
        r = requests.delete(base + "?api-version=v1&force=true", headers=headers, timeout=90)
        r.raise_for_status()
        check = requests.get(base + "?api-version=v1", headers=headers, timeout=60)
        if check.status_code != 404:
            raise RuntimeError('Delete nicht bestätigt')
        result = {"deleted": a.agent, "control_get": 404}
    if a.output and a.command != "download":
        a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
