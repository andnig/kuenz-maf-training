# 02 · Tools

Dein Agent aus 01 kennt nur, was das Modell weiß. Hier bekommt er **Tools**:
Python-Funktionen, die er aufrufen darf, um Daten zu laden. Danach beantwortet
er Fragen zu Prüfaufträgen, Anforderungen und zur Spezifikation aus unseren Daten.

**Ausgangspunkt:** `agent.py` ist das fertige Hello World aus 01.
**Daten:** im Ordner `daten/` im Projekt-Hauptordner (synthetisch).

Alle Befehle im Projekt-Hauptordner. Für die Prompts öffnest du Copilot Chat
(Sprechblase oben). `#file:…` hängt eine Datei an, damit Copilot sie sieht.

## Schritt 1 · Ein Hello-World-Tool

Prompt an Copilot:

```text
Füge in #file:02-tools/agent.py ein Tool aktuelle_uhrzeit hinzu, das die aktuelle Uhrzeit
als Text "HH:MM" zurückgibt. Verwende den Decorator @tool aus agent_framework
(Microsoft Agent Framework 1.19) und einen kurzen Docstring. Übergib das Tool dem Agenten mit tools=[...].
```

Starten und vergleichen:

```bash
uv run python 02-tools/agent.py "Wie spät ist es?"
uv run python 02-tools/agent.py "Was ist ein Agent?"
```

Bei der ersten Frage ruft das Modell das Tool auf, bei der zweiten nicht. Das Modell
entscheidet anhand von Name und Docstring, ob es ein Tool braucht.

## Schritt 2 · Die drei Daten-Tools

Prompt an Copilot:

```text
Lege die Datei 02-tools/tools.py an. Verschiebe aktuelle_uhrzeit dorthin und schreibe drei weitere Tools
mit @tool aus agent_framework. Die Daten liegen im Ordner daten im Projekt-Hauptordner:
- lade_pruefauftrag(review_id) sucht in #file:daten/pruefauftraege.json den Auftrag mit dieser review_id.
- lade_anforderungskatalog(asset_id, requirement_id=None) gibt die Anforderungen aus
  #file:daten/anforderungskatalog.json zurück, auf Wunsch nur eine einzelne Anforderung.
- lade_spezifikation(document_version) lädt daten/spezifikation_v1.json bzw. daten/spezifikation_v2.json.
Beschreibe jeden Parameter mit Annotated[str, Field(description=...)] und jedes Tool mit einem Docstring.
Gibt es eine ID oder Version nicht, gib {"fehler": "..."} zurück statt eine Ausnahme zu werfen.
Halte den Code einfach. Importiere die Tools in 02-tools/agent.py, übergib alle vier dem Agenten und
ändere die Instructions: Fragen nur mit den Tools beantworten, bei einem Fehler nichts erfinden.
```

```bash
uv run python 02-tools/agent.py "Was gilt für R-03 bei A-100?"
uv run python 02-tools/agent.py "Welche Spezifikation gehört zu PR-201?"
uv run python 02-tools/agent.py "Was steht in PR-999?"
```

Erwartet: R-03 verlangt Protokollversion 2.0 · PR-201 gehört zu SPEC-001 Version 2 ·
PR-999 gibt es nicht. Der Wortlaut variiert.

## Schritt 3 · Ein paar Tests

```text
Schreibe in 02-tools/test_tools.py drei bis vier kurze pytest-Tests für #file:02-tools/tools.py:
PR-001 gehört zu Version 1, ein unbekannter Auftrag liefert "fehler", R-03 einzeln laden, Version 2 laden.
```

```bash
uv run pytest 02-tools
```

## Code verstehen, bevor du ihn übernimmst

Lies jeden Vorschlag, bevor du ihn annimmst, und beantworte für jedes Tool:

1. **Was ist neu?** Welche Zeilen hat Copilot geändert oder angelegt?
2. **Welche Eingaben?** Welche Parameter, und was sieht das Modell davon (Docstring, `description`)?
3. **Was kommt zurück?** Wie sieht das Ergebnis für PR-001 aus?
4. **Was passiert bei Fehlern?** Was bekommt das Modell bei PR-999?

Kannst du eine Frage nicht beantworten, frag Copilot: „Erkläre mir Zeile für Zeile, was … macht.“

## Nicht fertig geworden?

Kein Problem: Der Ordner `03-session-middleware` startet mit unserem fertigen Stand dieses Schritts.
