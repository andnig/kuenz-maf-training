# Künz Agententraining · Microsoft Agent Framework

Du erzeugst dein erstes Agentenprojekt mit dem offiziellen **Foundry Toolkit** in VS Code.
Danach erweiterst du es mit Tools, Gesprächsverlauf, Extraktion und einem Prüfworkflow.
Die vorbereiteten Ordner sind Checkpoints: `02-tools` beginnt mit dem fertigen Stand von01,
`03-session-middleware` mit dem fertigen Stand von02 und so weiter. Wenn ein Schritt nicht
fertig wird, kannst du im nächsten Ordner weiterarbeiten. Im Teilnehmerprojekt ist01 leer.

| Ordner | Aufgabe | Tag |
| --- | --- | --- |
| `01-hello-world/` | Offizielles Basic-Responses-Projekt erzeugen, Paketversionen pinnen, Agent und Streaming verstehen | 2 |
| [`02-tools`](02-tools/README.md) | Tools für Prüfauftrag, Katalog und Spezifikation | 2 |
| [`03-session-middleware`](03-session-middleware/README.md) | Session und sichtbare Toolaufrufe | 2 |
| [`04-extraktion`](04-extraktion/README.md) | Angaben in einem festen Schema extrahieren | 2 |
| [`05-workflow`](05-workflow/README.md) | Extrahieren, Regeln vergleichen, Ergebnis ausgeben | 2 |
| [`06-hitl`](06-hitl/README.md) | Optional: menschliche Entscheidung je Klärungspunkt | 3 |
| [`07-hosting`](07-hosting/README.md) | Prüfworkflow über VS Code in Foundry bereitstellen | 3 |

## Umgebung öffnen

