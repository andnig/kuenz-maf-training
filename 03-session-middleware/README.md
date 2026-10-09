# 03 · Session und Middleware

Bisher vergisst der Agent nach jeder Antwort alles. Mit einer **Session** führt er
ein Gespräch: Folgefragen beziehen sich auf das Vorherige. Mit **Middleware** siehst
du, welches Tool er wann aufruft und wie lange es dauert.

**Ausgangspunkt:** der fertige Stand aus 02 (`agent.py`, `tools.py`, `test_tools.py`).

## Schritt 1 · Ein Gespräch mit Session

```text
Baue #file:03-session-middleware/agent.py zu einem kleinen Chat im Terminal um: Fragen lesen und beantworten,
bis eine leere Eingabe kommt. Der Agent soll sich an das bisherige Gespräch erinnern. Verwende dafür eine
Session mit agent.create_session() (Microsoft Agent Framework 1.21). Ohne Streaming.
```

```bash
uv run python 03-session-middleware/agent.py
```

Frag nacheinander: „Was gilt für R-03 bei A-100?“ und dann „Und was steht dazu in Version 1 der Spezifikation?“.
Der Agent versteht das „dazu“. Nimm zum Vergleich die Session beim Aufruf von `agent.run` heraus und frag noch einmal.

## Schritt 2 · Toolaufrufe sichtbar machen

```text
Ergänze in #file:03-session-middleware/agent.py eine Middleware mit @function_middleware aus agent_framework,
die bei jedem Toolaufruf Toolname und Dauer ausgibt, z. B. "  [Tool lade_anforderungskatalog, 0.00 s]".
```

Starte den Chat erneut. Bei jeder Frage siehst du jetzt, welche Tools das Modell aufruft.

## Code verstehen

1. **Was ist neu?** Wo entsteht die Session, wo wird sie übergeben?
2. **Welche Eingaben?** Was bekommt die Middleware (`context`) und was ist `call_next`?
3. **Was kommt zurück?** Was passiert, wenn die Middleware `call_next()` nicht aufruft?
4. **Was passiert bei Fehlern?** Was gibt die Middleware aus, wenn ein Tool einen Fehler liefert?

## Nicht fertig geworden?

Der Ordner `04-extraktion` startet mit unserem fertigen Stand dieses Schritts.
