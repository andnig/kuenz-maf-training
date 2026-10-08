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
Lege 05-workflow/regeln.py an, ohne Modellaufruf, einfach lesbar.
1. gueltige_fundstellen(anforderung, fundstellen, spezifikation): behält nur Fundstellen, deren Zitat im
   genannten Abschnitt steht (Leerzeichen und "−" vorher vereinheitlichen) und deren Abschnitt (Titel oder Text)
   keinen der anwendbarkeit.ausschlussbegriffe der Anforderung enthält.
2. bewerte(anforderung, angabe, spezifikation) gibt ein dict mit requirement_id, status, begruendung, fundstellen zurück:
   - keine gültige Fundstelle → "unklar"
   - Regel fachliche_bewertung → bewertung_vorschlag der Angabe
   - unterschiedliche Werte in den Fundstellen → "unklar" (Widerspruch)
   - sonst die Regel: teilmenge (Werte ⊆ erlaubt), maximum (Zahl ≤ grenzwert),
     version_mindestens (Versionsnummern teilweise als Zahlen vergleichen, 2.10 > 2.9), bereich_innerhalb (min/max einhalten)
   - erfüllt oder abweichend, mit einer kurzen Begründung als Satz.
Katalog: #file:daten/anforderungskatalog.json
```

```text
Schreibe in 05-workflow/test_regeln.py drei kurze pytest-Tests für #file:05-workflow/regeln.py mit echten
Zitaten aus der Spezifikation: R-03 mit Version 1.4 (§3.2, v1) ist abweichend; R-04 mit 30 ms (§4.1) und
80 ms (§A.1, v2) ist unklar; R-05 mit der Raumtemperatur aus §6.3 (v1) ist unklar.
```

```bash
uv run pytest 05-workflow
```

## Schritt 2 · Der Workflow

```text
Lege 05-workflow/workflow.py an (Microsoft Agent Framework 1.19, WorkflowBuilder und Executor mit @handler).
Vier Executors, die ein dict weiterreichen:
- AuftragLaden: review_id → lade_pruefauftrag
- AngabenExtrahieren: bekommt den Extraktions-Agenten im Konstruktor, ruft extrahiere aus extraktion.py auf
- Vergleichen: bewerte aus regeln.py für jede Anforderung des Katalogs
- ErgebnisAusgeben: ctx.yield_output mit review_id, asset_id, document_id, document_version, befunde und
  klaerungspunkte (alle Befunde, die nicht "erfüllt" sind).
Verbinde sie mit WorkflowBuilder(name="spezifikationspruefung", start_executor=...).add_chain([...]).build().
main(): review_id aus sys.argv, Workflow ausführen, Ergebnis als JSON ausgeben und danach je Anforderung mit
#file:daten/referenzbefunde.json vergleichen ("✓"/"✗").
Nutze #file:05-workflow/extraktion.py und #file:05-workflow/regeln.py.
```

```bash
uv run python 05-workflow/workflow.py PR-001
uv run python 05-workflow/workflow.py PR-201
```

Erwartet: sechs ✓ für jeden Auftrag. Klärungspunkte für PR-001: R-03 und R-05, für PR-201: R-04 und R-05.

## Code verstehen

1. **Was ist neu?** Welche vier Schritte gibt es, und wie hängen sie zusammen?
2. **Welche Eingaben?** Was reicht jeder Schritt an den nächsten weiter?
3. **Was kommt zurück?** Wie sieht das Ergebnis aus, und welche Teile sind Klärungspunkte?
4. **Was passiert bei Fehlern?** Was wird aus R-04, wenn die Extraktion §A.1 übersieht?

## Nicht fertig geworden?

Der Ordner `06-hitl` startet mit unserem fertigen Stand dieses Schritts.
