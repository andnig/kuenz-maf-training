import asyncio
import json
from pathlib import Path
import pytest
from agent_framework import FileCheckpointStorage
from lessons.ue09_agent import build_agent
from lessons.ue11_workflow import execute
from lessons.ue12_hitl import build_workflow
from pruefworkflow import CHECKPOINT_TYPEN, WORKFLOW_NAME, PrueferEntscheidung


def test_ue12_persist_restore_and_separate_decision(tmp_path):
    async def check():
        storage = FileCheckpointStorage(tmp_path, allowed_checkpoint_types=CHECKPOINT_TYPEN)
        initial = await build_workflow(storage, "referenz").run("PR-103")
        checkpoint = await storage.get_latest(workflow_name=WORKFLOW_NAME)
        assert len(checkpoint.pending_request_info_events) == 6
        del initial, storage
        storage = FileCheckpointStorage(tmp_path, allowed_checkpoint_types=CHECKPOINT_TYPEN)
        restored = build_workflow(storage, "referenz")
        questions = {}
        async for e in restored.run(checkpoint_id=checkpoint.checkpoint_id, stream=True):
            if e.type == "request_info": questions[e.request_id] = e.data
        answers = {key: PrueferEntscheidung("bestätigt", q.befund["status"], "", "test") for key,q in questions.items()}
        answers["PR-103/R-06"] = PrueferEntscheidung("korrigiert", "unklar", "Sperrlogik prüfen", "test")
        final = await restored.run(responses=answers)
        report = final.get_outputs()[0]
        r06 = next(b for b in report["befunde"] if b["requirement_id"] == "R-06")
        assert r06["ki_befund"]["status"] == "erfüllt" and r06["endgueltiger_status"] == "unklar"
        assert report["review_id"] == "PR-103" and report["document_version"] == "1"
    asyncio.run(check())


def test_workflow_pausiert_und_wird_in_neuer_instanz_fortgesetzt(tmp_path):
    """Persistente sechs Anfragen; frische Workflowinstanz verwendet dieselben Requests."""
    async def check():
        storage = FileCheckpointStorage(tmp_path, allowed_checkpoint_types=CHECKPOINT_TYPEN)
        original = {}
        async for event in build_workflow(storage, "referenz").run("PR-103", stream=True):
            if event.type == "request_info": original[event.request_id] = event.data
        assert sorted(original) == [f"PR-103/R-0{i}" for i in range(1, 7)]
        storage = FileCheckpointStorage(tmp_path, allowed_checkpoint_types=CHECKPOINT_TYPEN)
        checkpoint = await storage.get_latest(workflow_name=WORKFLOW_NAME)
        assert len(checkpoint.pending_request_info_events) == 6
        workflow = build_workflow(storage, "referenz")
        restored = {}
        async for event in workflow.run(checkpoint_id=checkpoint.checkpoint_id, stream=True):
            if event.type == "request_info": restored[event.request_id] = event.data
        assert sorted(restored) == sorted(original)
        decisions = {key: PrueferEntscheidung("bestätigt", q.befund["status"], "", "test") for key,q in restored.items()}
        decisions["PR-103/R-06"] = PrueferEntscheidung("korrigiert", "unklar", "Sperrlogik klären", "test")
        report = (await workflow.run(responses=decisions)).get_outputs()[0]
        assert (report["review_id"], report["document_version"], report["extraktion"]) == ("PR-103", "1", "referenz")
        r06 = next(b for b in report["befunde"] if b["requirement_id"] == "R-06")
        assert r06["ki_befund"]["status"] == "erfüllt"
        assert r06["pruefer_entscheidung"]["entscheidung"] == "korrigiert"
        assert r06["endgueltiger_status"] == "unklar"
        assert "R-06" in report["klaerungspunkte"]
    asyncio.run(check())
