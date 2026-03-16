"""
Qdrant Memory Adapter
Replaces Zep Cloud with Qdrant for agent memory and entity storage
"""

from typing import List, Dict, Any, Optional
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
import openai

from ..config_infrastructure import InfrastructureConfig


class QdrantMemoryAdapter:
    """Adapter for storing agent memories and entities in Qdrant"""

    def __init__(self):
        config = InfrastructureConfig.get_qdrant_config()
        self.client = QdrantClient(url=config["url"], api_key=config.get("api_key"))
        self.collection_prefix = config["collection_prefix"]
        self.embedding_model = "text-embedding-ada-002"  # Can be overridden

        # OpenAI client for embeddings (routes through LiteLLM)
        llm_config = InfrastructureConfig.get_llm_config()
        self.openai_client = openai.OpenAI(
            api_key=llm_config["api_key"], base_url=llm_config["base_url"]
        )

    def _get_collection_name(self, project_id: str, collection_type: str) -> str:
        """Generate collection name for project"""
        return f"{self.collection_prefix}_{project_id}_{collection_type}"

    def _ensure_collection(self, collection_name: str, vector_size: int = 1536):
        """Ensure collection exists with proper configuration"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model, input=text
        )
        return response.data[0].embedding

    def store_memory(
        self,
        project_id: str,
        agent_id: str,
        memory_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store agent memory in Qdrant"""
        collection_name = self._get_collection_name(project_id, "memories")
        self._ensure_collection(collection_name)

        memory_id = str(uuid.uuid4())
        embedding = self._get_embedding(memory_text)

        payload = {
            "agent_id": agent_id,
            "text": memory_text,
            "metadata": metadata or {},
        }

        self.client.upsert(
            collection_name=collection_name,
            points=[PointStruct(id=memory_id, vector=embedding, payload=payload)],
        )

        return memory_id

    def search_memories(
        self,
        project_id: str,
        query: str,
        agent_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search agent memories"""
        collection_name = self._get_collection_name(project_id, "memories")

        try:
            query_embedding = self._get_embedding(query)

            filter_conditions = None
            if agent_id:
                filter_conditions = Filter(
                    must=[
                        FieldCondition(key="agent_id", match=MatchValue(value=agent_id))
                    ]
                )

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                query_filter=filter_conditions,
                limit=limit,
            )

            return [
                {
                    "id": str(hit.id),
                    "text": hit.payload.get("text"),
                    "agent_id": hit.payload.get("agent_id"),
                    "metadata": hit.payload.get("metadata", {}),
                    "score": hit.score,
                }
                for hit in results
            ]
        except Exception:
            return []

    def store_entity(
        self,
        project_id: str,
        entity_name: str,
        entity_type: str,
        description: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store entity (person, location, concept) in Qdrant"""
        collection_name = self._get_collection_name(project_id, "entities")
        self._ensure_collection(collection_name)

        entity_id = str(uuid.uuid4())
        embedding = self._get_embedding(f"{entity_name}: {description}")

        payload = {
            "name": entity_name,
            "type": entity_type,
            "description": description,
            "attributes": attributes or {},
        }

        self.client.upsert(
            collection_name=collection_name,
            points=[PointStruct(id=entity_id, vector=embedding, payload=payload)],
        )

        return entity_id

    def get_entities(
        self, project_id: str, entity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve entities from project"""
        collection_name = self._get_collection_name(project_id, "entities")

        try:
            filter_conditions = None
            if entity_type:
                filter_conditions = Filter(
                    must=[
                        FieldCondition(key="type", match=MatchValue(value=entity_type))
                    ]
                )

            # Scroll through all points
            results = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=filter_conditions,
                limit=1000,
            )[0]

            return [
                {
                    "id": str(point.id),
                    "name": point.payload.get("name"),
                    "type": point.payload.get("type"),
                    "description": point.payload.get("description"),
                    "attributes": point.payload.get("attributes", {}),
                }
                for point in results
            ]
        except Exception:
            return []

    def delete_project_data(self, project_id: str):
        """Delete all data for a project"""
        for collection_type in ["memories", "entities"]:
            collection_name = self._get_collection_name(project_id, collection_type)
            try:
                self.client.delete_collection(collection_name)
            except Exception:
                pass
