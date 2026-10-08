# 07 · Der Prüfworkflow als Hosted Agent

Bisher läuft dein Workflow nur in deinem Codespace. Jetzt stellst du ihn in Microsoft
Foundry bereit: als **Hosted Agent**, den andere über die Responses-API aufrufen können,
zum Beispiel der Dispatcher in Copilot Studio.

Dafür gibt es im Projekt-Hauptordner zwei fertige Werkzeuge, die für jeden MAF-Agenten passen:

| Datei | Aufgabe |
| --- | --- |
| `hosted.py` | Läuft in Foundry. Lädt `erstelle_agent()` aus deiner Datei und stellt den Agenten bereit. |
| `deploy.py` | Läuft im Codespace. Lädt das Projekt hoch, ruft den Agenten auf, holt gespeicherte Antworten. |

Deine Aufgabe: Der Workflow muss sich wie ein Agent verhalten. Er bekommt eine Nachricht
(„Prüfe PR-101“) und antwortet mit Text (dem Ergebnis als JSON).

**Ausgangspunkt:** der fertige Prüfworkflow aus 05.

## Schritt 1 · Den Workflow zum Agenten machen

```text
Erweitere #file:07-hosting/workflow.py, damit der Workflow als Agent laufen kann (Microsoft Agent Framework 1.19):
1. AuftragLaden bekommt statt eines Strings list[Message] (aus agent_framework). Hole die Auftrags-ID mit
   re.search(r"PR-\d{3}", ...) aus dem Text der letzten Nachricht. Liefert lade_pruefauftrag einen Fehler,
   gib ihn mit ctx.yield_output als JSON-Text aus und höre auf (WorkflowContext[dict, str]).
2. ErgebnisAusgeben gibt das Ergebnis als JSON-Text aus (json.dumps mit ensure_ascii=False,
   WorkflowContext[Never, str]) und ergänzt "run_id": str(uuid4()).
3. Neue Funktion erstelle_agent(): FoundryChatClient mit DefaultAzureCredential aus azure.identity,
   Extraktions-Agent wie bisher, Rückgabe baue_workflow(extraktion).as_agent(name="Spezifikationspruefung").
4. main(): erstelle_agent().run(f"Prüfe {review_id}") aufrufen, response.text mit json.loads lesen,
   ausgeben und wie bisher mit der Referenz vergleichen.
```

```bash
uv run python 07-hosting/workflow.py PR-001
```

Erwartet: dasselbe Ergebnis wie in 05 (sechs ✓), jetzt mit `run_id`.

## Schritt 2 · Deployen

Nimm deinen Agentnamen `kuenz-pruefung-trainingNN` (NN = deine Nummer, z. B. 03).

```bash
uv run python deploy.py deploy kuenz-pruefung-training03 --datei 07-hosting/workflow.py
```

Foundry baut den Agenten (etwa 1 Minute) und meldet `active`. Danach gehen alle Aufrufe an diese Version.

## Schritt 3 · Aufrufen und gespeicherte Antwort abrufen

```bash
uv run python deploy.py invoke kuenz-pruefung-training03 "Prüfe PR-103"
uv run python deploy.py status kuenz-pruefung-training03 <response_id>
```

`invoke` startet eine neue Prüfung. Die erste Zeile zeigt `response_id`, Agentname und Version.
`status` holt die gespeicherte Antwort mit dieser ID ab: kein neuer Modellaufruf, dasselbe Ergebnis, dieselbe `run_id`.

## Code verstehen

1. **Was ist neu?** Was macht `as_agent()`, und warum braucht der erste Schritt jetzt `list[Message]`?
2. **Welche Eingaben?** Was schickt `deploy.py invoke` an Foundry, was kommt in `hosted.py` an?
3. **Was kommt zurück?** Woher kommen `response_id`, Agentname und Version, woher `run_id`?
4. **Was passiert bei Fehlern?** Was antwortet der Agent auf „Prüfe PR-999“?

`hosted.py` und `deploy.py` musst du nicht ändern. Lies sie trotzdem einmal: Beide sind kurz.
