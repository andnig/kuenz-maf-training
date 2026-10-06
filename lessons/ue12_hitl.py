from agent_framework import WorkflowBuilder, response_handler, WorkflowContext
from pruefworkflow import (
    AuftragLaden, AngabenExtrahieren, Vergleichen, Pruefer, BerichtErstellen,
    PrueferAnfrage, PrueferEntscheidung, PrueferErgebnis,
)


class ParticipantReviewer(Pruefer):
    @response_handler
    async def entscheidung_erhalten(self, anfrage: PrueferAnfrage, entscheidung: PrueferEntscheidung,
                                    ctx: WorkflowContext[PrueferErgebnis]):
        # TODO Ü12: Entscheidung zu requirement_id speichern, erst bei allen sechs Antworten
        # PrueferErgebnis senden. KI-Befunde nicht überschreiben. Korrektur braucht Kommentar.
        raise NotImplementedError("Ü12: Menschenschritt anbinden")


def build_workflow(storage=None, extraktion="modell"):
    # TODO Ü12: Prüfer + Bericht an die bekannte Kette hängen, checkpoint_storage setzen.
    # Workflowname spezifikationspruefung und Executor-IDs nicht ändern (Prozesswechsel).
    raise NotImplementedError("Ü12: Checkpoint-Workflow zusammensetzen")
