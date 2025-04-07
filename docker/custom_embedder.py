import os
import requests
from typing import List, Union
from embedbase.embedding.base import Embedder
from embedbase.logging_utils import get_logger


class CustomEmbedder(Embedder):
    """
    Embedder for custom embedding service that returns OpenAI-like structure.
    """

    def __init__(self, api_url: str):
        self.logger = get_logger()
        super().__init__()
        self.api_url = api_url
        self.embedding_dim = int(os.getenv("DIMENSIONS", "1024"))  # update if needed

    @property
    def dimensions(self) -> int:
        return self.embedding_dim

    def is_too_big(self, text: str) -> bool:
        # Customize based on your embedder's token limit
        return len(text) > 10000

    async def embed(self, data: Union[List[str], str]) -> List[List[float]]:
        if isinstance(data, str):
            data = [data]

        embeddings = []

        for item in data:
            try:
                payload = {
                    "model": "gritlm-7b:latest",
                    "input": item,
                    "encoding_format": "float"
                }
                print("Sending payload:", json.dumps(payload, indent=2))

                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    verify=False
                )
                response.raise_for_status()
                embedding = response.json()["data"][0]["embedding"]
                embeddings.append(embedding)
            except Exception as e:
                self.logger.error(f"Failed to embed input: {item[:50]}... Error: {e}")
                raise

        return embeddings

