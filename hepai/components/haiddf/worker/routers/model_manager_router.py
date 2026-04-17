"""
模型管理路由组
提供模型启用/禁用的 API 端点
"""
import os
import time
from typing import List, Callable, Dict
from dataclasses import field, dataclass
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from ..worker_app import HWorkerAPP
from ..utils import read_request_body
from ..singletons import authorizer

# 管理员认证依赖
admin_auth: Callable = Depends(authorizer.admin_auth)


@dataclass
class ModelManagerRouterGroup:
    """模型管理路由组"""
    name: str = "model_manager"
    prefix: str = "/apiv2"
    tags: List[str] = field(default_factory=lambda: ["model_manager"])
    router: APIRouter = field(default_factory=APIRouter)
    parent_app: HWorkerAPP = None  # type: ignore

    def __post_init__(self):
        """初始化路由"""
        rt = self.router

        # Dashboard 页面（无需认证，认证在前端完成）
        rt.get("/dashboard")(self.dashboard_page)

        # API 端点（需要管理员认证）
        rt.get("/models/grouped", dependencies=[admin_auth])(self.list_models_grouped)
        rt.get("/models/configs", dependencies=[admin_auth])(self.get_model_configs)
        rt.put("/models/config", dependencies=[admin_auth])(self.update_model_config)
        rt.post("/models/{model_name}/enable", dependencies=[admin_auth])(self.enable_model)
        rt.post("/models/{model_name}/disable", dependencies=[admin_auth])(self.disable_model)
        rt.post("/models/batch_update", dependencies=[admin_auth])(self.batch_update_models)
        rt.get("/models/status", dependencies=[admin_auth])(self.get_all_status)
        rt.put("/worker/config", dependencies=[admin_auth])(self.update_worker_config)
        rt.get("/providers/configs", dependencies=[admin_auth])(self.get_provider_configs)
        rt.put("/providers/config", dependencies=[admin_auth])(self.update_provider_config)
        rt.post("/models/model", dependencies=[admin_auth])(self.add_model)
        rt.delete("/models/model", dependencies=[admin_auth])(self.delete_model)

    def _sync_model_cfg(self, model_id: str, updates: Dict) -> None:
        """将 JSON 更新同步到内存中对应 LLMRemoteModelV2 的 cfg 字段。"""
        model_obj = self.parent_app.worker._model_map.get(model_id)
        if model_obj is None or not hasattr(model_obj, 'cfg'):
            return
        cfg = model_obj.cfg
        need_reset = False
        for k, v in updates.items():
            if k == 'engine':
                cfg.engine = v or model_id
                model_obj.engine = cfg.engine
            elif k == 'proxy':
                cfg.proxy = v  # None/null 清除代理
                need_reset = True
            elif k == 'api':
                if v is not None:
                    api_raw = v
                    cfg.api_mode = api_raw[0] if isinstance(api_raw, list) else api_raw
            elif k == 'appendAnthropicPath':
                if v is not None:
                    cfg.append_anthropic_path = bool(v)
                    need_reset = True
            elif k == 'endpoint_version':
                if v is not None:
                    cfg.version = v
        if need_reset:
            model_obj._http_client = None
            model_obj._anthropic_http_client = None

    def _sync_provider_cfg(self, provider_name: str, updates: Dict, cfg_mgr) -> None:
        """将 provider JSON 更新同步到该 provider 下所有内存模型的 cfg 字段。"""
        provider_cfg = cfg_mgr.config.get("models", {}).get("providers", {}).get(provider_name, {})

        # 解析 provider 级别的最新值
        new_base_url = provider_cfg.get("baseUrl", "")
        new_api_key_raw = provider_cfg.get("apiKey", "")
        new_need_external = provider_cfg.get("needExternalApiKey", False)
        new_provider_proxy = provider_cfg.get("proxy", None)
        new_provider_api_raw = provider_cfg.get("api", "openai-completions")
        new_provider_api_mode = new_provider_api_raw[0] if isinstance(new_provider_api_raw, list) else new_provider_api_raw
        new_provider_append = provider_cfg.get("appendAnthropicPath", True)

        # 解析 apiKey 中的环境变量
        if isinstance(new_api_key_raw, str) and new_api_key_raw.startswith("os.environ/"):
            new_api_key = os.environ.get(new_api_key_raw.split("/")[1], "")
        else:
            new_api_key = new_api_key_raw or ""

        for model_obj in self.parent_app.worker.models:
            if not hasattr(model_obj, 'cfg') or model_obj.cfg.provider != provider_name:
                continue
            model_id = model_obj.name
            # 获取该模型的 JSON 条目，用于判断模型级别是否有覆盖
            model_entry = next(
                (m for m in provider_cfg.get("models", []) if (m.get("id") or m.get("name")) == model_id),
                {}
            )
            cfg = model_obj.cfg
            need_reset = False

            if 'baseUrl' in updates:
                cfg.base_url = new_base_url
                need_reset = True

            if 'apiKey' in updates:
                cfg._api_key = new_api_key

            if 'needExternalApiKey' in updates:
                cfg.need_external_api_key = new_need_external

            # proxy / api / appendAnthropicPath：模型级别有值时不覆盖
            if 'proxy' in updates and 'proxy' not in model_entry:
                cfg.proxy = new_provider_proxy
                need_reset = True

            if 'api' in updates and 'api' not in model_entry:
                cfg.api_mode = new_provider_api_mode

            if 'appendAnthropicPath' in updates and 'appendAnthropicPath' not in model_entry:
                cfg.append_anthropic_path = new_provider_append
                need_reset = True

            if need_reset:
                model_obj._http_client = None
                model_obj._anthropic_http_client = None

    async def dashboard_page(self):
        """返回 Dashboard HTML 页面"""
        html_file = os.path.join(os.path.dirname(__file__), "../html", "dashboard.html")
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load dashboard page: {e}"
            )

    async def get_model_configs(self):
        """
        返回所有模型的完整配置字段（来自 JSON）+ enabled 状态

        Returns:
            {
                "success": True,
                "data": {
                    "openrouter": [
                        { "id": "openai/gpt-5.4", "engine": "...", "enabled": True, ... }
                    ]
                }
            }
        """
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr is None:
            raise HTTPException(status_code=503, detail="Config manager not available")

        enabled_map = self.parent_app.worker._enabled_models

        providers = cfg_mgr.config.get("models", {}).get("providers", {})
        data: Dict = {}
        for provider_name, provider in providers.items():
            models = []
            for m in provider.get("models", []):
                model_id = m.get("id") or m.get("name", "")
                entry = dict(m)
                entry["enabled"] = enabled_map.get(model_id, True)
                models.append(entry)
            data[provider_name] = models

        return {"success": True, "data": data, "timestamp": time.time()}

    async def update_model_config(self, request: Request):
        """
        更新模型的配置字段（写回 JSON）并可选更新 enabled 状态

        Request Body:
            { "model_id": "openai/gpt-5.4", "updates": { ...任意字段..., "enabled"?: bool } }
        """
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr is None:
            raise HTTPException(status_code=503, detail="Config manager not available")

        body = await read_request_body(request)
        model_id = body.get("model_id")
        updates = body.get("updates", {})

        if not model_id:
            raise HTTPException(status_code=400, detail="model_id is required")

        enabled = updates.pop("enabled", None)

        if updates:
            ok = cfg_mgr.update_model(model_id, updates)
            if not ok:
                raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found in config")

        if enabled is not None:
            self.parent_app.worker.set_model_enabled(model_id, bool(enabled))
            if cfg_mgr:
                cfg_mgr.update_model(model_id, {"enabled": bool(enabled)})

        # Sync config changes to in-memory model object
        if updates:
            self._sync_model_cfg(model_id, updates)

        return {"success": True, "model_id": model_id}

    async def list_models_grouped(self):
        """
        按提供者分组返回所有模型及状态

        Returns:
            {
                "success": True,
                "data": {
                    "hepai": [{"name": "hepai/gpt-4", "enabled": True}, ...],
                    "Uncategorized": [{"name": "local-llama", "enabled": False}, ...]
                },
                "timestamp": 1703001234.567
            }
        """
        worker = self.parent_app.worker
        grouped: Dict = {}
        for model in worker.models:
            provider = model.name.split("/")[0] if "/" in model.name else "Uncategorized"
            grouped.setdefault(provider, []).append({
                "name": model.name,
                "enabled": worker.is_model_enabled(model.name),
            })

        return {
            "success": True,
            "data": grouped,
            "timestamp": time.time()
        }

    async def enable_model(self, model_name: str):
        """
        启用指定模型

        Args:
            model_name: 模型名称

        Returns:
            {
                "success": True,
                "message": "Model xxx enabled",
                "model_name": "xxx",
                "enabled": True
            }
        """
        # 检查模型是否存在
        if model_name not in self.parent_app.worker._model_map:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_name}' not found"
            )

        self.parent_app.worker.set_model_enabled(model_name, True)
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr:
            cfg_mgr.update_model(model_name, {"enabled": True})

        return {
            "success": True,
            "message": f"Model '{model_name}' enabled",
            "model_name": model_name,
            "enabled": True
        }

    async def disable_model(self, model_name: str):
        """
        禁用指定模型

        注意：正在处理的请求会完成，排队中的请求会在获取信号量后被拒绝

        Args:
            model_name: 模型名称

        Returns:
            {
                "success": True,
                "message": "Model xxx disabled",
                "model_name": "xxx",
                "enabled": False,
                "note": "..."
            }
        """
        # 检查模型是否存在
        if model_name not in self.parent_app.worker._model_map:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_name}' not found"
            )

        self.parent_app.worker.set_model_enabled(model_name, False)
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr:
            cfg_mgr.update_model(model_name, {"enabled": False})

        return {
            "success": True,
            "message": f"Model '{model_name}' disabled",
            "model_name": model_name,
            "enabled": False,
            "note": "In-progress requests will complete, queued requests will be rejected"
        }

    async def batch_update_models(self, request: Request):
        """
        批量更新多个模型的状态

        Request Body:
            {
                "updates": [
                    {"model_name": "xxx", "enabled": true},
                    {"model_name": "yyy", "enabled": false},
                    ...
                ]
            }

        Returns:
            {
                "success": True,
                "results": [
                    {"model_name": "xxx", "enabled": true, "success": True},
                    {"model_name": "yyy", "enabled": false, "success": True}
                ],
                "count": 2
            }
        """
        body = await read_request_body(request)
        updates = body.get("updates", [])

        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No updates provided"
            )

        worker = self.parent_app.worker
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        results = []

        for update in updates:
            model_name = update.get("model_name")
            enabled = update.get("enabled")

            if not model_name:
                results.append({
                    "model_name": model_name,
                    "success": False,
                    "error": "model_name is required"
                })
                continue

            if enabled is None:
                results.append({
                    "model_name": model_name,
                    "success": False,
                    "error": "enabled is required"
                })
                continue

            # 检查模型是否存在
            if model_name not in worker._model_map:
                results.append({
                    "model_name": model_name,
                    "success": False,
                    "error": f"Model '{model_name}' not found"
                })
                continue

            # 更新状态
            try:
                worker.set_model_enabled(model_name, enabled)
                if cfg_mgr:
                    cfg_mgr.update_model(model_name, {"enabled": enabled})
                results.append({
                    "model_name": model_name,
                    "enabled": enabled,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "model_name": model_name,
                    "success": False,
                    "error": str(e)
                })

        # 如果 worker 已注册到 controller，发送一次心跳更新状态
        worker = self.parent_app.worker
        if not worker.config.no_register:
            try:
                # 在后台线程中发送心跳，避免阻塞响应
                import asyncio
                loop = asyncio.get_event_loop()
                loop.run_in_executor(None, worker.register_to_controller, True)

                if hasattr(worker, 'logger'):
                    worker.logger.info("Model status updated, heartbeat sent to controller")
            except Exception as e:
                if hasattr(worker, 'logger'):
                    worker.logger.warning(f"Failed to send heartbeat after model status update: {e}")

        return {
            "success": True,
            "results": results,
            "count": len(results)
        }

    async def get_all_status(self):
        """
        获取所有模型的状态（用于验证密码）

        Returns:
            {
                "success": True,
                "models": {
                    "hepai/gpt-4": True,
                    "local-llama": False,
                    ...
                },
                "timestamp": 1703001234.567
            }
        """
        return {
            "success": True,
            "models": dict(self.parent_app.worker._enabled_models),
            "timestamp": time.time()
        }

    async def update_worker_config(self, request: Request):
        """
        更新 worker 运行时配置并持久化到 JSON。

        可更新字段：description, limit_model_concurrency, is_free, debug, permissions
        注意：limit_model_concurrency 修改需重启才对并发信号量生效。

        Request Body:
            { "updates": { "description": "...", "is_free": false, ... } }
        """
        _ALLOWED = {"description", "limit_model_concurrency", "is_free", "debug", "permissions"}

        body = await read_request_body(request)
        updates: Dict = body.get("updates", {})
        updates = {k: v for k, v in updates.items() if k in _ALLOWED}

        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        worker = self.parent_app.worker
        worker_config = worker.config
        for k, v in updates.items():
            if hasattr(worker_config, k):
                setattr(worker_config, k, v)
            if k == 'permissions':
                worker.worker_permissions = worker._parse_permissions(v)

        # 持久化到 JSON
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr:
            cfg_mgr.set_worker_config(updates)

        return {"success": True, "updated": list(updates.keys())}

    async def get_provider_configs(self):
        """返回所有 provider 的顶层配置（不含 models 列表）"""
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr is None:
            raise HTTPException(status_code=503, detail="Config manager not available")

        providers = cfg_mgr.config.get("models", {}).get("providers", {})
        data = {
            name: {k: v for k, v in provider.items() if k != "models"}
            for name, provider in providers.items()
        }
        return {"success": True, "data": data, "timestamp": time.time()}

    async def update_provider_config(self, request: Request):
        """
        更新指定 provider 的顶层配置（浅合并，不影响 models 列表）。

        Request Body:
            { "provider_name": "openrouter", "updates": { "proxy": "...", ... } }
        """
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr is None:
            raise HTTPException(status_code=503, detail="Config manager not available")

        body = await read_request_body(request)
        provider_name = body.get("provider_name")
        updates: Dict = {k: v for k, v in body.get("updates", {}).items() if k != "models"}

        if not provider_name:
            raise HTTPException(status_code=400, detail="provider_name is required")
        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        try:
            cfg_mgr.update_provider(provider_name, updates)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

        # Sync provider config changes to all in-memory models of this provider
        self._sync_provider_cfg(provider_name, updates, cfg_mgr)

        return {"success": True, "provider_name": provider_name, "updated": list(updates.keys())}

    async def add_model(self, request: Request):
        """
        向指定 provider 添加新模型，同时注册到内存。

        Request Body:
            { "provider_name": "openrouter", "model": { "id": "...", "engine": "...", ... } }
        """
        import asyncio
        from hepai.components.haiddf.base_class._llm_remote_model_v2 import (
            LLMRemoteModelV2, LLMModelConfig,
        )

        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr is None:
            raise HTTPException(status_code=503, detail="Config manager not available")

        body = await read_request_body(request)
        provider_name = body.get("provider_name")
        model_info: Dict = body.get("model", {})
        model_id = model_info.get("id") or model_info.get("name")

        if not provider_name:
            raise HTTPException(status_code=400, detail="provider_name is required")
        if not model_id:
            raise HTTPException(status_code=400, detail="model id is required")

        # 写入 JSON
        try:
            cfg_mgr.add_model(provider_name, model_info)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

        # 构建内存对象（与 from_config 逻辑一致）
        provider_cfg = cfg_mgr.config.get("models", {}).get("providers", {}).get(provider_name, {})
        base_url = provider_cfg.get("baseUrl", "")
        api_key_raw = provider_cfg.get("apiKey", "")
        need_external = provider_cfg.get("needExternalApiKey", False)
        provider_proxy = provider_cfg.get("proxy", None)
        provider_api_raw = provider_cfg.get("api", "openai-completions")
        provider_api_mode = provider_api_raw[0] if isinstance(provider_api_raw, list) else provider_api_raw
        provider_append = provider_cfg.get("appendAnthropicPath", True)

        # 解析 apiKey 环境变量
        if isinstance(api_key_raw, str) and api_key_raw.startswith("os.environ/"):
            api_key = os.environ.get(api_key_raw.split("/")[1], "")
        else:
            api_key = api_key_raw or ""

        engine = model_info.get("engine") or model_id
        name = model_info.get("name") or model_id
        proxy = model_info.get("proxy", provider_proxy)
        api_raw = model_info.get("api", provider_api_mode)
        api_mode = api_raw[0] if isinstance(api_raw, list) else api_raw
        append = model_info.get("appendAnthropicPath", provider_append)

        model_cfg = LLMModelConfig(
            name=name,
            engine=engine,
            base_url=base_url,
            _api_key=api_key,
            provider=provider_name,
            api_mode=api_mode,
            proxy=proxy,
            need_external_api_key=need_external,
            append_anthropic_path=append,
        )
        model_cfg._api_key = api_key  # __post_init__ 可能已处理，再次确保已解析

        new_model = LLMRemoteModelV2(config=model_cfg)

        # 注册到内存
        worker = self.parent_app.worker
        app = self.parent_app
        enabled = model_info.get("enabled", True)

        worker.models.append(new_model)
        worker._model_map[model_id] = new_model
        worker._enabled_models[model_id] = bool(enabled)
        app.model_semaphores[model_id] = asyncio.Semaphore(app.limit_model_concurrency)
        app._model_lookup_cache[model_id] = len(worker.models) - 1

        return {"success": True, "model_id": model_id, "provider_name": provider_name}

    async def delete_model(self, request: Request):
        """
        从指定 provider 删除模型，同时从内存中注销。

        Request Body:
            { "model_id": "openai/gpt-5", "provider_name": "openrouter" }
        """
        cfg_mgr = getattr(self.parent_app.state, 'cfg_mgr', None)
        if cfg_mgr is None:
            raise HTTPException(status_code=503, detail="Config manager not available")

        body = await read_request_body(request)
        model_id = body.get("model_id")
        provider_name = body.get("provider_name")

        if not model_id:
            raise HTTPException(status_code=400, detail="model_id is required")

        # 从 JSON 删除
        removed = cfg_mgr.remove_model(model_id, provider_name)
        if not removed:
            raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

        # 从内存注销
        worker = self.parent_app.worker
        app = self.parent_app
        worker.models = [m for m in worker.models if m.name != model_id]
        worker._model_map.pop(model_id, None)
        worker._enabled_models.pop(model_id, None)
        app.model_semaphores.pop(model_id, None)
        app._model_lookup_cache.pop(model_id, None)
        # 重建 lookup cache 索引
        app._model_lookup_cache = {m.name: i for i, m in enumerate(worker.models)}

        return {"success": True, "model_id": model_id}
