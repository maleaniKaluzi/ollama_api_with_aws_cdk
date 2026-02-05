import requests


OLLAMA_URL = "http://localhost:11434"
MODEL = "nomic-embed-text"


def embed(text):

    res = requests.post(
        f"{OLLAMA_URL}/api/embeddings", json={"model": MODEL, "prompt": text}
    )

    return res.json()["embedding"]
