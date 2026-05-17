"""
WorkerConfigManager — worker_config.json 的持久化配置管理器。

配置文件统一存放在 ~/.hepai/worker_configs/{worker_id}.json，
无需手动指定路径，天然支持同机多 worker 共存。

首次启动时若目标文件不存在，自动从同目录的 worker_config.json 模板复制初始化。
所有写操作线程安全，写后自动更新 metadata.lastTouchedAt。

JSON 顶层字段：metadata（旧名 meta）、worker、model（旧名 models）。
旧文件加载时会自动迁移并回写。
"""

import json
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# 默认配置根目录
DEFAULT_CONFIG_DIR = Path.home() / ".hepai" / "worker_configs"

# 本文件所在目录（用于定位本地模板）
_HERE = Path(__file__).parent

# 顶层字段名
_KEY_METADATA = "metadata"
_KEY_MODEL = "model"
# 旧字段名（用于一次性迁移）
_LEGACY_KEY_METADATA = "meta"
_LEGACY_KEY_MODEL = "models"


class WorkerConfigManager:
    """
    管理 ~/.hepai/worker_configs/{worker_id}.json 的读写。

    用法示例::

        mgr = WorkerConfigManager("openrouter")

        # 查询
        mgr.list_models()
        mgr.get_model("openai/gpt-4o")

        # 新增
        mgr.add_model("openrouter", {"id": "openai/gpt-4o", "engine": "openai/gpt-4o"})

        # 修改
        mgr.update_model("openai/gpt-4o", {"maxTokens": 65536})

        # 删除
        mgr.remove_model("openai/gpt-4o")

        # 热重载（外部手动改过 JSON 后调用）
        mgr.reload()
    """

    def __init__(self, worker_id: str, config_dir: str = None):
        self.worker_id = worker_id
        self.config_dir = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
        self.config_path = self.config_dir / f"{worker_id}_worker.json"
        self._lock = threading.Lock()
        self._config: Dict = {}
        self._ensure_config()
        self.reload()

    # ── 初始化 ────────────────────────────────────────────────────────────

    def _ensure_config(self) -> None:
        """确保配置目录和文件存在；首次运行时从本地模板自动初始化。"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 迁移旧命名（{worker_id}.json → {worker_id}_worker.json）
        old_path = self.config_dir / f"{self.worker_id}.json"
        if old_path.exists() and not self.config_path.exists():
            old_path.rename(self.config_path)
            print(
                f"[WorkerConfigManager] 迁移配置文件: {old_path.name} → {self.config_path.name}",
                flush=True,
            )

        if self.config_path.exists():
            return

        local_template = _HERE / "worker_config.json"
        if local_template.exists():
            shutil.copy(local_template, self.config_path)
            print(
                f"[WorkerConfigManager] 初始化配置: {local_template} → {self.config_path}",
                flush=True,
            )
        else:
            # 本地无模板，创建空骨架
            skeleton = {
                _KEY_METADATA: {"version": "2.2"},
                "worker": {},
                _KEY_MODEL: {"providers": {}},
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(skeleton, f, indent=2, ensure_ascii=False)
            print(
                f"[WorkerConfigManager] 创建空配置: {self.config_path}",
                flush=True,
            )

    # ── 文件 I/O ──────────────────────────────────────────────────────────

    def reload(self) -> None:
        """从磁盘重新加载配置（覆盖内存中的状态），并迁移旧字段名。"""
        with self._lock:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            if self._migrate_legacy_keys():
                # 旧字段名 → 新字段名，回写磁盘
                self._save()

    def _migrate_legacy_keys(self) -> bool:
        """把顶层 meta→metadata、models→model 就地改名。返回是否发生迁移。"""
        migrated = False
        if _LEGACY_KEY_METADATA in self._config and _KEY_METADATA not in self._config:
            self._config[_KEY_METADATA] = self._config.pop(_LEGACY_KEY_METADATA)
            migrated = True
        elif _LEGACY_KEY_METADATA in self._config and _KEY_METADATA in self._config:
            # 同时存在：丢弃旧的，保留新的
            self._config.pop(_LEGACY_KEY_METADATA)
            migrated = True
        if _LEGACY_KEY_MODEL in self._config and _KEY_MODEL not in self._config:
            self._config[_KEY_MODEL] = self._config.pop(_LEGACY_KEY_MODEL)
            migrated = True
        elif _LEGACY_KEY_MODEL in self._config and _KEY_MODEL in self._config:
            self._config.pop(_LEGACY_KEY_MODEL)
            migrated = True
        if migrated:
            print(
                f"[WorkerConfigManager] 迁移旧字段名 → metadata/model: {self.config_path}",
                flush=True,
            )
        return migrated

    def _save(self) -> None:
        """将内存配置写回磁盘，并更新 metadata.lastTouchedAt。
        调用前必须已持有 self._lock。
        """
        metadata = self._config.setdefault(_KEY_METADATA, {})
        metadata["lastTouchedAt"] = (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        )
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    # ── 内部属性 ──────────────────────────────────────────────────────────

    @property
    def _providers(self) -> Dict:
        return self._config.get(_KEY_MODEL, {}).get("providers", {})

    # ── 只读查询 ──────────────────────────────────────────────────────────

    @property
    def config(self) -> Dict:
        """返回当前内存中的完整配置（只读参考，勿直接修改）。"""
        return self._config

    def get_provider(self, provider_name: str) -> Optional[Dict]:
        """返回指定 provider 的配置，不存在时返回 None。"""
        return self._providers.get(provider_name)

    def list_providers(self) -> List[str]:
        """返回所有 provider 名称列表。"""
        return list(self._providers.keys())

    def list_models(self, provider_name: str = None) -> List[Dict]:
        """
        返回所有模型列表，每条记录附加 ``_provider`` 字段。

        :param provider_name: 若指定，则只返回该 provider 下的模型。
        """
        result = []
        for pname, provider in self._providers.items():
            if provider_name and pname != provider_name:
                continue
            for m in provider.get("models", []):
                result.append({"_provider": pname, **m})
        return result

    def get_model(self, model_id: str, provider_name: str = None) -> Optional[Dict]:
        """
        按 id 查找模型，找不到返回 None。

        :param model_id:      模型的 id 或 name 字段值。
        :param provider_name: 若指定，则只在该 provider 下查找。
        """
        for m in self.list_models(provider_name):
            if (m.get("id") or m.get("name")) == model_id:
                return m
        return None

    # ── Provider 写操作 ───────────────────────────────────────────────────

    def add_provider(self, provider_name: str, provider_config: Dict) -> None:
        """
        新增一个 provider。

        :param provider_name:   provider 唯一标识，如 ``"openrouter"``。
        :param provider_config: provider 配置字典，示例::

            {
                "baseUrl": "https://openrouter.ai/api/",
                "apiKey":  "os.environ/OPENROUTER_API_KEY",
                "api":     "openai-completions",
                "models":  []
            }

        :raises ValueError: 若 provider 已存在。
        """
        with self._lock:
            providers = self._config.setdefault(_KEY_MODEL, {}).setdefault("providers", {})
            if provider_name in providers:
                raise ValueError(f"Provider '{provider_name}' already exists")
            providers[provider_name] = provider_config
            self._save()

    def remove_provider(self, provider_name: str) -> None:
        """
        删除指定 provider 及其下所有模型。

        :raises KeyError: 若 provider 不存在。
        """
        with self._lock:
            if provider_name not in self._providers:
                raise KeyError(f"Provider '{provider_name}' not found")
            del self._providers[provider_name]
            self._save()

    def update_provider(self, provider_name: str, updates: Dict) -> None:
        """
        更新 provider 的顶层字段（浅合并，不影响 models 列表）。

        :raises KeyError: 若 provider 不存在。
        """
        with self._lock:
            if provider_name not in self._providers:
                raise KeyError(f"Provider '{provider_name}' not found")
            self._providers[provider_name].update(updates)
            self._save()

    # ── Model 写操作 ──────────────────────────────────────────────────────

    def add_model(self, provider_name: str, model_info: Dict) -> None:
        """
        向指定 provider 追加一个模型。

        :param provider_name: 目标 provider 名称，必须已存在。
        :param model_info:    模型配置字典，必须包含 ``id`` 或 ``name`` 字段。示例::

            {
                "id":            "openai/gpt-4o",
                "engine":        "openai/gpt-4o",
                "contextWindow": 128000,
                "maxTokens":     16384
            }

        :raises KeyError:   若 provider 不存在。
        :raises ValueError: 若该 provider 下已有同 id 的模型。
        """
        with self._lock:
            providers = self._config.setdefault(_KEY_MODEL, {}).setdefault("providers", {})
            if provider_name not in providers:
                raise KeyError(
                    f"Provider '{provider_name}' not found, use add_provider() first"
                )
            models: List[Dict] = providers[provider_name].setdefault("models", [])
            model_id = model_info.get("id") or model_info.get("name")
            if any((m.get("id") or m.get("name")) == model_id for m in models):
                raise ValueError(
                    f"Model '{model_id}' already exists in provider '{provider_name}'"
                )
            models.append(model_info)
            self._save()

    def remove_model(self, model_id: str, provider_name: str = None) -> bool:
        """
        删除指定模型。

        :param model_id:      要删除的模型 id 或 name。
        :param provider_name: 若指定，则只在该 provider 下查找删除。
        :returns: ``True`` 表示成功删除，``False`` 表示未找到。
        """
        with self._lock:
            for pname, provider in self._providers.items():
                if provider_name and pname != provider_name:
                    continue
                models: List[Dict] = provider.get("models", [])
                new_models = [
                    m for m in models if (m.get("id") or m.get("name")) != model_id
                ]
                if len(new_models) < len(models):
                    provider["models"] = new_models
                    self._save()
                    return True
        return False

    def update_model(
        self, model_id: str, updates: Dict, provider_name: str = None
    ) -> bool:
        """
        更新指定模型的字段（浅合并）。

        :param model_id:      目标模型 id 或 name。
        :param updates:       要合并的字段字典。
        :param provider_name: 若指定，则只在该 provider 下查找。
        :returns: ``True`` 表示成功更新，``False`` 表示未找到。
        """
        with self._lock:
            for pname, provider in self._providers.items():
                if provider_name and pname != provider_name:
                    continue
                for m in provider.get("models", []):
                    if (m.get("id") or m.get("name")) == model_id:
                        m.update(updates)
                        self._save()
                        return True
        return False

    # ── 便捷方法 ──────────────────────────────────────────────────────────

    def set_model_proxy(self, model_id: str, proxy: Optional[str]) -> bool:
        """快捷设置（或清除）某个模型的 proxy。"""
        return self.update_model(model_id, {"proxy": proxy})

    def set_provider_api_key(self, provider_name: str, api_key: str) -> None:
        """快捷更新 provider 的 apiKey。"""
        self.update_provider(provider_name, {"apiKey": api_key})

    def get_secret_key(self) -> Optional[str]:
        """读取持久化的 worker secret key，不存在时返回 None。"""
        return self._config.get(_KEY_METADATA, {}).get("secret_key")

    def set_secret_key(self, key: str) -> None:
        """将 worker secret key 写入 metadata.secret_key 并持久化。"""
        with self._lock:
            self._config.setdefault(_KEY_METADATA, {})["secret_key"] = key
            self._save()

    def get_admin_key(self) -> Optional[str]:
        """读取持久化的 admin key，不存在时返回 None。"""
        return self._config.get(_KEY_METADATA, {}).get("admin_key")

    def set_admin_key(self, key: str) -> None:
        """将 admin key 写入 metadata.admin_key 并持久化。"""
        with self._lock:
            self._config.setdefault(_KEY_METADATA, {})["admin_key"] = key
            self._save()

    def get_metadata(self) -> Dict:
        """返回 metadata 整段（包含 version、lastTouchedAt、secret_key、admin_key 等）。"""
        return dict(self._config.get(_KEY_METADATA, {}))

    def get_version(self) -> Optional[str]:
        """读取 metadata.version。"""
        return self._config.get(_KEY_METADATA, {}).get("version")

    def get_worker_config(self) -> Optional[Dict]:
        """读取持久化的 worker 配置，为空 dict 或不存在时返回 None。"""
        w = self._config.get("worker")
        return w if w else None

    def set_worker_config(self, config: Dict) -> None:
        """将 worker 配置写入 worker 字段并持久化（浅合并）。"""
        with self._lock:
            existing = self._config.setdefault("worker", {})
            existing.update(config)
            self._save()

    def __repr__(self) -> str:
        n_providers = len(self._providers)
        n_models = sum(len(p.get("models", [])) for p in self._providers.values())
        return (
            f"<WorkerConfigManager worker_id={self.worker_id!r} "
            f"path={self.config_path} "
            f"providers={n_providers} models={n_models}>"
        )
