"""Pattern storage using ChromaDB for vector-based retrieval."""

import logging
from typing import Dict, Any, List, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class PatternStorage:
    """Manages storage and retrieval of reasoning patterns in ChromaDB."""
    
    COLLECTION_NAME = "reasoning_patterns"
    
    def __init__(self, chromadb_host: str = "sira-chromadb", chromadb_port: int = 8000):
        """Initialize pattern storage.
        
        Args:
            chromadb_host: ChromaDB host address
            chromadb_port: ChromaDB port number
        """
        self.chromadb_host = chromadb_host
        self.chromadb_port = chromadb_port
        self.client = None
        self.collection = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.HttpClient(
                host=self.chromadb_host,
                port=self.chromadb_port,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={
                    "description": "Reasoning patterns extracted from high-quality responses",
                    "hnsw:space": "cosine"  # Use cosine similarity
                }
            )
            
            logger.info(
                "pattern_storage_initialized",
                extra={
                    "collection": self.COLLECTION_NAME,
                    "count": self.collection.count()
                }
            )
            
        except Exception as e:
            logger.error(
                "pattern_storage_init_error",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise
    
    def store_pattern(self, pattern: Dict[str, Any]) -> bool:
        """Store a pattern in ChromaDB.
        
        Args:
            pattern: Pattern dictionary with all fields
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            pattern_id = pattern['pattern_id']
            
            # Check if pattern already exists
            existing = self._get_pattern_by_id(pattern_id)
            if existing:
                logger.info(
                    "pattern_already_exists",
                    extra={"pattern_id": pattern_id}
                )
                return self._update_pattern_stats(pattern_id, pattern)
            
            # Create document text for embedding (combination of key fields)
            document = self._create_pattern_document(pattern)
            
            # Create metadata (everything except large text fields)
            metadata = {
                'pattern_type': pattern['pattern_type'],
                'domain': pattern['domain'],
                'quality_score': pattern['quality_score'],
                'extracted_at': pattern['extracted_at'],
                'usage_count': pattern['usage_count'],
                'success_rate': pattern['success_rate'],
                'applicability': pattern['applicability'][:500]  # Truncate for metadata
            }
            
            # Store in ChromaDB
            self.collection.add(
                ids=[pattern_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            logger.info(
                "pattern_stored",
                extra={
                    "pattern_id": pattern_id,
                    "pattern_type": pattern['pattern_type'],
                    "domain": pattern['domain']
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "pattern_storage_error",
                extra={
                    "pattern_id": pattern.get('pattern_id', 'unknown'),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return False
    
    def _get_pattern_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a pattern by its ID.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Pattern dictionary or None if not found
        """
        try:
            result = self.collection.get(
                ids=[pattern_id],
                include=['documents', 'metadatas']
            )
            
            if result['ids']:
                return {
                    'pattern_id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            
            return None
            
        except Exception as e:
            logger.error(
                "pattern_retrieval_error",
                extra={
                    "pattern_id": pattern_id,
                    "error": str(e)
                }
            )
            return None
    
    def _update_pattern_stats(self, pattern_id: str, pattern: Dict[str, Any]) -> bool:
        """Update usage statistics for an existing pattern.
        
        Args:
            pattern_id: Pattern identifier
            pattern: Updated pattern data
            
        Returns:
            True if updated successfully
        """
        try:
            # Get existing pattern
            existing = self._get_pattern_by_id(pattern_id)
            if not existing:
                return False
            
            # Update metadata with new stats
            updated_metadata = existing['metadata'].copy()
            updated_metadata['usage_count'] = pattern.get('usage_count', updated_metadata.get('usage_count', 0))
            updated_metadata['success_rate'] = pattern.get('success_rate', updated_metadata.get('success_rate', 0.0))
            
            self.collection.update(
                ids=[pattern_id],
                metadatas=[updated_metadata]
            )
            
            logger.info(
                "pattern_stats_updated",
                extra={
                    "pattern_id": pattern_id,
                    "usage_count": updated_metadata['usage_count']
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "pattern_update_error",
                extra={
                    "pattern_id": pattern_id,
                    "error": str(e)
                }
            )
            return False
    
    def _create_pattern_document(self, pattern: Dict[str, Any]) -> str:
        """Create a document string for embedding from pattern.
        
        This combines the most important textual fields for semantic search.
        
        Args:
            pattern: Pattern dictionary
            
        Returns:
            Document string for embedding
        """
        parts = [
            f"Pattern Type: {pattern['pattern_type']}",
            f"Domain: {pattern['domain']}",
            f"Applicability: {pattern['applicability']}",
            "Reasoning Steps:",
            *[f"- {step}" for step in pattern['reasoning_steps']],
            "Success Indicators:",
            *[f"- {indicator}" for indicator in pattern['success_indicators']],
            f"Template: {pattern['template']}"
        ]
        
        return "\n".join(parts)
    
    def search_similar_patterns(
        self,
        query: str,
        n_results: int = 5,
        min_quality: float = 0.7,
        pattern_type: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar patterns using semantic similarity.
        
        Args:
            query: Query text to find similar patterns for
            n_results: Number of results to return
            min_quality: Minimum quality score filter
            pattern_type: Optional filter by pattern type
            domain: Optional filter by domain
            
        Returns:
            List of similar patterns with similarity scores
        """
        try:
            # Build where clause for filtering
            where = {}
            if min_quality > 0:
                where["quality_score"] = {"$gte": min_quality}
            if pattern_type:
                where["pattern_type"] = pattern_type
            if domain:
                where["domain"] = domain
            
            # Search ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where if where else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            patterns = []
            if results['ids'] and results['ids'][0]:
                for i, pattern_id in enumerate(results['ids'][0]):
                    patterns.append({
                        'pattern_id': pattern_id,
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                    })
            
            logger.info(
                "pattern_search_complete",
                extra={
                    "query_length": len(query),
                    "results_count": len(patterns),
                    "filters": where
                }
            )
            
            return patterns
            
        except Exception as e:
            logger.error(
                "pattern_search_error",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return []
    
    def get_pattern_count(self) -> int:
        """Get total number of stored patterns.
        
        Returns:
            Pattern count
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(
                "pattern_count_error",
                extra={"error": str(e)}
            )
            return 0
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern from storage.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            self.collection.delete(ids=[pattern_id])
            
            logger.info(
                "pattern_deleted",
                extra={"pattern_id": pattern_id}
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "pattern_deletion_error",
                extra={
                    "pattern_id": pattern_id,
                    "error": str(e)
                }
            )
            return False
    
    def health_check(self) -> bool:
        """Check if ChromaDB connection is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            logger.error(
                "pattern_storage_health_check_failed",
                extra={"error": str(e)}
            )
            return False
