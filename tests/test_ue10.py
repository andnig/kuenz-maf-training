import asyncio
from types import SimpleNamespace
import pytest
from lessons.ue10_session import compare_sessions, observe_tool
from training_tools import anforderungskatalog_laden


def test_session_identity_is_shared_only_on_follow_up():
    class RecordingAgent:
        def __init__(self): self.calls = []
        def create_session(self): return object()
        async def run(self, prompt, *, session=None):
            self.calls.append((prompt, session))
            return SimpleNamespace(text="Modellwortlaut beliebig")
    agent = RecordingAgent()
    result = asyncio.run(compare_sessions(agent))
    assert set(result) == {"first", "with_session", "without_session"}
    assert agent.calls[0][1] is agent.calls[1][1] and agent.calls[0][1] is not None
    assert agent.calls[2][1] is None


def test_r99_error_reliably_passes_through_middleware(capsys):
    context = SimpleNamespace(function=SimpleNamespace(name="lade_anforderungskatalog"), arguments={"requirement_id":"R-99"})
    async def next_call(): anforderungskatalog_laden("A-100", "R-99")
    with pytest.raises(ValueError, match="R-99"):
        asyncio.run(observe_tool(context, next_call))
    output = capsys.readouterr().out
    assert "tool.start" in output and "tool.error" in output and "tool.end" in output
