"""Redis caching layer for SIRA performance optimization."""
import json
import hashlib
from typing import Optional, List, Dict, Any
import redis.asyncio as redis
from src.core.logging import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class RedisCache:
    """Redis-based caching for pattern retrieval and query results."""
    
    def __init__(self):
        self.redis_url = getattr(settings, 'redis_url', 'redis://sira-redis:6379/0')
        self.client: Optional[redis.Redis] = None
        self.default_ttl = 3600  # 1 hour default TTL
        
    async def connect(self):
        """Establish Redis connection."""
        if not self.client:
            try:
                self.client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                await self.client.ping()
                logger.info("redis_connected", url=self.redis_url)
            except Exception as e:
                logger.error("redis_connection_failed", error=str(e))
                self.client = None
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("redis_disconnected")
    
    def _generate_key(self, prefix: str, data: str) -> str:
        """Generate cache key from prefix and data hash."""
        data_hash = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{data_hash}"
    
    async def get_pattern_retrieval(self, query: str, n_results: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached pattern retrieval results.
        
        Args:
            query: Query text
            n_results: Number of results requested
            
        Returns:
            Cached pattern list or None if not found
        """
        if not self.client:
            return None
        
        try:
            key = self._generate_key("pattern_retrieval", f"{query}:{n_results}")
            cached = await self.client.get(key)
            
            if cached:
                logger.info("cache_hit", cache_type="pattern_retrieval", key=key[:50])
                return json.loads(cached)
            
            logger.debug("cache_miss", cache_type="pattern_retrieval", key=key[:50])
            return None
            
        except Exception as e:
            logger.error("cache_get_error", error=str(e))
            return None
    
    async def set_pattern_retrieval(
        self,
        query: str,
        n_results: int,
        patterns: List[Dict[str, Any]],
        ttl: Optional[int] = None
    ):
        """Cache pattern retrieval results.
        
        Args:
            query: Query text
            n_results: Number of results
            patterns: Retrieved patterns
            ttl: Time to live in seconds (default: 1 hour)
        """
        if not self.client:
            return
        
        try:
            key = self._generate_key("pattern_retrieval", f"{query}:{n_results}")
            ttl = ttl or self.default_ttl
            
            await self.client.setex(
                key,
                ttl,
                json.dumps(patterns)
            )
            
            logger.debug("cache_set", cache_type="pattern_retrieval", key=key[:50], ttl=ttl)
            
        except Exception as e:
            logger.error("cache_set_error", error=str(e))
    
    async def get_query_result(self, query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached query result (for identical queries in same session).
        
        Args:
            query: Query text
            session_id: Session identifier
            
        Returns:
            Cached result or None
        """
        if not self.client:
            return None
        
        try:
            key = self._generate_key("query_result", f"{session_id}:{query}")
            cached = await self.client.get(key)
            
            if cached:
                logger.info("cache_hit", cache_type="query_result", key=key[:50])
                return json.loads(cached)
            
            return None
            
        except Exception as e:
            logger.error("cache_get_error", error=str(e))
            return None
    
    async def set_query_result(
        self,
        query: str,
        session_id: str,
        result: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Cache query result.
        
        Args:
            query: Query text
            session_id: Session identifier
            result: Query result
            ttl: Time to live in seconds (default: 10 minutes for queries)
        """
        if not self.client:
            return
        
        try:
            key = self._generate_key("query_result", f"{session_id}:{query}")
            ttl = ttl or 600  # 10 minutes for query caching
            
            await self.client.setex(
                key,
                ttl,
                json.dumps(result)
            )
            
            logger.debug("cache_set", cache_type="query_result", key=key[:50], ttl=ttl)
            
        except Exception as e:
            logger.error("cache_set_error", error=str(e))
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dict with cache stats (hits, misses, keys, memory)
        """
        if not self.client:
            return {"error": "not_connected"}
        
        try:
            info = await self.client.info("stats")
            keyspace = await self.client.info("keyspace")
            
            total_hits = info.get("keyspace_hits", 0)
            total_misses = info.get("keyspace_misses", 0)
            total_requests = total_hits + total_misses
            
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            
            # Count keys by prefix
            pattern_keys = len(await self.client.keys("pattern_retrieval:*"))
            query_keys = len(await self.client.keys("query_result:*"))
            
            return {
                "connected": True,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "hit_rate_percent": round(hit_rate, 2),
                "pattern_retrieval_keys": pattern_keys,
                "query_result_keys": query_keys,
                "total_keys": info.get("db0", {}).get("keys", 0) if "db0" in keyspace else 0
            }
            
        except Exception as e:
            logger.error("cache_stats_error", error=str(e))
            return {"error": str(e)}
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache entries.
        
        Args:
            pattern: Key pattern to clear (e.g., "pattern_retrieval:*"), or None for all
        """
        if not self.client:
            return
        
        try:
            if pattern:
                keys = await self.client.keys(pattern)
                if keys:
                    await self.client.delete(*keys)
                    logger.info("cache_cleared", pattern=pattern, count=len(keys))
            else:
                await self.client.flushdb()
                logger.info("cache_cleared_all")
                
        except Exception as e:
            logger.error("cache_clear_error", error=str(e))


# Global cache instance
_cache: Optional[RedisCache] = None


async def get_cache() -> RedisCache:
    """Get or create Redis cache instance."""
    global _cache
    if _cache is None:
        _cache = RedisCache()
        await _cache.connect()
    return _cache
