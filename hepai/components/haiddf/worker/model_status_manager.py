"""
模型状态管理器
负责管理模型的启用/禁用状态，并持久化到 YAML 文件
"""
import os
import time
import yaml
import threading
from typing import Dict, List, TYPE_CHECKING
from dataclasses import dataclass, field, asdict

if TYPE_CHECKING:
    from ._worker_class import CommonWorker


@dataclass
class ModelStatusConfig:
    """单个模型的状态配置"""
    model_name: str
    enabled: bool = True
    provider: str = "Uncategorized"
    last_updated: float = field(default_factory=lambda: time.time())


class ModelStatusManager:
    """
    模型状态管理器

    功能：
    - 管理模型的启用/禁用状态
    - 持久化状态到 YAML 文件
    - 按提供者分组模型
    - 线程安全的状态读写
    """

    def __init__(self, worker: 'CommonWorker', config_file: str):
        """
        初始化模型状态管理器

        Args:
            worker: CommonWorker 实例
            config_file: 配置文件路径（model_config.yaml）
        """
        self.worker = worker
        self.config_file = config_file
        self._model_status: Dict[str, bool] = {}  # 内存缓存 {model_name: enabled}
        self._lock = threading.Lock()  # 线程锁

        # 加载或创建配置文件
        self._load_or_create_config()

    def is_model_enabled(self, model_name: str) -> bool:
        """
        检查模型是否启用

        Args:
            model_name: 模型名称

        Returns:
            bool: True 表示启用，False 表示禁用
        """
        with self._lock:
            return self._model_status.get(model_name, True)  # 默认启用

    def set_model_status(self, model_name: str, enabled: bool):
        """
        设置模型状态并持久化到文件

        Args:
            model_name: 模型名称
            enabled: True 启用，False 禁用
        """
        with self._lock:
            old_status = self._model_status.get(model_name)
            self._model_status[model_name] = enabled

            # 记录日志
            if hasattr(self.worker, 'logger'):
                action = "enabled" if enabled else "disabled"
                self.worker.logger.info(
                    f"Model '{model_name}' has been {action} "
                    f"(previous status: {old_status})"
                )

            # 持久化到文件
            self._save_config()

    def get_models_by_provider(self) -> Dict[str, List[Dict]]:
        """
        按提供者分组模型

        Returns:
            Dict[str, List[Dict]]: {
                "hepai": [{"name": "hepai/gpt-4", "enabled": True}, ...],
                "Uncategorized": [{"name": "local-llama", "enabled": False}, ...]
            }
        """
        providers: Dict[str, List[Dict]] = {}

        for model in self.worker.models:
            model_name = model.name
            provider = self._extract_provider(model_name)

            if provider not in providers:
                providers[provider] = []

            providers[provider].append({
                "name": model_name,
                "enabled": self.is_model_enabled(model_name)
            })

        return providers

    def get_all_model_status(self) -> Dict[str, bool]:
        """
        获取所有模型的状态

        Returns:
            Dict[str, bool]: {model_name: enabled}
        """
        with self._lock:
            return self._model_status.copy()

    def _extract_provider(self, model_name: str) -> str:
        """
        从模型名称中提取提供者

        规则：
        - 包含 "/" 的模型名：提取 "/" 前部分（如 "hepai/gpt-4" → "hepai"）
        - 不包含 "/" 的模型名：归类为 "Uncategorized"

        Args:
            model_name: 模型名称

        Returns:
            str: 提供者名称
        """
        if "/" in model_name:
            return model_name.split("/")[0]
        return "Uncategorized"

    def _load_or_create_config(self):
        """加载或创建配置文件"""
        if os.path.exists(self.config_file):
            try:
                self._load_config()
                if hasattr(self.worker, 'logger'):
                    self.worker.logger.info(
                        f"Model status config loaded from: {self.config_file}"
                    )
            except Exception as e:
                # 配置文件损坏，备份并重建
                if hasattr(self.worker, 'logger'):
                    self.worker.logger.error(
                        f"Failed to load config from {self.config_file}: {e}. "
                        f"Creating backup and rebuilding..."
                    )
                self._backup_and_rebuild()
        else:
            # 首次运行，创建配置文件
            self._create_default_config()
            if hasattr(self.worker, 'logger'):
                self.worker.logger.info(
                    f"Model status config created at: {self.config_file}"
                )
            else:
                print(f"Model status config created at: {self.config_file}")

    def _load_config(self):
        """从文件加载配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        if not config_data or 'models' not in config_data:
            raise ValueError("Invalid config file format")

        # 加载模型状态
        models_config = config_data.get('models', {})
        for model_name, model_data in models_config.items():
            if isinstance(model_data, dict):
                self._model_status[model_name] = model_data.get('enabled', True)
            else:
                self._model_status[model_name] = True

        # 检查是否有新增的模型（在 worker.models 中但不在配置文件中）
        for model in self.worker.models:
            if model.name not in self._model_status:
                self._model_status[model.name] = True  # 新模型默认启用

    def _create_default_config(self):
        """创建默认配置文件（所有模型默认启用）"""
        for model in self.worker.models:
            self._model_status[model.name] = True

        self._save_config()

    def _save_config(self):
        """保存配置到文件"""
        config_data = {
            'version': '1.0',
            'last_modified': time.time(),
            'models': {}
        }

        for model in self.worker.models:
            model_name = model.name
            config_data['models'][model_name] = {
                'enabled': self._model_status.get(model_name, True),
                'provider': self._extract_provider(model_name),
                'last_updated': time.time()
            }

        # 写入文件（使用临时文件 + 原子替换保证安全性）
        temp_file = self.config_file + '.tmp'
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

            # 原子替换
            os.replace(temp_file, self.config_file)
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e

    def _backup_and_rebuild(self):
        """备份损坏的配置文件并重建"""
        # 备份
        if os.path.exists(self.config_file):
            backup_file = f"{self.config_file}.backup.{int(time.time())}"
            try:
                os.rename(self.config_file, backup_file)
                if hasattr(self.worker, 'logger'):
                    self.worker.logger.info(f"Backup created: {backup_file}")
            except Exception as e:
                if hasattr(self.worker, 'logger'):
                    self.worker.logger.error(f"Failed to create backup: {e}")

        # 重建
        self._create_default_config()
