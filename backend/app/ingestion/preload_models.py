from fastembed import SparseTextEmbedding, TextEmbedding

from app.config import settings


def preload():
    print(f"Preloading dense model '{settings.EMBEDDING_MODEL}'...")
    dense = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
    list(dense.embed(["test warmup text"]))
    print("Dense model cached successfully.")

    print(f"Preloading sparse model '{settings.SPARSE_MODEL}'...")
    try:
        sparse = SparseTextEmbedding(model_name=settings.SPARSE_MODEL)
        list(sparse.embed(["test warmup text"]))
        print("Sparse model cached successfully.")
    except Exception as e:
        print(f"Sparse model warning: {e}")


if __name__ == "__main__":
    preload()
