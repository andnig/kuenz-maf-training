# 04 · Strukturierte Ausgabe

Für die Prüfung soll das Modell nicht frei antworten, sondern **Angaben in einem
festen Schema** liefern: je Anforderung die Fundstellen mit Abschnitt, wörtlichem
Zitat und Wert. Ob eine Anforderung erfüllt ist, entscheidet danach der Code (Schritt 05).

**Ausgangspunkt:** der fertige Stand aus 03.

## Schritt 1 · Das Schema und die Extraktion

```text
Lege 04-extraktion/extraktion.py an (Microsoft Agent Framework 1.19, Pydantic).
1. Pydantic-Modelle mit Field(description=...):
   Fundstelle(abschnitt, zitat, werte: list[str]),
   Angabe(requirement_id, fundstellen: list[Fundstelle], bewertung_vorschlag: "erfüllt"/"abweichend"/"unklar" oder None, begruendung),
   Extraktion(angaben: list[Angabe]).
2. Eine Konstante ANWEISUNG für einen Agenten, der Angaben zu R-01 bis R-06 sucht, aber nicht bewertet
   (außer R-06). Regeln: nur den gelieferten Text verwenden; das ganze Dokument lesen, auch den Anhang A.x;
   wörtliche Zitate; bei unterschiedlichen Werten ALLE Fundstellen liefern; nichts erfinden.
   Format der werte: R-01 ["DE","EN"], R-02 ["41"], R-03 ["1.4"], R-04 ["30"], R-05 ["-20","40"], R-06 [].
3. baue_prompt(document_version): Anforderungen aus lade_anforderungskatalog("A-100") und alle Abschnitte
   aus lade_spezifikation(version) als Text, Abschnitte mit "§" und Nummer.
4. async extrahiere(agent, document_version): agent.run(prompt, options={"response_format": Extraktion,
   "reasoning": {"effort": "medium"}}) und response.value zurückgeben.
5. zitat_im_text(fundstelle, spezifikation): steht das Zitat wörtlich im genannten Abschnitt?
6. main(): Version aus sys.argv, Agent ohne Tools mit ANWEISUNG, Angaben je Anforderung ausgeben und
   bei jeder Fundstelle "im Text" oder "NICHT im Text" anzeigen.
Nutze die Tools aus #file:04-extraktion/tools.py als normale Funktionen und den Aufbau von #file:04-extraktion/agent.py.
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
2. **Welche Eingaben?** Was steht im Prompt, was in der ANWEISUNG?
3. **Was kommt zurück?** Was ist `response.value`, was `response.text`?
4. **Was passiert bei Fehlern?** Was zeigt `zitat_im_text`, wenn das Modell ein Zitat erfindet?

Das Schema erzwingt die **Form** der Antwort, nicht ihre **Wahrheit**. Deshalb prüft der Code die Zitate.

## Nicht fertig geworden?

Der Ordner `05-workflow` startet mit unserem fertigen Stand dieses Schritts.
