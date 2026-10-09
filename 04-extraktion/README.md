# 04 · Strukturierte Ausgabe

Für die Prüfung soll das Modell nicht frei antworten, sondern **Angaben in einem
festen Schema** liefern: je Anforderung die Fundstellen mit Abschnitt, wörtlichem
Zitat und Wert. Ob eine Anforderung erfüllt ist, entscheidet danach der Code (Schritt 05).

**Ausgangspunkt:** der fertige Stand aus 03.

## Schritt 1 · Das Schema und die Extraktion

```text
Lege 04-extraktion/extraktion.py an (Microsoft Agent Framework 1.19). Ein Agent ohne Tools liest eine Version
der Spezifikation und liefert zu jeder Anforderung R-01 bis R-06 die Fundstellen: Abschnitt, wörtliches Zitat
und die gefundenen Werte. Er bewertet nicht. Nur bei R-06 schlägt er "erfüllt", "abweichend" oder "unklar" vor,
mit Begründung.
- Die Antwort kommt in einem festen Schema (Pydantic, response_format), nicht als freier Text.
- Im Prompt stehen die Anforderungen von A-100 und der ganze Text der Spezifikation samt Anhang.
  Hol beides mit den Funktionen aus #file:04-extraktion/tools.py.
- Anweisung an den Agenten: nur den gelieferten Text verwenden, wörtlich zitieren, bei unterschiedlichen
  Werten alle Fundstellen liefern, nichts erfinden. Werte als Liste ohne Einheit, z. B. ["DE","EN"], ["41"], ["1.4"], ["-20","40"].
- Das Modell soll gründlich lesen (reasoning effort medium).
- Prüfe im Code, ob jedes Zitat wirklich im genannten Abschnitt steht.
- Aufruf mit der Version als Argument. Gib je Anforderung die Fundstellen aus, jeweils mit "im Text" oder "NICHT im Text".
Baue den Agenten so auf wie in #file:04-extraktion/agent.py.
```

```bash
uv run python 04-extraktion/extraktion.py 1
uv run python 04-extraktion/extraktion.py 2
```

Erwartet für Version 2 bei R-04 **zwei** Fundstellen: §4.1 mit 30 ms und §A.1 mit 80 ms.
Die Spezifikation widerspricht sich hier. Für Version 1 nennt das Modell bei R-05 vermutlich
§6.3 mit einer Raumtemperatur; das betrifft das Bedienpult, nicht den Kran.

## Code verstehen

1. **Was ist neu?** Wo steht das Schema, wo wird es dem Modell übergeben?
2. **Welche Eingaben?** Was steht im Prompt, was in den Instructions des Agenten?
3. **Was kommt zurück?** Was ist `response.value`, was `response.text`?
4. **Was passiert bei Fehlern?** Was zeigt die Ausgabe, wenn das Modell ein Zitat erfindet?

Das Schema erzwingt die **Form** der Antwort, nicht ihre **Wahrheit**. Deshalb prüft der Code die Zitate.

## Nicht fertig geworden?

Der Ordner `05-workflow` startet mit unserem fertigen Stand dieses Schritts.
