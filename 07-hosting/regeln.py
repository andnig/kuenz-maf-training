"""Vergleichsregeln: normaler Python-Code, kein Modell. Jede Anforderung bekommt einen Status."""


def normalisiere(text: str) -> str:
    return " ".join(text.replace("−", "-").split())


def zahl(text: str) -> float:
    return float(normalisiere(text).replace("+", "").replace(",", "."))


def version(text: str) -> tuple[int, ...]:
    return tuple(int(teil) for teil in text.strip().split("."))


def gueltige_fundstellen(anforderung: dict, fundstellen: list[dict], spezifikation: dict) -> list[dict]:
    """Behält nur Fundstellen, deren Zitat im Abschnitt steht und die den richtigen Gegenstand betreffen."""
    abschnitte = {a["abschnitt"]: a for a in spezifikation["abschnitte"]}
    ausschluss = anforderung.get("anwendbarkeit", {}).get("ausschlussbegriffe", [])
    gueltig = []
    for fundstelle in fundstellen:
        abschnitt = abschnitte.get(fundstelle["abschnitt"].strip("§ "))
        if abschnitt is None or normalisiere(fundstelle["zitat"]) not in normalisiere(abschnitt["text"]):
            continue
        text = (abschnitt["titel"] + " " + abschnitt["text"]).lower()
        if any(begriff.lower() in text for begriff in ausschluss):
            continue
        gueltig.append(fundstelle)
    return gueltig


def bewerte(anforderung: dict, angabe: dict, spezifikation: dict) -> dict:
    """Wendet die Vergleichsregel aus dem Katalog an und gibt einen Befund zurück."""
    regel = anforderung["vergleichsregel"]
    fundstellen = gueltige_fundstellen(anforderung, angabe["fundstellen"], spezifikation)

    def befund(status: str, begruendung: str) -> dict:
        return {"requirement_id": anforderung["requirement_id"], "status": status,
                "begruendung": begruendung, "fundstellen": fundstellen}

    if not fundstellen:
        return befund("unklar", "Die Spezifikation macht dazu keine passende Angabe.")
    if regel["typ"] == "fachliche_bewertung":
        return befund(angabe["bewertung_vorschlag"] or "unklar", "Vorschlag des Modells, ein Mensch entscheidet.")

    werte = {tuple(f["werte"]) for f in fundstellen}
    if len(werte) > 1:
        genannt = " und ".join(" bis ".join(w) for w in sorted(werte))
        return befund("unklar", f"Die Spezifikation nennt unterschiedliche Werte: {genannt}.")
    wert = fundstellen[0]["werte"]

    einheit = regel.get("einheit", "")
    if regel["typ"] == "teilmenge":
        erfuellt = set(wert) <= set(regel["erlaubt"])
        text = f"Gefordert {', '.join(wert)}, lieferbar {', '.join(regel['erlaubt'])}."
    elif regel["typ"] == "maximum":
        erfuellt = zahl(wert[0]) <= regel["grenzwert"]
        text = f"{wert[0]} {einheit} gegenüber höchstens {regel['grenzwert']} {einheit}."
    elif regel["typ"] == "version_mindestens":
        erfuellt = version(wert[0]) >= version(regel["grenzwert"])
        text = f"Protokollversion {wert[0]} gegenüber mindestens {regel['grenzwert']}."
    elif regel["typ"] == "bereich_innerhalb":
        erfuellt = zahl(wert[0]) >= regel["min"] and zahl(wert[1]) <= regel["max"]
        text = f"{wert[0]} bis {wert[1]} {einheit} gegenüber erlaubt {regel['min']} bis {regel['max']} {einheit}."
    else:
        return befund("unklar", f"Unbekannte Regel {regel['typ']}.")

    return befund("erfüllt" if erfuellt else "abweichend", text)
