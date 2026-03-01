import json
import os
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

from platformdirs import PlatformDirs

DEFAULT_CONFIG = {
    "logging": {"level": "info"},
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


def _env_overrides(prefix: str = "RECIPROCITY_") -> dict:
    overrides = {}
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        path = key[len(prefix) :].lower().split("_")
        cursor = overrides
        for part in path[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[path[-1]] = value
    return overrides


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
    merged = _deep_merge(DEFAULT_CONFIG, user_config)
    env_config = _env_overrides()
    return _deep_merge(merged, env_config)


@lru_cache(maxsize=1)
def get_config():
    """
    Returns a namespace object containing the configuration (merged with defaults).
    """
    merged = get_config_dict()
    return _to_namespace(merged)
