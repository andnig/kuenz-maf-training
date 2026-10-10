# 05 · Der Prüfworkflow

Jetzt wird aus den Bausteinen die Prüfung: ein **Workflow** aus vier festen
Schritten. Das Modell extrahiert, der Code vergleicht mit festen Regeln.

```
Auftrag laden → Angaben extrahieren → Regeln vergleichen → Ergebnis ausgeben
```

An Tag 3 machst du diesen Stand in Schritt 07 zum Hosted Agent in Foundry.

**Ausgangspunkt:** der fertige Stand aus 04.

## Schritt 1 · Die Regeln

Jede Anforderung im Katalog hat eine `vergleichsregel` (siehe `daten/anforderungskatalog.json`).

```text
Lege 05-workflow/regeln.py an: einfacher Code ohne Modellaufruf. Eine Funktion bewerte vergleicht eine Angabe
aus #file:05-workflow/extraktion.py mit ihrer Anforderung aus #file:daten/anforderungskatalog.json und liefert
den Befund: Status "erfüllt", "abweichend" oder "unklar" mit einer kurzen Begründung als Satz.
- Es zählen nur Fundstellen, deren Zitat wirklich im genannten Abschnitt steht (Leerzeichen und Minuszeichen
  tolerant vergleichen) und deren Abschnitt keinen Ausschlussbegriff der Anforderung enthält.
- Keine gültige Fundstelle oder unterschiedliche Werte → "unklar".
- Sonst gilt die vergleichsregel der Anforderung. Bei fachliche_bewertung zählt der Vorschlag des Modells.
- Versionsnummern als Zahlen vergleichen: 2.10 ist größer als 2.9.
```

```text
Schreibe in 05-workflow/test_regeln.py drei kurze pytest-Tests für #file:05-workflow/regeln.py mit echten
Zitaten aus der Spezifikation: R-03 mit Version 1.4 (§3.2, v1) ist abweichend; R-04 mit 30 ms (§4.1) und
80 ms (§A.1, v2) ist unklar; R-05 mit der Raumtemperatur aus §6.3 (v1) ist unklar.
```

```bash
python -m pytest 05-workflow
```

## Schritt 2 · Der Workflow

```text
Lege 05-workflow/workflow.py an: ein Workflow mit vier Schritten (Microsoft Agent Framework 1.21,
WorkflowBuilder und Executor):
Auftrag laden → Angaben extrahieren (#file:05-workflow/extraktion.py) → Regeln vergleichen
(#file:05-workflow/regeln.py) → Ergebnis ausgeben.
Das Ergebnis enthält review_id, asset_id, document_id, document_version, die Befunde und als klaerungspunkte
alle Befunde, die nicht "erfüllt" sind.
Aufruf mit der Auftrags-ID als Argument: Ergebnis als JSON ausgeben und danach je Anforderung mit
#file:daten/referenzbefunde.json vergleichen ("✓"/"✗").
```

```bash
python 05-workflow/workflow.py PR-001
python 05-workflow/workflow.py PR-201
```

Erwartet: sechs ✓ für jeden Auftrag. Klärungspunkte für PR-001: R-03 und R-05, für PR-201: R-04 und R-05.

## Code verstehen

1. **Was ist neu?** Welche vier Schritte gibt es, und wie hängen sie zusammen?
2. **Welche Eingaben?** Was reicht jeder Schritt an den nächsten weiter?
3. **Was kommt zurück?** Wie sieht das Ergebnis aus, und welche Teile sind Klärungspunkte?
4. **Was passiert bei Fehlern?** Was wird aus R-04, wenn die Extraktion §A.1 übersieht?

## Nicht fertig geworden?

Der Ordner `06-hitl` startet mit unserem fertigen Stand dieses Schritts.
