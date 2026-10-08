# 01 · Hello World

Dein erster Agent mit dem Microsoft Agent Framework (MAF). Er schickt eine Frage
an ein Modell in Microsoft Foundry und gibt die Antwort aus.

Alles passiert in einer Datei: [`agent.py`](agent.py). Arbeite die TODOs darin
der Reihe nach ab.

## Was du am Ende hast

Einen Agenten, der

- seine Konfiguration aus `.env` liest,
- sich mit deiner Azure-Anmeldung beim Modell meldet,
- mit eigenem Namen und eigenen Instructions antwortet,
- die Antwort einmal am Stück und einmal Stück für Stück (Streaming) ausgibt.

Dieser Agent ist die Grundlage für alle weiteren Schritte.

## Schritte

Alle Befehle laufen im Terminal im Projekt-Hauptordner (**Terminal → New Terminal**).

1. **Konfiguration** (TODO 1)

   ```bash
   cp .env.example .env
   ```

   Öffne `.env`. Projektadresse und Deploymentname sind schon eingetragen.

2. **Anmelden** (TODO 2)

   ```bash
   az login --use-device-code --tenant 42abcb50-0ca4-44ec-b66c-80926c94af9d
   ```

   Öffne den angezeigten Link, gib den Code ein und wähle dein Trainingskonto.
   Ersetze danach in `agent.py` bei `credential = None` das `None` durch
   `AzureCliCredential()`.

3. **Name und Instructions** (TODO 3)

   Ersetze die beiden `"TODO"` durch einen Namen und deine Instructions.

4. **Starten** (TODO 4)

   ```bash
   uv run python 01-hello-world/agent.py
   uv run python 01-hello-world/agent.py "Was ist ein Tool bei einem Agenten?"
   ```

   Erwartet: eine kurze deutsche Antwort. Der Wortlaut ist bei jedem Lauf anders.
   Ändere die Instructions, starte erneut und vergleiche.

5. **Streaming mit Copilot** (TODO 5)

   Lass Copilot Chat den Aufruf auf Streaming umbauen. Den Text für Copilot
   findest du im TODO. Lies die Änderung, bevor du sie übernimmst.

## Wenn etwas nicht klappt

| Meldung | Ursache und Lösung |
| --- | --- |
| `TODO 1: .env fehlt oder ist leer` | `cp .env.example .env` im Projekt-Hauptordner ausführen. |
| `Azure credential is required …` | TODO 2: `None` durch `AzureCliCredential()` ersetzen. |
| `Please run 'az login'` oder `AzureCliCredential.get_token failed` | Anmeldung fehlt oder ist abgelaufen: `az login --use-device-code --tenant …` wiederholen. |
| `PermissionDenied` oder `403` | Das Konto hat keine Rolle zum Modellaufruf (Foundry User auf dem Projekt). |
| `No such file or directory: 01-hello-world/agent.py` | Du bist nicht im Projekt-Hauptordner. `cd /workspaces/kuenz-maf-training` |
