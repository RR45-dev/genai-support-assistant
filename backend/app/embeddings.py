from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app import config


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBEDDING_MODEL_NAME)


def embed(texts: list[str]):
    model = get_model()
    return model.encode(texts, normalize_embeddings=True)
