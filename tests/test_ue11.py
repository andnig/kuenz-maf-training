import asyncio
import json
from pathlib import Path
import pytest
from agent_framework import FileCheckpointStorage
from lessons.ue09_agent import build_agent
from lessons.ue11_workflow import execute
from lessons.ue12_hitl import build_workflow
from pruefworkflow import CHECKPOINT_TYPEN, WORKFLOW_NAME, PrueferEntscheidung


@pytest.mark.parametrize("review,version", [("PR-001", "1"), ("PR-201", "2")])
def test_ue11_reference_cases(review, version):
    r = asyncio.run(execute(review, "referenz"))
    reference = json.loads((Path(__file__).parents[1]/"training_data/referenzbefunde.json").read_text())
    expected = next(p for p in reference["pruefungen"] if p["document_version"] == version)["befunde"]
    assert r.kontext.review_id == review
    assert [(b["requirement_id"], b["status"]) for b in r.befunde] == [(b["requirement_id"], b["status"]) for b in expected]

