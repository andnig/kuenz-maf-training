from tools import lade_anforderungskatalog, lade_pruefauftrag, lade_spezifikation


def test_pruefauftrag_pr001():
    assert lade_pruefauftrag("PR-001")["document_version"] == "1"


def test_unbekannter_pruefauftrag():
    assert "fehler" in lade_pruefauftrag("PR-999")


def test_einzelne_anforderung():
    katalog = lade_anforderungskatalog("A-100", "R-03")
    assert [a["requirement_id"] for a in katalog["requirements"]] == ["R-03"]


def test_spezifikation_version_2():
    assert lade_spezifikation("2")["document_version"] == "2"
