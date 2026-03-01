from importlib.metadata import version
from reciprocity.config import get_config
from ollama import Client

ollama_client = Client(host=get_config().ollama.host)
ollama_model = (
    f"reciprocity:{version('reciprocity')}-{get_config().ollama.base.replace(':', '-')}"
)
