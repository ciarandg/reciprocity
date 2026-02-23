from ollama import Client

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "reciprocity"
OLLAMA_BASE = "qwen3:1.7b"

ollama_client = Client(host=OLLAMA_HOST)
