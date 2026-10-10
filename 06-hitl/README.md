# 06 · Ein Mensch entscheidet (optional)

Bei Klärungspunkten soll ein Prüfer entscheiden, bevor das Ergebnis weitergeht.
Der Workflow **hält an**, fragt je Klärungspunkt nach und läuft mit den Antworten weiter.
Die Entscheidung des Menschen wird getrennt vom KI-Befund gespeichert.

**Ausgangspunkt:** der fertige Prüfworkflow aus 05.

## Schritt 1 · Den Prüfer einbauen

```text
Erweitere #file:06-hitl/workflow.py (Microsoft Agent Framework 1.21): Vor dem Ergebnis entscheidet ein Mensch
jeden Klärungspunkt.
- Neuer Schritt Pruefer nach dem Vergleich: Er fragt für jeden Befund, der nicht "erfüllt" ist, mit
  ctx.request_info nach und läuft mit @response_handler weiter, sobald alle Antworten da sind.
- Die Entscheidungen kommen getrennt von den Befunden als "entscheidungen" ins Ergebnis.
- Im Terminal: zu jeder Frage Befund und Fundstellen zeigen, die Entscheidung abfragen und den Workflow
  mit den Antworten fortsetzen.
```

```bash
python 06-hitl/workflow.py PR-101
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
