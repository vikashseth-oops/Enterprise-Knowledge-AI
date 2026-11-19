from app.agent.graph import get_agent_graph
from app.ingestion.pipeline import IngestionPipeline, get_ingestion_pipeline
from app.retrieval.qdrant_store import QdrantStore, get_qdrant_store


def get_pipeline() -> IngestionPipeline:
    return get_ingestion_pipeline()


def get_store() -> QdrantStore:
    return get_qdrant_store()


def get_graph():
    return get_agent_graph()
