from reciprocity.config import config
from ollama import Client

OLLAMA_MODEL = "reciprocity"

ollama_client = Client(host=config.ollama.host)
