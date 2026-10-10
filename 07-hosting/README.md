# 07 · Der Prüfworkflow als Hosted Agent

Der Prüfworkflow läuft bisher lokal. Jetzt bekommt er eine Responses-Schnittstelle und wird
über **Foundry Toolkit → Code → Remote** bereitgestellt. Der Hosting-Einstieg ist ein kleines
`main.py` nach dem offiziellen MAF-Sample. Deployment und Playground übernimmt VS Code.

**Ausgangspunkt:** fertiger Workflow aus05, im Checkpoint07 vorbereitet.
Lokale Befehle zunächst im Repository-Hauptordner mit aktivierter `.venv`.

## Schritt 1 · Workflow als Agent

```text
Erweitere #file:07-hosting/workflow.py mit der Agent-Schnittstelle von MAF 1.21.0:
- Erster Schritt akzeptiert list[Message], extrahiert PR-xxx aus der letzten Nachricht.
- Unbekannter Auftrag liefert die bestehende Fehlermeldung als JSON.
- Ergebnis als JSON-Text, ergänzt um run_id (UUID).
- erstelle_agent() baut mit FoundryChatClient und DefaultAzureCredential einen
  FRISCHEN Workflow und gibt workflow.as_agent(name="Spezifikationspruefung") zurück.
- Konfiguration FOUNDRY_PROJECT_ENDPOINT und AZURE_AI_MODEL_DEPLOYMENT_NAME aus .env/Cloudumgebung.
- Lokale main() ruft "Prüfe <ID>" auf, druckt JSON und vergleicht bekannte Aufträge
  weiterhin mit Referenzbefunden. Fehler ohne review_id ebenfalls verständlich ausgeben.
Erhalte Extraktion, Regeln und Ergebnisstruktur.
```

```bash
python 07-hosting/workflow.py PR-001
python 07-hosting/workflow.py PR-999
```

Erwartet: PR-001 wie05 (sechs✓), zusätzlich run_id. PR-999 liefert JSON mit fehler.

## Schritt 2 · Hosting-Einstieg selbst ergänzen

```text
Erzeuge #file:07-hosting/main.py nach der offiziellen MAF-Hosting-Integration.
Importiere ResponsesHostServer aus agent_framework_foundry_hosting,
load_dotenv aus dotenv und erstelle_agent aus workflow.
Unter if __name__ == "__main__": load_dotenv();
ResponsesHostServer(erstelle_agent, history_source="agent").run().
Übergib die Funktion als Factory, rufe sie hier nicht vorab auf:
jede Anfrage braucht einen frischen Workflow. Die Workflow-Nachrichtenhistorie
verwaltet MAF; history_source="agent" erhält dessen Routing.
Kein Deployment-Skript; workflow.py bleibt direkt ausführbar.
Erkläre Request → ResponsesHostServer → Workflow → JSON.
```

```bash
python 07-hosting/main.py
```

Der Server hört auf Port 8088. Im Toolkit **Agent Inspector** mit dem lokalen Server verbinden
und „Prüfe PR-001“ sowie „Prüfe PR-999“ senden. Alternativ im zweiten Terminal:

```bash
curl -s http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input":"Prüfe PR-999","stream":false}'
```

Stoppe den lokalen Server mit Ctrl+C.

## Schritt 3 · Vollständigen Quellordner prüfen

Öffne **07-hosting als Workspace** in VS Code. Wähle die bestehende root `.venv` als Interpreter.
`azure.yaml` liegt direkt in07, `services.pruefung.project` ist `.`: nur07 wird gepackt.
`main.py`, Workflowmodule, `requirements.txt` und `daten/` müssen dort liegen.
Die synthetischen Daten sind bereits kopiert; `tools.py` lädt diese lokale daten-Mappe.
Bei eigenen Datenänderungen root und07 synchron halten.

Im Terminal in07:

```bash
python -m pip install -r requirements.txt
cp ../.env .env
```

Prüfe FOUNDRY_PROJECT_ENDPOINT und AZURE_AI_MODEL_DEPLOYMENT_NAME=training-chat.
Der Modellname ist in `azure.yaml` als Cloud-Umgebung deklariert.
FOUNDRY_PROJECT_ENDPOINT setzt der Foundry-Dienst in der Cloud automatisch;
für lokale Aufrufe steht er in deiner .env. Der Name ist als Deployment-Umgebungsvariable reserviert.
Private .env, virtuelle Umgebung und Caches werden über `.agentignore` ausgeschlossen.
Die Cloud verwendet die Identität des Agenten; deine lokale Anmeldung wird nicht hochgeladen.

## Schritt 4 · Deployment in VS Code

1. Foundry Toolkit → **Developer Tools → Build → Deploy to Microsoft Foundry**.
2. Bestehendes Trainingsprojekt auswählen. **Code → Remote → New agent**.
3. Eigener Name `kuenz-pruefung-trainingNN` (NN=deine Teilnehmernummer).
4. Review: Python 3.13, Startbefehl `python3 main.py`, Quelle07-hosting,0.5CPU,1GiB.
5. **Deploy**. Unter **My Resources → Agents → Hosted Agent → Details** den Laufstatus abwarten.
6. **Playground**: „Prüfe PR-001“, „Prüfe PR-201“, „Prüfe PR-999“ testen.
   Notiere Agentname, getestete Version, Endpunkt, response_id und run_id.

Eine neue Version wird mit **Existing agent** bereitgestellt. Die Versionsauswahl im Playground
ändert nur dessen Testaufrufe: **Automatic** und der spätere Dispatcher müssen ebenfalls den
vorgesehenen Stand liefern. Falls Automatic eine alte Version liefert, Endpoint-Routing
im Foundry-Portal auf die neue Version setzen und erneut prüfen.

## Schritt 5 · Gespeicherte Antwort mit dem SDK abrufen

Ein neuer Playground-Aufruf startet eine neue Prüfung. Ein GET mit der response_id liest
das gespeicherte Resultat ohne neue Prüfung. Aus dem Projekt-Client direkt abrufen;
Agentname muss zu dem Endpunkt passen, der die Response erzeugt hat:

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv(".env")
with AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                     credential=DefaultAzureCredential(), allow_preview=True) as project:
    with project.get_openai_client(agent_name="kuenz-pruefung-trainingNN") as client:
        response = client.responses.retrieve("response_id-aus-dem-Playground")
        print(response.id, response.status, response.output_text)
        print(response.model_dump().get("agent"))  # tatsächlicher Agentname und Version
```

Du kannst den kurzen Code im Python-Terminal ausführen; ein eigenes Hilfsskript ist nicht nötig.
Prüfe dieselbe response_id, dasselbe JSON und dieselbe run_id. Im gespeicherten GET nennt
`agent` den tatsächlichen Agentnamen und die Version; diese Version mit dem beabsichtigten
Deployment vergleichen. Technisch completed ist
noch keine menschliche Freigabe. Danach folgt die Agent-Evaluation im Toolkit/Foundry-Portal
und die Anbindung des Dispatchers.

## Code verstehen

1. Warum as_agent()? Wie wird aus "Prüfe PR-001" die Auftrags-ID?
2. Warum eine Factory pro Request statt eines gemeinsam genutzten Workflows?
3. Welche IDs liefert der Workflow, welche der Responses-Dienst?
4. Was wird gepackt, was bleibt privat, welche Identität läuft in der Cloud?

[Toolkit-Anleitung](https://code.visualstudio.com/docs/intelligentapps/hosted-agents) ·
[Hosting vorhandenen Codes](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-deploy-own-code?tabs=python-responses)
