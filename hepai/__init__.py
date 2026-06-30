from pathlib import Path


def _read_version():
    version_file = Path(__file__).resolve().parent.parent / "hai" / "version.py"
    for line in version_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            return line.split("=", 1)[1].strip().strip("'\"")
    return "0.0.0"


__version__ = _read_version()


_LAZY_EXPORTS = {
    "HepAI": ("hepai.components.haiddf.hepai_client", "HepAIClient"),
    "AsyncHepAI": ("hepai.components.haiddf.hepai_client", "AsyncHepAIClient"),
    "Stream": ("hepai.components.haiddf.hclient._hclient", "Stream"),
    "ChatCompletion": ("hepai.components.haiddf.hclient._hclient", "ChatCompletion"),
    "ChatCompletionChunk": ("hepai.components.haiddf.hclient._hclient", "ChatCompletionChunk"),
    "HRModel": ("hepai.components.haiddf.base_class._worker_class", "HRModel"),
    "HRemoteModel": ("hepai.components.haiddf.base_class._worker_class", "HRemoteModel"),
    "HCloudModel": ("hepai.components.haiddf.base_class._worker_class", "HCloudModel"),
    "HModelConfig": ("hepai.components.haiddf.base_class._worker_class", "HModelConfig"),
    "LRModel": ("hepai.components.haiddf.hclient._remote_model", "LRModel"),
    "RemoteModel": ("hepai.components.haiddf.hclient._remote_model", "RemoteModel"),
    "HWorkerAPP": ("hepai.components.haiddf.worker.worker_app", "HWorkerAPP"),
    "HWorkerConfig": ("hepai.components.haiddf.worker._worker_class", "HWorkerConfig"),
    "HaiMCP": ("hepai.components.haiddf.hclient.map_adapter.hai_mcp", "HaiMCP"),
    "LLMRemoteModelV2": ("hepai.components.haiddf.base_class._llm_remote_model_v2", "LLMRemoteModelV2"),
    "connect": ("hepai.components.utils", "connect"),
}

_LEGACY_HAI_EXPORTS = {
    "HaiFile",
    "BaseWorkerModel",
    "WorkerArgs",
    "parse_args",
    "parse_args_into_dataclasses",
    "worker",
    "hub",
    "Config",
    "UAII",
    "LLM",
    "Model",
    "Models",
    "api_key",
}


def __getattr__(name):
    if name in _LAZY_EXPORTS:
        module_name, attr_name = _LAZY_EXPORTS[name]
        from importlib import import_module

        attr = getattr(import_module(module_name), attr_name)
        globals()[name] = attr
        return attr

    if name in _LEGACY_HAI_EXPORTS:
        import hai

        attr = getattr(hai, name)
        globals()[name] = attr
        return attr

    raise AttributeError(f"module 'hepai' has no attribute {name!r}")


__all__ = [
    "__version__",
    *_LAZY_EXPORTS.keys(),
    *_LEGACY_HAI_EXPORTS,
]
