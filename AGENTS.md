# Projektanleitung für den Coding-Assistenten

Starterpaket des Künz-Agententrainings (synthetische Beispieldaten). Teilnehmer bauen hier in Übung 9–12 einen eigenen Agenten und Workflow mit dem Microsoft Agent Framework (MAF) und deployen ihn in Übung 13 als Foundry Hosted Agent. Du hilfst bei genau einem TODO; die Person muss jede Zeile erklären können.

## Umgebung

- Python 3.13 (`requires-python = ">=3.13,<3.14"`), Abhängigkeiten fest gepinnt in `pyproject.toml` und `uv.lock` (u. a. `agent-framework-core==1.19.0`, `agent-framework-foundry==1.13.1`). Installiert wird nur mit `uv sync --frozen`; die Versionen bleiben, wie sie sind – keine Pakete hinzufügen oder aktualisieren.
- Anmeldung über `az login` (Entra); Endpunkt und Modell stehen in `.env`. Inhalte aus `.env`, Tokens und Schlüssel erscheinen nie in Code, Ausgaben oder Prompts.
- Alle Befehle im Projekt-Hauptordner, Programme als Modul: `uv run python -m lessons.<datei>`.

## Arbeitsbereich: ein TODO

Geändert wird nur die Übungsdatei des aktuellen TODO, und darin nur der markierte Teil:

| Übung | Datei | Ausführen | Offline-Test |
|---|---|---|---|
| Ü9 | `lessons/ue09_agent.py` | `uv run python -m lessons.ue09_agent "Frage"` | `uv run pytest tests/test_ue09.py -q` |
| Ü10 | `lessons/ue10_session.py` | `uv run python -m lessons.ue10_session` | `uv run pytest tests/test_ue10.py -q` |
| Ü11 | `lessons/ue11_workflow.py` | `uv run python -m lessons.ue11_workflow PR-001 --extraktion referenz` | `uv run pytest tests/test_ue11.py -q` |
| Ü12 | `lessons/ue12_hitl.py` | `uv run python pruefen.py start PR-101 --extraktion referenz`, dann `status` und `fortsetzen` | `uv run pytest tests/test_ue12.py -q` |

Die TODO-Kommentare sind die Anforderung (welche Bausteine, welche Namen und IDs stabil bleiben). Alles andere ist vorbereitet und bleibt unverändert: `training_tools.py` (Tools), `pruefung.py` (Regeln), `pruefworkflow.py` und `pruefservice/` (Executors, Typen), `training_data/`, `referenz/`, `tests/`, `hosted_main.py`. Fachliche Entscheidungen trifft der Code in `pruefung.py`; Instructions beschreiben Rolle und Toolnutzung, aber vergleichen keine Grenzwerte.

## MAF 1.19 – die im Projekt verwendeten Namen

Orientiere dich an den Imports und Aufrufen, die schon im Repository stehen:

- Agent: `Agent(client=…, name=…, instructions=…, tools=[…], middleware=[…])`, Aufruf `await agent.run(text)`; der Client kommt aus `lessons/runtime.py`.
- Session: `session = agent.create_session()`, dann `await agent.run(text, session=session)`.
- Middleware: `@function_middleware` mit `async def …(context: FunctionInvocationContext, call_next)`, darin `await call_next()`.
- Workflow: `WorkflowBuilder` mit den vorbereiteten Executors aus `pruefworkflow.py`; Ergebnis über `result.get_outputs()`.
- Menschenschritt: `@response_handler`, `WorkflowContext`, `FileCheckpointStorage`.

Beispiele aus dem Netz mit `ChatAgent`, `AgentThread` oder `@ai_function` stammen aus älteren Versionen; übertrage sie auf die Namen oben.

## Fertig, wenn

1. Der Offline-Test der Übung grün ist (`uv run pytest -q` zeigt Übungstests späterer Übungen weiterhin rot – das ist gewollt).
2. Ein echter Lauf mit dem Befehl aus der Tabelle das erwartete Verhalten zeigt.
3. `uv run python code_review.py` nur Änderungen in der Übungsdatei zeigt; die Person erklärt den Diff (was neu ist, Eingaben, Rückgabe, Fehlerpfad).
