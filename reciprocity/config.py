from types import SimpleNamespace
from collections.abc import Mapping
import json
from pathlib import Path
from platformdirs import PlatformDirs

DEFAULT_CONFIG = {"ollama": {"host": "http://127.0.0.1:11434", "base": "qwen3:1.7b"}}

dirs = PlatformDirs("reciprocity", "ciarandg")

config_dir = Path(dirs.user_config_dir)
config_file = config_dir / "config.json"


def load_json_config(path: Path) -> dict:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def deep_merge(base: dict, override: dict) -> dict:
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
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def to_namespace(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [to_namespace(x) for x in d]
    return d


user_config = load_json_config(config_file)
merged = deep_merge(DEFAULT_CONFIG, user_config)
config = to_namespace(merged)
