"""Prüflogik und Prüfworkflow ohne Modellaufruf: Fundstellen, fehlende/widersprüchliche Angaben, Checkpoint."""

import pytest

from pruefung import Angabe, Extraktion, Fundstelle, pruefe_spezifikation, referenz_extraktion_laden, vergleiche


def befund(befunde, requirement_id):
    return next(b for b in befunde if b["requirement_id"] == requirement_id)


def extraktion_mit(version, requirement_id, *fundstellen):
    extraktion = referenz_extraktion_laden(version)
    angabe = next(a for a in extraktion.angaben if a.requirement_id == requirement_id)
    angabe.fundstellen = list(fundstellen)
    return extraktion


@pytest.mark.parametrize("version", ["1", "2"])
def test_referenz_extraktion_entspricht_referenzbefunden(version):
    """Alle vorbereiteten Regeln einschließlich R-03 treffen die geprüfte Referenz."""
    import json
    from pathlib import Path

    referenz = json.loads((Path(__file__).parents[1] / "training_data/referenzbefunde.json").read_text(encoding="utf-8"))
    erwartet = next(p for p in referenz["pruefungen"] if p["document_version"] == version)["befunde"]
    actual = pruefe_spezifikation(version)
    for e in erwartet:
        assert befund(actual, e["requirement_id"])["status"] == e["status"], e["requirement_id"]
        assert befund(actual, e["requirement_id"])["fundstellen"] == e["fundstellen"], e["requirement_id"]


def test_erfundene_fundstelle_wird_nicht_uebernommen():
    erfunden = Fundstelle(abschnitt="6.1", zitat="von −20 °C bis +40 °C", bezug="Kran A-100", werte=["-20", "40"])
    ergebnis = befund(vergleiche(extraktion_mit("1", "R-05", erfunden), "1"), "R-05")
    assert ergebnis["status"] == "unklar"
    assert ergebnis["fundstellen"] == []
    assert "nicht im Originaltext" in ergebnis["begruendung"]


def test_fundstelle_aus_falscher_dokumentversion_wird_verworfen():
    aus_v2 = Fundstelle(abschnitt="6.2", zitat="von −20 °C bis +45 °C", bezug="Kran A-100", werte=["-20", "45"])
    assert befund(vergleiche(extraktion_mit("1", "R-05", aus_v2), "1"), "R-05")["status"] == "unklar"


def test_fehlende_angabe_ist_nie_erfuellt():
    ergebnis = befund(vergleiche(extraktion_mit("1", "R-02"), "1"), "R-02")
    assert ergebnis["status"] == "unklar"


def test_widerspruechliche_werte_sind_unklar_mit_allen_fundstellen():
    ergebnis = befund(pruefe_spezifikation("2"), "R-04")
    assert ergebnis["status"] == "unklar"
    assert [f["abschnitt"] for f in ergebnis["fundstellen"]] == ["4.1", "A.1"]


def test_grenzwert_ueberschritten_ist_abweichend():
    zu_hoch = Fundstelle(abschnitt="4.1", zitat="Die Latenz beträgt höchstens 30 ms.", bezug="Kran", werte=["60"])
    assert befund(vergleiche(extraktion_mit("1", "R-04", zu_hoch), "1"), "R-04")["status"] == "abweichend"


def test_extraktion_ohne_eintrag_fuer_anforderung():
    unvollstaendig = Extraktion(angaben=[a for a in referenz_extraktion_laden("1").angaben if a.requirement_id != "R-01"])
    assert befund(vergleiche(unvollstaendig, "1"), "R-01")["status"] == "unklar"


def test_r06_bleibt_ki_vorschlag():
    ergebnis = befund(pruefe_spezifikation("1"), "R-06")
    assert ergebnis["regel"] == "fachliche_bewertung"
    assert ergebnis["begruendung"].startswith("KI-Vorschlag")


def test_abschnitt_mit_paragraphzeichen_wird_akzeptiert():
    extraktion = extraktion_mit("1", "R-02", Fundstelle(abschnitt="§ 2.3", zitat="von 41 t bleibt unverändert",
                                                        bezug="Kran A-100", werte=["41"]))
    r02 = befund(vergleiche(extraktion, "1"), "R-02")
    assert r02["status"] == "erfüllt"
    assert r02["fundstellen"][0]["abschnitt"] == "2.3"
