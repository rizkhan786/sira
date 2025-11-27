"""Redis caching layer for SIRA performance optimization.

Provides caching for pattern retrieval, embeddings, and frequent queries
to reduce latency by 30%+ through intelligent caching.
"""
import os
import json
import hashlib
from typing import Optional, Any, List, Dict
from datetime import timedelta
import redis.asyncio as redis
from src.core.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Manages Redis caching for SIRA components."""
    
    # Cache TTLs (time-to-live)
    TTL_PATTERN_RETRIEVAL = 3600  # 1 hour - patterns change slowly
    TTL_EMBEDDINGS = 7200  # 2 hours - embeddings are stable
    TTL_QUERY_RESULT = 1800  # 30 minutes - query results
    TTL_METRICS = 300  # 5 minutes - metrics update frequently
    
    # Cache key prefixes
    PREFIX_PATTERN = "pattern:"
    PREFIX_EMBEDDING = "embed:"
    PREFIX_QUERY = "query:"
    PREFIX_METRICS = "metrics:"
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        enabled: bool = True
    ):
        """Initialize cache manager.
        
        Args:
            host: Redis host (default from env: REDIS_HOST)
            port: Redis port (default from env: REDIS_PORT)
            db: Redis database number (default: 0)
            enabled: Whether caching is enabled (default: True)
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", 6379))
        self.db = db
        self.enabled = enabled
        self._client: Optional[redis.Redis] = None
        
        # Stats
        self._hits = 0
        self._misses = 0
        
        logger.info(
            "cache_manager_initialized",
            host=self.host,
            port=self.port,
            enabled=self.enabled
        )
    
    async def connect(self):
        """Connect to Redis."""
        if not self.enabled:
            logger.info("cache_disabled")
            return
        
        try:
            self._client = await redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            
            # Test connection
            await self._client.ping()
            logger.info("cache_connected", host=self.host, port=self.port)
            
        except Exception as e:
            logger.error(
                "cache_connection_failed",
                error=str(e),
                host=self.host,
                port=self.port
            )
            self.enabled = False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            logger.info("cache_disconnected")
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """Create cache key with prefix and hash.
        
        Args:
            prefix: Key prefix (e.g., "pattern:")
            identifier: Identifier string
            
        Returns:
            Full cache key
        """
        # Hash identifier to keep keys short and consistent
        hash_obj = hashlib.sha256(identifier.encode())
        hash_str = hash_obj.hexdigest()[:16]
        return f"{prefix}{hash_str}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.enabled or not self._client:
            return None
        
        try:
            value = await self._client.get(key)
            
            if value is not None:
                self._hits += 1
                logger.debug("cache_hit", key=key[:20])
                return json.loads(value)
            else:
                self._misses += 1
                logger.debug("cache_miss", key=key[:20])
                return None
                
        except Exception as e:
            logger.warning("cache_get_error", error=str(e), key=key[:20])
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = None
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self._client:
            return False
        
        try:
            serialized = json.dumps(value)
            
            if ttl:
                await self._client.setex(key, ttl, serialized)
            else:
                await self._client.set(key, serialized)
            
            logger.debug("cache_set", key=key[:20], ttl=ttl)
            return True
            
        except Exception as e:
            logger.warning("cache_set_error", error=str(e), key=key[:20])
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled or not self._client:
            return False
        
        try:
            result = await self._client.delete(key)
            logger.debug("cache_delete", key=key[:20], deleted=result > 0)
            return result > 0
        except Exception as e:
            logger.warning("cache_delete_error", error=str(e), key=key[:20])
            return False
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "pattern:*")
        """
        if not self.enabled or not self._client:
            return
        
        try:
            cursor = 0
            deleted = 0
            
            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                
                if keys:
                    deleted += await self._client.delete(*keys)
                
                if cursor == 0:
                    break
            
            logger.info("cache_invalidated", pattern=pattern, deleted=deleted)
            
        except Exception as e:
            logger.warning("cache_invalidate_error", error=str(e), pattern=pattern)
    
    # Pattern retrieval caching
    
    async def get_patterns(
        self,
        query: str,
        n_results: int,
        min_quality: float
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached pattern retrieval results.
        
        Args:
            query: Query text
            n_results: Number of results
            min_quality: Minimum quality threshold
            
        Returns:
            Cached patterns or None
        """
        identifier = f"{query}:{n_results}:{min_quality}"
        key = self._make_key(self.PREFIX_PATTERN, identifier)
        return await self.get(key)
    
    async def set_patterns(
        self,
        query: str,
        n_results: int,
        min_quality: float,
        patterns: List[Dict[str, Any]]
    ) -> bool:
        """Cache pattern retrieval results.
        
        Args:
            query: Query text
            n_results: Number of results
            min_quality: Minimum quality threshold
            patterns: Pattern retrieval results
            
        Returns:
            True if cached successfully
        """
        identifier = f"{query}:{n_results}:{min_quality}"
        key = self._make_key(self.PREFIX_PATTERN, identifier)
        return await self.set(key, patterns, ttl=self.TTL_PATTERN_RETRIEVAL)
    
    # Embedding caching
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached text embedding.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Cached embedding or None
        """
        key = self._make_key(self.PREFIX_EMBEDDING, text)
        return await self.get(key)
    
    async def set_embedding(self, text: str, embedding: List[float]) -> bool:
        """Cache text embedding.
        
        Args:
            text: Text
            embedding: Embedding vector
            
        Returns:
            True if cached successfully
        """
        key = self._make_key(self.PREFIX_EMBEDDING, text)
        return await self.set(key, embedding, ttl=self.TTL_EMBEDDINGS)
    
    # Query result caching
    
    async def get_query_result(
        self,
        query: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached query result.
        
        Args:
            query: Query text
            session_id: Session ID
            
        Returns:
            Cached result or None
        """
        identifier = f"{query}:{session_id}"
        key = self._make_key(self.PREFIX_QUERY, identifier)
        return await self.get(key)
    
    async def set_query_result(
        self,
        query: str,
        session_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """Cache query result.
        
        Args:
            query: Query text
            session_id: Session ID
            result: Query result
            
        Returns:
            True if cached successfully
        """
        identifier = f"{query}:{session_id}"
        key = self._make_key(self.PREFIX_QUERY, identifier)
        return await self.set(key, result, ttl=self.TTL_QUERY_RESULT)
    
    # Metrics caching
    
    async def get_metrics(self, metric_type: str) -> Optional[Dict[str, Any]]:
        """Get cached metrics.
        
        Args:
            metric_type: Type of metrics (e.g., "core", "tier1")
            
        Returns:
            Cached metrics or None
        """
        key = f"{self.PREFIX_METRICS}{metric_type}"
        return await self.get(key)
    
    async def set_metrics(
        self,
        metric_type: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Cache metrics.
        
        Args:
            metric_type: Type of metrics
            metrics: Metrics data
            
        Returns:
            True if cached successfully
        """
        key = f"{self.PREFIX_METRICS}{metric_type}"
        return await self.set(key, metrics, ttl=self.TTL_METRICS)
    
    # Cache statistics
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "enabled": self.enabled,
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "connected": self._client is not None
        }
    
    async def get_redis_info(self) -> Dict[str, Any]:
        """Get Redis server info.
        
        Returns:
            Dictionary with Redis stats
        """
        if not self.enabled or not self._client:
            return {"error": "Cache not enabled or not connected"}
        
        try:
            info = await self._client.info()
            return {
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.warning("cache_info_error", error=str(e))
            return {"error": str(e)}
    
    async def flush(self):
        """Flush all cache data (use with caution)."""
        if not self.enabled or not self._client:
            return
        
        try:
            await self._client.flushdb()
            logger.warning("cache_flushed")
        except Exception as e:
            logger.error("cache_flush_error", error=str(e))
    
    def reset_stats(self):
        """Reset cache statistics."""
        self._hits = 0
        self._misses = 0
        logger.info("cache_stats_reset")
