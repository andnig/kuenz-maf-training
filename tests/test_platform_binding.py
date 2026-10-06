import asyncio
from types import SimpleNamespace

from agent_framework_foundry_hosting import ResponsesHostServer
from hosted_main import TrainingResponsesHostServer
from review_contract import PLATFORM_BINDING


def test_parallel_request_ids_do_not_leak(monkeypatch):
    async def fake(self, request, context, cancel):
        await asyncio.sleep(0)
        yield dict(PLATFORM_BINDING.get())
    monkeypatch.setattr(ResponsesHostServer, "_handle_response", fake)
    server = object.__new__(TrainingResponsesHostServer)
    async def collect(rid):
        ctx = SimpleNamespace(response_id=rid, conversation_id="conv_" + rid)
        result = [e async for e in server._handle_response(None, ctx, asyncio.Event())]
        assert PLATFORM_BINDING.get() is None
        return result
    async def run():
        return await asyncio.gather(collect("response_a"), collect("response_b"))
    assert asyncio.run(run()) == [[{"response_id":"response_a", "conversation_id":"conv_response_a"}],
                                 [{"response_id":"response_b", "conversation_id":"conv_response_b"}]]
