from typing import Dict, List, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
import uuid
import json


def _flatten_metadata(data: Any, parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
    """
    Flatten nested metadata into Pinecone-compatible key-value pairs.
    Pinecone allows: string, number, boolean, list[string]
    Everything else becomes a string.
    """
    items = {}

    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(_flatten_metadata(v, new_key, sep))
    elif isinstance(data, list):
        # Pinecone only accepts list[str], so convert items to strings
        items[parent_key] = [str(x) for x in data]
    elif isinstance(data, (str, int, float, bool)):
        items[parent_key] = data
    else:
        # Anything weird → serialize to JSON string
        items[parent_key] = json.dumps(data)

    return items


class PineconeMemoryStore:
    """Ultra-fast semantic memory storage using Pinecone serverless with auto metadata sanitization."""

    def __init__(
        self,
        api_key: str,
        index_name: str = "pitchpilot",
        vector_dimension: int = 384,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cloud: str = "aws",
        region: str = "us-east-1"
    ):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.vector_dimension = vector_dimension
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)

        # Ensure index exists safely
        self._ensure_index(cloud, region)

        # Fast reference to index object
        self.index = self.pc.Index(index_name)

    # -------------------------------------------------------
    def _ensure_index(self, cloud: str, region: str):
        """Create index if missing. Handles race conditions."""
        try:
            existing = [idx["name"] for idx in self.pc.list_indexes()]
        except Exception as e:
            raise RuntimeError(f"Pinecone index listing failed: {e}")

        if self.index_name not in existing:
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.vector_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud=cloud, region=region)
                )
            except Exception as e:
                raise RuntimeError(f"Failed to create Pinecone index '{self.index_name}': {e}")

    # -------------------------------------------------------
    def _sanitize_metadata(self, text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ensure Pinecone-compatible metadata."""
        metadata = metadata or {}

        safe_meta = {
            "text": text
        }

        # Flatten and sanitize all metadata deeply
        flat = _flatten_metadata(metadata)

        safe_meta.update(flat)
        return safe_meta

    # -------------------------------------------------------
    def add_to_memory(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Store text and metadata safely in Pinecone."""
        memory_id = str(uuid.uuid4())

        vector = self.embedding_model.embed_query(text)

        safe_metadata = self._sanitize_metadata(text, metadata)

        try:
            self.index.upsert(
                vectors=[
                    {
                        "id": memory_id,
                        "values": vector,
                        "metadata": safe_metadata
                    }
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Pinecone upsert failed for memory {memory_id}: {e}")

        return memory_id

    # -------------------------------------------------------
    def retrieve_relevant(self, query: str, limit: int = 5) -> List[str]:
        query_vec = self.embedding_model.embed_query(query)

        try:
            results = self.index.query(
                vector=query_vec,
                top_k=limit,
                include_metadata=True
            )
        except Exception as e:
            raise RuntimeError(f"Pinecone query failed: {e}")

        # Convert dataclass → dict safely
        if hasattr(results, "to_dict"):
            results = results.to_dict()

        matches = results.get("matches", [])
        output = []

        for match in matches:
            meta = match.get("metadata", {})
            text = meta.get("text")

            if isinstance(text, str):
                output.append(text)

        return output

