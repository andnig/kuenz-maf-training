from regeln import bewerte
from tools import lade_anforderungskatalog, lade_spezifikation


def anforderung(requirement_id):
    return lade_anforderungskatalog("A-100", requirement_id)["requirements"][0]


def angabe(*fundstellen):
    return {"fundstellen": list(fundstellen), "bewertung_vorschlag": None}


def test_alte_protokollversion_weicht_ab():
    v1 = lade_spezifikation("1")
    f = {"abschnitt": "3.2", "zitat": "Künz TOS-Interface in Protokollversion 1.4", "werte": ["1.4"]}
    assert bewerte(anforderung("R-03"), angabe(f), v1)["status"] == "abweichend"


def test_widerspruechliche_latenz_ist_unklar():
    v2 = lade_spezifikation("2")
    f1 = {"abschnitt": "4.1", "zitat": "Latenz beträgt höchstens 30 ms", "werte": ["30"]}
    f2 = {"abschnitt": "A.1", "zitat": "bis zu 80 ms Latenz eingeplant", "werte": ["80"]}
    assert bewerte(anforderung("R-04"), angabe(f1, f2), v2)["status"] == "unklar"


def test_raumtemperatur_zaehlt_nicht():
    v1 = lade_spezifikation("1")
    f = {"abschnitt": "6.3", "zitat": "bei einer Raumtemperatur von +10 °C bis +35 °C funktionsfähig", "werte": ["10", "35"]}
    assert bewerte(anforderung("R-05"), angabe(f), v1)["status"] == "unklar"
