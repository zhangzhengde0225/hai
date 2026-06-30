from pathlib import Path
from ast import literal_eval


def _read_metadata():
    version_file = Path(__file__).resolve().parent.parent / "hai" / "version.py"
    data = {}
    for line in version_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("__"):
            key, _, value = line.partition("=")
            value = value.split("#", 1)[0].strip()
            try:
                data[key.strip()] = literal_eval(value)
            except (SyntaxError, ValueError):
                data[key.strip()] = value.strip("'\"")
    return data


def _print_version():
    meta = _read_metadata()
    appname = meta.get("__appname__", "hepai")
    version = meta.get("__version__", "0.0.0")
    suffix = meta.get("__version_suffix__", "")
    if suffix:
        version = f"{version}-{suffix}"
    print(f"{appname.upper()} Version: {version}")


def run():
    import sys

    args = sys.argv[1:]
    if not args or args[0] in {"-V", "--version", "version"}:
        _print_version()
        if not args:
            print('Install "hepai[legacy]" to use legacy hai commands such as train, eval, and datasets.')
        return

    try:
        from hai.uaii.cli.cli_main import run as legacy_run
    except ModuleNotFoundError as exc:
        missing = exc.name or "legacy dependency"
        raise SystemExit(
            f"The legacy hai CLI command requires optional dependency `{missing}`. "
            'Install it with `pip install "hepai[legacy]"`, or use `pip install "hepai[full]"` '
            "for all optional features."
        ) from exc

    legacy_run()


if __name__ == "__main__":
    run()
