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
        rt.post("/models/{model_name}/enable", dependencies=[admin_auth])(self.enable_model)
        rt.post("/models/{model_name}/disable", dependencies=[admin_auth])(self.disable_model)
        rt.post("/models/batch_update", dependencies=[admin_auth])(self.batch_update_models)
        rt.get("/models/status", dependencies=[admin_auth])(self.get_all_status)

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
        manager = self.parent_app.worker.model_status_manager
        grouped = manager.get_models_by_provider()

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
        manager = self.parent_app.worker.model_status_manager

        # 检查模型是否存在
        if model_name not in self.parent_app.worker._model_map:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_name}' not found"
            )

        # 启用模型
        manager.set_model_status(model_name, enabled=True)

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
        manager = self.parent_app.worker.model_status_manager

        # 检查模型是否存在
        if model_name not in self.parent_app.worker._model_map:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_name}' not found"
            )

        # 禁用模型
        manager.set_model_status(model_name, enabled=False)

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

        manager = self.parent_app.worker.model_status_manager
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
            if model_name not in self.parent_app.worker._model_map:
                results.append({
                    "model_name": model_name,
                    "success": False,
                    "error": f"Model '{model_name}' not found"
                })
                continue

            # 更新状态
            try:
                manager.set_model_status(model_name, enabled)
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
        manager = self.parent_app.worker.model_status_manager
        all_status = manager.get_all_model_status()

        return {
            "success": True,
            "models": all_status,
            "timestamp": time.time()
        }
