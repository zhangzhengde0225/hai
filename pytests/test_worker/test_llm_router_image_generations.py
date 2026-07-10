from types import SimpleNamespace

import pytest

from hepai.components.haiddf.worker.routers import llm_router


class FakeParentApp:
    def __init__(self):
        self.calls = []

    async def worker_unified_gate(self, function_params, model, function):
        self.calls.append(
            {
                "function_params": function_params,
                "model": model,
                "function": function,
            }
        )
        return {"ok": True, "kwargs": function_params.kwargs}


@pytest.mark.asyncio
async def test_image_generations_routes_through_parent_app_without_worker_auth(monkeypatch):
    async def fake_read_request_body(request):
        return {
            "model": "openai/gpt-image-1",
            "prompt": "draw a detector",
        }

    monkeypatch.setattr(llm_router, "read_request_body", fake_read_request_body)

    parent_app = FakeParentApp()
    router_group = llm_router.LLMRouterGroup(parent_app=parent_app)

    result = await router_group.image_generations(SimpleNamespace())

    assert result["ok"] is True
    assert len(parent_app.calls) == 1
    call = parent_app.calls[0]
    assert call["model"] == "openai/gpt-image-1"
    assert call["function"] == "image_generations"
    assert call["function_params"].args == []
    assert call["function_params"].kwargs["size"] == "auto"
    assert call["function_params"].kwargs["quality"] == "auto"
    assert call["function_params"].kwargs["response_format"] == "url"
