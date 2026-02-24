from reciprocity.config import config
from ollama import Client

ollama_client = Client(host=config.ollama.host)
ollama_model = f"reciprocity:{config.ollama.base.replace(':', '-')}"
