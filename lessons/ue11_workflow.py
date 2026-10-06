import argparse
import asyncio
from agent_framework import WorkflowBuilder
from pruefworkflow import AuftragLaden, AngabenExtrahieren, Vergleichen
from pruefservice.workflow import BefundeAusgeben


def build_workflow(extraktion="modell", client=None):
    # TODO Ü11: vier vorbereitete Executors instanziieren und selbst als Kette verbinden.
    # AuftragLaden → AngabenExtrahieren → Vergleichen → BefundeAusgeben, stabiler Workflowname.
    raise NotImplementedError("Ü11: MAF-Workflow zusammensetzen")


async def execute(review_id, extraktion="modell", client=None):
    result = await build_workflow(extraktion, client).run(review_id)
    outputs = result.get_outputs()
    if len(outputs) != 1:
        raise RuntimeError("Workflow lieferte nicht genau ein Ergebnis")
    return outputs[0]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("review_id", default="PR-001", nargs="?")
    p.add_argument("--extraktion", choices=["modell", "referenz"], default="referenz")
    a = p.parse_args()
    result = asyncio.run(execute(a.review_id, a.extraktion))
    for b in result.befunde:
        print(b["requirement_id"], b["status"], b["begruendung"])
