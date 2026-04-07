import asyncio
import time
from typing import List, Union

from hepai.components.haiddf.base_class._llm_remote_model_v2 import LLMRemoteModelV2 as LLMRemoteModel


_TEST_MESSAGES = [{"role": "user", "content": "Hi, reply with one word only."}]
_TEST_MAX_TOKENS = 16


class LLMConenctivityEvaluator:

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def run(self, models: Union[LLMRemoteModel, List[LLMRemoteModel]]) -> List[dict]:
        """测试模型列表的连通性，返回每个模型的测试结果列表。

        每条结果格式：
            {"name": str, "engine": str, "api_mode": str, "ok": bool, "latency": float, "error": str}
        """
        if isinstance(models, LLMRemoteModel):
            models = [models]

        results = []
        for model in models:
            result = asyncio.run(self._test_one(model))
            results.append(result)
            status = "✅" if result["ok"] else "❌"
            latency = f"{result['latency']:.2f}s" if result["ok"] else result["error"]
            print(f"{status} [{result['api_mode']}] {result['name']}  {latency}")

        ok_count = sum(1 for r in results if r["ok"])
        print(f"\n{ok_count}/{len(results)} models passed.")
        return results

    async def _test_one(self, model: LLMRemoteModel) -> dict:
        api_mode = getattr(model.cfg, "api_mode")
        base = {"name": model.cfg.name, "engine": model.cfg.engine, "api_mode": api_mode,
                "ok": False, "latency": 0.0, "error": ""}
        t0 = time.perf_counter()
        try:
            coro = self._dispatch(model, api_mode)
            await asyncio.wait_for(coro, timeout=self.timeout)
            base["latency"] = time.perf_counter() - t0
            base["ok"] = True
        except asyncio.TimeoutError:
            base["error"] = f"timeout ({self.timeout}s)"
        except Exception as e:
            base["error"] = str(e)
        return base

    async def _dispatch(self, model: LLMRemoteModel, api_mode: str):
        if api_mode == "openai-completions":
            await self._chat_completions(model)
        elif api_mode == "openai-responses":
            await self._responses(model)
        elif api_mode == "anthropic-messages":
            await self._anthropic_messages(model)
        else:
            raise ValueError(f"Unsupported api_mode: {api_mode!r}")

    async def _chat_completions(self, model: LLMRemoteModel):
        result = await model.chat_completions(
            messages=_TEST_MESSAGES,
            max_tokens=_TEST_MAX_TOKENS,
            stream=False,
        )
        assert isinstance(result, dict), f"Unexpected response type: {type(result)}"

    async def _responses(self, model: LLMRemoteModel):
        result = await model.responses(
            input=_TEST_MESSAGES,
            max_output_tokens=_TEST_MAX_TOKENS,
            stream=False,
        )
        assert isinstance(result, dict), f"Unexpected response type: {type(result)}"

    async def _anthropic_messages(self, model: LLMRemoteModel):
        result = await model.anthropic_messages(
            model=model.cfg.engine,
            messages=_TEST_MESSAGES,
            max_tokens=_TEST_MAX_TOKENS,
            stream=False,
        )
        assert isinstance(result, dict), f"Unexpected response type: {type(result)}"
