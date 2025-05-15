from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid
import json

class QdrantMemoryStore:
    """Memory store using Qdrant for semantic storage and retrieval."""
    
    def __init__(
        self, 
        url: str, 
        api_key: Optional[str] = None, 
        collection_name: str = "pitchpilot_memory",
        vector_dimension: int = 1536
    ):
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.vector_dimension = vector_dimension
        
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
        # In a real implementation, this would use the LLM's embedding API
        # For simplicity, we'll use a mock implementation
        vector = self._mock_generate_embedding(text)
        
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
        vector = self._mock_generate_embedding(query)
        
        # Search for relevant points
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit
        )
        
        # Extract texts from results
        texts = [result.payload["text"] for result in search_results]
        
        return texts
    
    def _mock_generate_embedding(self, text: str) -> List[float]:
        """
        Mock function to generate vector embedding.
        In a real implementation, this would use an embedding model.
        """
        import hashlib
        import random
        
        # Generate a deterministic seed based on the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash, 16) % 10000
        random.seed(seed)
        
        # Generate a vector of the required dimension
        vector = [random.uniform(-1, 1) for _ in range(self.vector_dimension)]
        
        # Normalize the vector
        magnitude = sum(v * v for v in vector) ** 0.5
        vector = [v / magnitude for v in vector]
        
        return vector
