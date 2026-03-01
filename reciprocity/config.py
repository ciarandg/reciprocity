import json
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

from platformdirs import PlatformDirs

DEFAULT_CONFIG = {
    "log_level": "info",
    "ollama": {"host": "http://127.0.0.1:11434", "base": "qwen3:1.7b"},
}


def _load_json_config(path: Path) -> dict:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge override into base.
    Does not mutate inputs.
    """
    result = dict(base)

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], Mapping)
            and isinstance(value, Mapping)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def _to_namespace(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [_to_namespace(x) for x in d]
    return d


@lru_cache(maxsize=1)
def config_file() -> Path:
    """
    Returns the path to the configuration file
    """
    dirs = PlatformDirs("reciprocity", "ciarandg")
    config_dir = Path(dirs.user_config_dir)
    return config_dir / "config.json"


@lru_cache(maxsize=1)
def get_config_dict():
    """
    Returns a dictionary containing the configuration (merged with defaults).
    In most cases you should use get_config() instead as it provides a namespace
    object that you can access with the dot operator.
    """
    file = config_file()
    user_config = _load_json_config(file)
    return _deep_merge(DEFAULT_CONFIG, user_config)


@lru_cache(maxsize=1)
def get_config():
    """
    Returns a namespace object containing the configuration (merged with defaults).
    """
    merged = get_config_dict()
    return _to_namespace(merged)
