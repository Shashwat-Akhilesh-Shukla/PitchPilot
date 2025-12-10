from typing import Dict, List, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
import uuid


class PineconeMemoryStore:
    """Ultra-fast semantic memory storage using Pinecone serverless."""

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

        # Ensure index exists once
        self._ensure_index(cloud, region)

        # fast reference to index object
        self.index = self.pc.Index(index_name)

    def _ensure_index(self, cloud: str, region: str):
        existing = [idx["name"] for idx in self.pc.list_indexes()]

        if self.index_name not in existing:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.vector_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=cloud, region=region)
            )

    def add_to_memory(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Store text with metadata in Pinecone."""
        memory_id = str(uuid.uuid4())

        # compute embedding only once
        vector = self.embedding_model.embed_query(text)

        # Pinecone fast upsert
        self.index.upsert(
            vectors=[
                {
                    "id": memory_id,
                    "values": vector,
                    "metadata": {
                        "text": text,
                        "metadata": metadata or {}
                    }
                }
            ]
        )

        return memory_id

    def retrieve_relevant(self, query: str, limit: int = 5) -> List[str]:
        """Retrieve top-K semantic matches."""
        query_vec = self.embedding_model.embed_query(query)

        results = self.index.query(
            vector=query_vec,
            top_k=limit,
            include_metadata=True
        )

        return [
            match["metadata"]["text"]
            for match in results["matches"]
        ]
