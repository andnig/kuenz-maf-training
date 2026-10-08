# Künz Agententraining · Microsoft Agent Framework

In diesem Repository baust du Schritt für Schritt einen eigenen Agenten mit dem
Microsoft Agent Framework (MAF). Jeder Ordner ist ein Schritt. Du beginnst mit
`01-hello-world` und erweiterst diesen Agenten danach.

| Ordner | Was du baust | Tag |
| --- | --- | --- |
| [`01-hello-world`](01-hello-world/README.md) | Einen Agenten, der eine Frage an das Modell in Foundry schickt und antwortet | 2 |
| [`02-tools`](02-tools/README.md) | Tools: der Agent lädt Prüfauftrag, Anforderungskatalog und Spezifikation | 2 |
| [`03-session-middleware`](03-session-middleware/README.md) | Ein Gespräch mit Gedächtnis und sichtbaren Toolaufrufen | 2 |
| [`04-extraktion`](04-extraktion/README.md) | Angaben aus der Spezifikation in einem festen Schema | 2 |
| [`05-workflow`](05-workflow/README.md) | Den Prüfworkflow: extrahieren, mit Regeln vergleichen, Ergebnis ausgeben | 2 |
| [`06-hitl`](06-hitl/README.md) | Optional: ein Mensch entscheidet je Klärungspunkt | 3 |
| [`07-hosting`](07-hosting/README.md) | Den Prüfworkflow als Foundry Hosted Agent bereitstellen | 3 |

Jeder Ordner startet mit dem fertigen Stand des vorigen. Wer einen Schritt nicht
fertig bekommt, macht im nächsten Ordner weiter. Den neuen Code schreibst du mit
GitHub Copilot; jede Anleitung enthält die Prompts und sagt, wie du den Vorschlag prüfst.
Tests startest du je Ordner, z. B. `uv run pytest 02-tools`.

## Woher kommen die Daten?

Alles im Ordner `daten/` ist synthetisch und liegt als JSON im Repository. Das ist dem
Training geschuldet: So arbeiten alle ohne Zugang zu Künz-Systemen, und jeder Lauf ist
nachvollziehbar. Im Betrieb kämen dieselben Inhalte aus einem Dienst.

| Datei | Inhalt | Im Betrieb käme das aus … |
| --- | --- | --- |
| `pruefauftraege.json` | Prüfaufträge: welche Anlage, welche Spezifikation in welcher Version | der Auftragsverwaltung (z. B. Dataverse, ERP) |
| `anforderungskatalog.json` | Interne Anforderungen R-01 bis R-06 mit Vergleichsregel | einer gepflegten Quelle (z. B. Dataverse, SharePoint-Liste) |
| `spezifikation_v1.json`, `_v2.json` | Text des Kunden-Lastenhefts SPEC-001, vorab aus dem Dokument extrahiert und in Abschnitte zerlegt | einem Extraktionsdienst, der das PDF liest (z. B. MarkItDown, Azure AI Document Intelligence) |
| `referenzbefunde.json` | Von Menschen geprüfte Soll-Befunde für PR-001 und PR-201 | einem Testsatz mit abgenommenen Fällen |

## Öffnen

[Codespace im Browser öffnen](https://codespaces.new/pondhouse-data/kuenz-maf-training?quickstart=1)

Du brauchst einen persönlichen GitHub-Account. Beim Öffnen richtet der Codespace
Python 3.13, uv, die Azure CLI und die festgelegten MAF-Pakete selbst ein
(`uv sync --frozen`). Warte, bis das Terminal fertig ist.

Prüfen:

```bash
uv run python -c "import agent_framework.foundry; print('MAF bereit')"
```

Erwartet: `MAF bereit`.

## Was liegt wo?

| Datei | Aufgabe |
| --- | --- |
| `01-hello-world/` … `07-hosting/` | Ein Ordner je Lernschritt, jeweils mit Anleitung |
| `hosted.py`, `deploy.py` | Einen Agenten als Foundry Hosted Agent bereitstellen und aufrufen (Schritt 07) |
| `daten/` | Prüfaufträge, Anforderungskatalog, Spezifikation v1/v2, Referenzbefunde |
| `.env.example` | Vorlage für deine Konfiguration: Projektadresse und Deploymentname |
| `pyproject.toml`, `uv.lock` | Python-Version und exakte Paketversionen (inklusive pytest) |
| `.devcontainer/` | Einrichtung des Codespace |

Das Projekt verwendet Python 3.13, MAF Core 1.19.0 und den Foundry-Provider 1.13.1.

## Arbeit aufbewahren

Dateien speichern. Am Ende des Tages auf https://github.com/codespaces beim eigenen
Codespace **… → Stop codespace** wählen. Zum Weiterarbeiten denselben Codespace
wieder öffnen. Deine `.env` und die Azure-Anmeldung bleiben im Codespace.

Wer nach dem Training eigene Agenten baut, startet mit dem allgemeinen
[MAF-Starter](https://github.com/pondhouse-data/maf-starter).
