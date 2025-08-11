from typing import Dict, List, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid

from langchain_huggingface import HuggingFaceEmbeddings

import os

class QdrantMemoryStore:
    """Memory store using Qdrant for semantic storage and retrieval with HuggingFace Embeddings."""

    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        collection_name: str = "pitchpilot",
        vector_dimension: int = 384 ,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.vector_dimension = vector_dimension
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)

        # Ensure collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_dimension,
                    distance=Distance.COSINE
                )
            )

    def add_to_memory(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add text to memory with associated metadata.

        Args:
            text: The text to store
            metadata: Associated metadata

        Returns:
            ID of the stored memory
        """
        # Generate a UUID for the memory
        memory_id = str(uuid.uuid4())

        # Generate vector embedding for the text
        vector = self.embedding_model.embed_query(text)

        # Create the point
        point = PointStruct(
            id=memory_id,
            vector=vector,
            payload={
                "text": text,
                "metadata": metadata or {}
            }
        )

        # Insert the point
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return memory_id

    def retrieve_relevant(self, query: str, limit: int = 5) -> List[str]:
        """
        Retrieve relevant memories based on a query.

        Args:
            query: The query text
            limit: Maximum number of memories to retrieve

        Returns:
            List of relevant memory texts
        """
        # Generate vector embedding for the query
        vector = self.embedding_model.embed_query(query)

        # Search for relevant points
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit
        )

        # Extract texts from results
        texts = [result.payload["text"] for result in search_results]
        return texts
