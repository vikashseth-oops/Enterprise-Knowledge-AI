import datetime
import math
from typing import Any

from app.core.logging import logger
from app.ingestion.embedder import get_embedder
from app.ingestion.pipeline import get_ingestion_pipeline
from app.retrieval.qdrant_store import get_qdrant_store

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Searches the enterprise knowledge base for documents and excerpts matching a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search keywords or query.",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Maximum number of chunks to return (default 5).",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_documents",
            "description": "Lists all indexed documents currently stored in the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": "Fetches all available chunks and content for a given document by filename or doc_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_name_or_id": {
                        "type": "string",
                        "description": "Filename or doc_id to summarize.",
                    }
                },
                "required": ["document_name_or_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluates a safe mathematical expression (e.g. '120 * 45 / 1.2').",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical formula to evaluate.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Returns the current UTC date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


class ToolExecutor:
    """Executes registered agent tools with defensive error handling."""

    @staticmethod
    async def execute(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        logger.info("executing_tool", tool_name=name, args=arguments)
        try:
            if name == "search_knowledge_base":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 5)
                embedder = get_embedder()
                dense_vec, sparse_vec = embedder.embed_query(query)
                store = get_qdrant_store()
                hits = await store.search_hybrid(dense_vec, sparse_vec, top_k=top_k)
                return {
                    "status": "success",
                    "results_count": len(hits),
                    "results": [
                        {
                            "chunk_id": h["chunk_id"],
                            "doc_name": h["doc_name"],
                            "snippet": h["text"][:300],
                            "score": h["score"],
                        }
                        for h in hits
                    ],
                }

            elif name == "list_documents":
                pipeline = get_ingestion_pipeline()
                docs = pipeline.list_documents()
                return {
                    "status": "success",
                    "total_documents": len(docs),
                    "documents": [
                        {
                            "doc_id": d.doc_id,
                            "filename": d.filename,
                            "size_bytes": d.file_size_bytes,
                            "chunks": d.chunk_count,
                            "status": d.status,
                        }
                        for d in docs
                    ],
                }

            elif name == "summarize_document":
                target = arguments.get("document_name_or_id", "")
                pipeline = get_ingestion_pipeline()
                store = get_qdrant_store()

                # Find document in registry
                matched_doc = None
                for d in pipeline.list_documents():
                    if d.doc_id == target or d.filename.lower() == target.lower():
                        matched_doc = d
                        break

                if not matched_doc:
                    return {
                        "status": "error",
                        "message": f"Document '{target}' not found.",
                    }

                chunks = store.get_document_chunks(matched_doc.doc_id, limit=20)
                texts = [c.get("text", "") for c in chunks]
                combined = "\n\n".join(texts)

                return {
                    "status": "success",
                    "filename": matched_doc.filename,
                    "doc_id": matched_doc.doc_id,
                    "content_preview": combined[:2500],
                    "total_chunks": len(chunks),
                }

            elif name == "calculator":
                expr = arguments.get("expression", "")
                # Safe evaluation restricted to math primitives
                safe_globals = {
                    "__builtins__": None,
                    "abs": abs,
                    "round": round,
                    "min": min,
                    "max": max,
                    "pow": pow,
                    "math": math,
                }
                # Sanitize expression: allow digits, operators, parens, whitespace, math names
                if not all(c in "0123456789+-*/()., %" or c.isalnum() for c in expr):
                    return {
                        "status": "error",
                        "message": "Invalid characters in expression.",
                    }

                result = eval(expr, safe_globals, {})
                return {"status": "success", "expression": expr, "result": result}

            elif name == "get_current_datetime":
                now = datetime.datetime.now(datetime.UTC)
                return {
                    "status": "success",
                    "iso_utc": now.isoformat(),
                    "formatted": now.strftime("%A, %B %d, %Y at %I:%M:%S %p UTC"),
                }

            else:
                return {"status": "error", "message": f"Unknown tool: {name}"}

        except Exception as e:
            logger.error("tool_execution_error", tool=name, error=str(e))
            return {
                "status": "error",
                "message": f"Failed to execute tool {name}: {e!s}",
            }
