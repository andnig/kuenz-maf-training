# Künz Agententraining: deine Entwicklungsumgebung

Öffne [deinen Codespace im Browser](https://codespaces.new/andnig/kuenz-maf-training?quickstart=1).
Du brauchst einen persönlichen GitHub-Account und einen Browser. Python 3.13,
uv, Azure CLI und die festgelegten MAF-Pakete werden automatisch eingerichtet.
Jede Person arbeitet in ihrem eigenen Codespace. Die Beispieldaten sind synthetisch.

[Vorbereitung zum Ausdrucken (PDF)](vorbereitung.pdf)

## Vor dem Training

1. Öffne den Link und wähle **Create codespace**. Warte auf den fertigen Editor und das Ende der Einrichtung.
2. **Terminal → New Terminal**. Führe `uv run python umgebung_pruefen.py` aus. Erwartet: `"umgebung": "OK"`.
3. Melde im Trainingschat „Codespace OK“ oder den Schritt und die Fehlermeldung.
4. Öffne https://github.com/codespaces und wähle beim eigenen Codespace **… → Stop codespace**.

GitHub zeigt beim Start, welchem Account die Nutzung zugerechnet wird. Persönliche
Accounts haben ein enthaltenes Kontingent; prüfe in deinen GitHub-Einstellungen,
ob ausreichend Kontingent verfügbar ist. Bei einer Sperre melde dich beim Trainer.
Die Berechtigung für GitHub Copilot wird separat geprüft; Codespaces und Copilot
haben getrennte Kontingente bzw. Lizenzen.

## Im Training: Übung 8

Öffne deinen bestehenden Codespace über https://github.com/codespaces.
Alle Befehle laufen im Terminal im Projekt-Hauptordner.

```bash
uv run python umgebung_pruefen.py
az login --use-device-code --tenant 42abcb50-0ca4-44ec-b66c-80926c94af9d
az account set --subscription "Kuenz Training 2026"
```

Bestätige den Gerätecode im Browser mit deinem persönlichen **Trainingskonto**.
Die vorbereitete `.env` enthält Projekt und Modell. Setze `HOSTED_AGENT_NAME`
auf deine Nummer, z. B. `kuenz-pruefung-training03` für Person 03.

```bash
uv run python -m lessons.ue08_model
```

Lies danach `lessons/runtime.py` und `lessons/ue08_model.py`; die weiteren
Schritte stehen im Aufgabenblatt Ü8. Für Ü9–Ü13 verwendest du denselben Codespace.
Die roten TODO-Tests der späteren Übungen gehören zum Starterstand.

## Arbeit aufbewahren

Dateien speichern, dann den Codespace stoppen. Zum Fortsetzen denselben Codespace
wieder öffnen. GitHub löscht Codespaces nach ihrer eingestellten Aufbewahrungsfrist;
sichere deshalb deinen Stand am Ende jedes Trainingstags:

```bash
uv run python sichern.py
```

Im Explorer `mein-training.zip` rechts anklicken → **Download**. Die Sicherung
enthält deinen Code und die Ergebnisse; `.env` und die Azure-Anmeldung bleiben
in deiner persönlichen Umgebung. Danach **Stop codespace**.

Quellen (abgerufen 06.10.2026):
- [Codespaces-Vorlagen](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-from-a-template)
- [Kontingente und Abrechnung](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces)