[Eigenen Codespace öffnen](https://codespaces.new/pondhouse-data/kuenz-maf-training?quickstart=1).
Dafür brauchst du einen persönlichen GitHub-Account mit verfügbarem Codespaces-Kontingent.
Die Umgebung richtet Python 3.13, Azure CLI, Python-Debugger, GitHub Copilot und Foundry Toolkit ein.
Die festgelegten Pakete werden mit **pip** in `.venv/` installiert. Warte bis die Einrichtung fertig ist.
Foundry Toolkit läuft im Codespace über den Remote-Erweiterungshost und ist im Browsereditor verfügbar.
Optional kannst du denselben Codespace über **… → Open in Visual Studio Code** in VS Code Desktop öffnen.


Im Terminal im Repository-Hauptordner:

```bash
source .venv/bin/activate
python -c "import agent_framework.foundry; print('MAF bereit')"
cp .env.example .env
az login --use-device-code --tenant 42abcb50-0ca4-44ec-b66c-80926c94af9d
```

Prüfe das angemeldete Trainingskonto. `.env` enthält Projektadresse und Modell `training-chat`;
die Datei bleibt privat. Foundry Toolkit kann zusätzlich eine eigene Anmeldung verlangen.

## Ü8 · Im leeren Ordner01 bootstrappen

1. Der Ordner `01-hello-world/` ist leer. Die `.gitkeep` ist nur eine Git-Markierung:
   vor dem Erzeugen löschen. Im Toolkit wählst du diesen Ordner als Ziel.
2. Foundry Toolkit in der linken Leiste öffnen → **Developer Tools → Build → Create Agent**.
   Unter **Code an agent from samples**: **Agent Framework** wählen. Die aktuelle Katalogseite heißt **Build your first chat agent**.
   **Use template** → **Agent Framework → Python → Responses** wählen. Im älteren Katalog heißt
   dieselbe Vorlage **Basic Hosted Agent**.
3. Bei **Workspace Folder** den Repository-Hauptordner, bei **Folder Name** `01-hello-world` wählen.
   Prüfe das Ziel: genau der vorhandene leere Ordner01, kein zweiter01-Unterordner.
   **Setup with Microsoft Foundry** → vorhandenes Trainingsprojekt `kuenz-agents` →
   vorhandenes **Model Deployment** `training-chat` → **Create**. Kein neues Modell anlegen.
4. Den erzeugten Ordner mit `azure.yaml` als Workspace offen lassen. Der Basic-Responses-Agent liegt in
   `src/agent-framework-agent-basic-responses/main.py`; Die lokale `.env` liegt daneben. Der Katalog kann
   `requirements.txt` oder `pyproject.toml` mit `uv.lock` erzeugen.
   Falls der Katalog den Namen verändert: die genaue Quellmappe steht bei `services → … → project` in `azure.yaml`.
5. Lege die **requirements.txt in dieser Quellmappe** an bzw. ersetze sie durch den Inhalt unserer
   [`requirements.txt`](requirements.txt). So verwendet das offizielle Gerüst unseren getesteten Paketstand.
   Falls die Vorlage stattdessen `pyproject.toml`, `uv.lock` und `uv.toml` mitbringt,
   entferne diese drei Dateien aus der Quellmappe: lokale Installation und Remote-Build verwenden
   dadurch dieselbe gepinnte requirements.txt. Die generierten `.vscode`-Dateien und `main.py` bleiben erhalten.
6. **Python: Select Interpreter** → **Enter interpreter path** → unsere bestehende
   `<Repository-Hauptordner>/.venv/bin/python`. Im Codespace ist das
   `/workspaces/kuenz-maf-training/.venv/bin/python`. In der generierten Quellmappe:

   ```bash
   python -m pip install -r requirements.txt
   ```

7. Prüfe die generierte `.env`: `FOUNDRY_PROJECT_ENDPOINT` ist unsere Projektadresse,
   `AZURE_AI_MODEL_DEPLOYMENT_NAME=training-chat`. Das Sample und unsere weiteren Checkpoints verwenden denselben Modellnamen.
8. **Run and Debug → Debug Local Agent HTTP Server → F5**. Der Server startet auf Port 8088,
   Agent Inspector öffnet sich. Frage: „Was ist ein Agent? Antworte in zwei Sätzen.“
   Ändere die Instructions in `main.py`, speichere, starte neu und vergleiche.
   Agent Inspector allein startet den Server nicht. Stoppe den Debug-Lauf vor dem nächsten Serverstart.

### Direkten Aufruf und Streaming verstehen

Erzeuge mit Copilot eine kleine `agent.py` im Workspace-Hauptordner01 (neben `azure.yaml`). So bleibt der direkte
Python-Aufruf für Session-, Middleware- und Workflowübungen verständlich.

```text
Erzeuge agent.py im Workspace-Hauptordner01, auf Basis von src/agent-framework-agent-basic-responses/main.py.
Verwende Agent und FoundryChatClient, Entra-Anmeldung und load_dotenv()
für die vorhandene .env im übergeordneten Trainings-Hauptordner.
Modellname: AZURE_AI_MODEL_DEPLOYMENT_NAME.
Name HelloAgent, Instructions: Du bist ein hilfreicher Assistent. Antworte kurz und auf Deutsch.
Eine async main()-Funktion liest die Frage aus sys.argv oder verwendet
"Was ist ein Agent? Antworte in zwei Sätzen.". Rufe await agent.run(question) auf
und gib response.text aus. main.py und die Hosting-Konfiguration bleiben erhalten.
Erkläre Client, Agent, Instructions und run().
```

Zurück im Repository-Hauptordner mit aktivierter `.venv`:

```bash
python 01-hello-world/agent.py
python 01-hello-world/agent.py "Was ist ein Tool bei einem Agenten?"
```

Danach:

```text
Ändere nur agent.py auf Streaming (agent-framework-core1.21.0):
async for update in agent.run(question, stream=True):
    print(update.text, end="", flush=True)
Zum Schluss ein Zeilenumbruch. Erkläre den Unterschied zum bisherigen Aufruf.
```

Lies den Code, teste ihn und beobachte, wann die Antwort erscheint.
Öffne anschließend wieder den Repository-Hauptordner. Für02 und alle weiteren lokalen Übungen
verwenden wir dieselbe `.venv` und die root `.env`. Der vorgegebene Checkpoint02 enthält den
fertigen direkten Aufruf aus01 plus den Basic-Hosting-Einstiegspunkt; die Fachübungen arbeiten mit `agent.py`.

## Ab02 · Lokale Übungen

Alle Befehle laufen im **Repository-Hauptordner** mit aktivierter `.venv`:

```bash
python 02-tools/agent.py
python -m pytest 03-session-middleware
```

Teste je Ordner separat: die Checkpoints besitzen gleichnamige Module.
`07-hosting/` ist zusätzlich ein vollständiger Deployment-Quellordner mit eigenen
`requirements.txt`, `azure.yaml` und einer Kopie von `daten/`; sein Hosting-Einstieg wird erst in Ü13 gebaut.

## Daten und Aufbewahren

`daten/` enthält synthetische Prüfaufträge, Anforderungen, Spezifikationen und Referenzbefunde.
Im Betrieb kämen diese aus ERP, Dataverse, SharePoint beziehungsweise einer Dokumentextraktion.
`referenzbefunde.json` enthält menschlich geprüfte Sollbefunde; die lokalen Vergleiche bleiben möglich.
Beim Deployen müssen die Daten im Quellpaket liegen. Die Kopie in07 wird bei der Vorbereitung gegen root geprüft.

Speichere deine Dateien. Auf https://github.com/codespaces am Tagesende **… → Stop codespace** wählen.
Dateien und Anmeldung bleiben erhalten. Vor dem Löschen eigene Projektdateien herunterladen;
private `.env` und Anmeldung gehören nicht in eine weitergegebene Kopie.
Nach dem Training erzeugst du eigene Projekte genauso über das offizielle Toolkit.
Ein separates Starter-Repository und dessen Transfer entfallen.

[Offizieller Bootstrap, lokaler Test und Deployment](https://code.visualstudio.com/docs/intelligentapps/hosted-agents).
