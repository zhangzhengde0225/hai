import importlib


def test_logger_uses_hepai_log_dir_environment_variable(monkeypatch, tmp_path):
    custom_log_dir = tmp_path / "hepai-logs"
    monkeypatch.setenv("HEPAI_LOG_DIR", str(custom_log_dir))

    import hepai.tools.logger as logger_module

    logger_module = importlib.reload(logger_module)
    logger = logger_module.Logger.get_logger("test_logger")
    logger.info("hello")

    assert logger_module.Logger.logg_dir == str(custom_log_dir)
    assert custom_log_dir.exists()
    assert list(custom_log_dir.glob("*.log"))
