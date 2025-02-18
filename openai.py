import os
from typing import List, Union, Optional

from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from embedbase.embedding.base import Embedder
from embedbase.logging_utils import get_logger
from openai import BadRequestError

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=3),
    stop=stop_after_attempt(3),
    retry=retry_if_not_exception_type(BadRequestError),
)
def embed_retry(self,
    data: List[str],
) -> List[dict]:
    """
    Embed a list of sentences and retry on failure
    :param data: list of sentences to embed
    :param provider: which provider to use
    :return: list of embeddings
    """
 
    openai_model = os.getenv('OPENAI_MODEL', 'text-embedding-ada-002')

    embeddings = self.openai.embeddings.create(input=data, model=openai_model)

    return [
        e.embedding
        for e in embeddings.data
    ]


class OpenAI(Embedder):
    """
    OpenAI Embedder
    """

    EMBEDDING_MODEL = "text-embedding-ada-002"
    EMBEDDING_CTX_LENGTH = 8191
    EMBEDDING_ENCODING = "cl100k_base"

    def __init__(
        self, openai_api_key: str, openai_organization: Optional[str] = None
    ):
        self.logger = get_logger()
        super().__init__()
        try:
            from openai import OpenAI
            import tiktoken
        except ImportError:
            raise ImportError(
                "OpenAI is not installed. Install it with `pip install openai tiktoken`"
            )

        self.encoding = tiktoken.get_encoding(self.EMBEDDING_ENCODING)
        url = os.getenv('OPENAI_URL')
        if url is not None:
            self.logger.info(f"OPENAI: set explicit url: {url}")
            self.openai = OpenAI(base_url=url, api_key=openai_api_key)
        else:
            self.logger.info(f"OPENAI: set implicit url")
            self.openai = OpenAI(api_key=openai_api_key, organization=openai_organization)

    @property
    def dimensions(self) -> int:
        dims = os.getenv('DIMENSIONS')
        if dims is None:
            return 1536
        else:
            return int(dims)

    def is_too_big(self, text: str) -> bool:
        tokens = self.encoding.encode(text)
        if len(tokens) > self.EMBEDDING_CTX_LENGTH:
            return True

        return False

    async def embed(self, data: Union[List[str], str]) -> List[List[float]]:
        return embed_retry(self, data)
