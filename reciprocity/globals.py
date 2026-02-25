from importlib.metadata import version
from reciprocity.config import config
from ollama import Client

ollama_client = Client(host=config.ollama.host)
ollama_model = (
    f"reciprocity:{version('reciprocity')}-{config.ollama.base.replace(':', '-')}"
)
