from __future__ import annotations

import hashlib
import math
import time
from abc import ABC, abstractmethod

from memory_config.settings import get_settings

settings = get_settings()

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class LocalHashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha512(text.encode("utf-8")).digest()
            raw = [float(digest[i % len(digest)]) for i in range(self.dimension)]
            norm = math.sqrt(sum(val * val for val in raw)) or 1.0
            vectors.append([val / norm for val in raw])
        return vectors


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str, dimension: int) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package is not installed. Use `pip install -e .[openai]`.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        start = time.perf_counter()
        response = self.client.embeddings.create(model=self.model, input=texts)
        vectors = [list(item.embedding[: self.dimension]) for item in response.data]
        _ = (time.perf_counter() - start) * 1000
        return vectors


def build_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider.lower() == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    return LocalHashEmbeddingProvider(dimension=settings.embedding_dimension)
