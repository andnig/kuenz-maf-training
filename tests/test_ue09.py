import asyncio
import json
from pathlib import Path
import pytest
from agent_framework import FileCheckpointStorage
from lessons.ue09_agent import build_agent
from lessons.ue11_workflow import execute
from lessons.ue12_hitl import build_workflow
from pruefworkflow import CHECKPOINT_TYPEN, WORKFLOW_NAME, PrueferEntscheidung


def test_ue09_agent_has_two_tools_and_instructions():
    from unittest.mock import MagicMock
    from agent_framework import BaseChatClient
    agent = build_agent(MagicMock(spec=BaseChatClient))
    assert agent.default_options["instructions"] and len(agent.default_options["instructions"]) > 100
    assert {t.name for t in agent.default_options["tools"]} >= {"lade_anforderungskatalog", "lade_spezifikation"}

