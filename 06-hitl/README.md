# 06 · Ein Mensch entscheidet (optional)

Bei Klärungspunkten soll ein Prüfer entscheiden, bevor das Ergebnis weitergeht.
Der Workflow **hält an**, fragt je Klärungspunkt nach und läuft mit den Antworten weiter.
Die Entscheidung des Menschen wird getrennt vom KI-Befund gespeichert.

**Ausgangspunkt:** der fertige Prüfworkflow aus 05.

## Schritt 1 · Den Prüfer einbauen

```text
Erweitere #file:06-hitl/workflow.py (Microsoft Agent Framework 1.19):
1. Neuer Executor Pruefer zwischen Vergleichen und ErgebnisAusgeben. Im @handler für jeden Befund, der nicht
   "erfüllt" ist, ctx.request_info(befund, str, request_id=requirement_id) aufrufen. Gibt es keinen, das dict direkt
   weitergeben.
2. Eine Methode mit @response_handler nimmt (befund, antwort: str, ctx) entgegen, merkt sich die Antwort je
   requirement_id und gibt das dict mit "entscheidungen" weiter, sobald alle Antworten da sind.
3. ErgebnisAusgeben schreibt zusätzlich "entscheidungen" ins Ergebnis.
4. main(): den Workflow mit stream=True laufen lassen und alle Ereignisse vom Typ "request_info" sammeln.
   Für jede Anfrage Befund und Fundstellen anzeigen und mit input() die Entscheidung abfragen.
   Danach workflow.run(responses=antworten) und das Ergebnis als JSON ausgeben.
```

```bash
uv run python 06-hitl/workflow.py PR-101
```

Nimm statt PR-101 deinen eigenen Prüfauftrag (PR-101 bis PR-105). Erwartet: zwei Fragen
(R-03 und R-05) und im Ergebnis deine beiden Entscheidungen unter `entscheidungen`.

## Code verstehen

1. **Was ist neu?** Wo hält der Workflow an, wo läuft er weiter?
2. **Welche Eingaben?** Was sieht der Prüfer, was gibt er zurück?
3. **Was kommt zurück?** Wo stehen KI-Befund und menschliche Entscheidung im Ergebnis?
4. **Was passiert bei Fehlern?** Was passiert, wenn eine Antwort fehlt?

Im Betrieb würde der Workflow seinen Stand speichern (Checkpoint) und erst Stunden später
weiterlaufen. In der Übung läuft alles in einem Prozess.
