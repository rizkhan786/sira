"""Database repository for SIRA."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import asyncpg
from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseRepository:
    """Repository for database operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.pool: Optional[asyncpg.Pool] = None
        
    async def connect(self):
        """Initialize database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=self.settings.postgres_host,
                port=self.settings.postgres_port,
                user=self.settings.postgres_user,
                password=self.settings.postgres_password,
                database=self.settings.postgres_db,
                min_size=2,
                max_size=10
            )
            logger.info("database_pool_created", host=self.settings.postgres_host)
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("database_pool_closed")
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session.
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            Session ID (UUID)
        """
        await self.connect()
        
        session_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sessions (id, user_id, created_at, last_activity)
                VALUES ($1, $2, $3, $3)
            """, session_id, user_id, created_at)
        
        logger.info("session_created", session_id=session_id, user_id=user_id)
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        await self.connect()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, user_id, created_at, last_activity
                FROM sessions
                WHERE id = $1
            """, session_id)
        
        if row:
            return {
                "id": str(row["id"]),
                "user_id": row["user_id"],
                "created_at": row["created_at"].isoformat(),
                "last_activity": row["last_activity"].isoformat()
            }
        return None
    
    async def update_session_activity(self, session_id: str):
        """Update session's last activity timestamp."""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE sessions
                SET last_activity = $1
                WHERE id = $2
            """, datetime.now(timezone.utc), session_id)
    
    async def save_query(
        self,
        session_id: str,
        query_text: str,
        response_text: str,
        reasoning_steps: List[Dict[str, Any]],
        processing_time: float,
        token_usage: Dict[str, int],
        quality_score: float = None,
        quality_breakdown: Dict[str, Any] = None
    ) -> str:
        """Save a query and its response.
        
        Args:
            session_id: Session identifier
            query_text: User's query
            response_text: System response
            reasoning_steps: List of reasoning steps
            processing_time: Processing time in seconds
            token_usage: Token usage statistics
            
        Returns:
            Query ID (UUID)
        """
        await self.connect()
        
        query_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        import json
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO queries (
                    id, session_id, query_text, response_text,
                    reasoning_steps, timestamp, processing_time, token_usage,
                    quality_score, quality_breakdown
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
                query_id,
                session_id,
                query_text,
                response_text,
                json.dumps(reasoning_steps),  # Convert to JSON string
                timestamp,
                processing_time,
                json.dumps(token_usage),  # Convert to JSON string
                quality_score,
                json.dumps(quality_breakdown) if quality_breakdown else None
            )
        
        logger.info(
            "query_saved",
            query_id=query_id,
            session_id=session_id,
            processing_time=processing_time
        )
        
        return query_id
    
    async def get_session_queries(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent queries for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of queries to return
            
        Returns:
            List of query records
        """
        await self.connect()
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id, query_text, response_text, reasoning_steps,
                    timestamp, processing_time, token_usage
                FROM queries
                WHERE session_id = $1
                ORDER BY timestamp DESC
                LIMIT $2
            """, session_id, limit)
        
        import json
        return [
            {
                "id": str(row["id"]),
                "query_text": row["query_text"],
                "response_text": row["response_text"],
                "reasoning_steps": json.loads(row["reasoning_steps"]) if isinstance(row["reasoning_steps"], str) else row["reasoning_steps"],
                "timestamp": row["timestamp"].isoformat(),
                "processing_time": row["processing_time"],
                "token_usage": json.loads(row["token_usage"]) if isinstance(row["token_usage"], str) else row["token_usage"]
            }
            for row in rows
        ]
    
    async def save_metrics(
        self,
        query_id: str,
        response_quality: Optional[float] = None,
        user_feedback: Optional[int] = None
    ):
        """Save metrics for a query.
        
        Args:
            query_id: Query identifier
            response_quality: Calculated quality score (0-1)
            user_feedback: User feedback (-1, 0, 1)
        """
        await self.connect()
        
        timestamp = datetime.now(timezone.utc)
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO metrics (query_id, timestamp, response_quality, user_feedback)
                VALUES ($1, $2, $3, $4)
            """, query_id, timestamp, response_quality, user_feedback)
        
        logger.info("metrics_saved", query_id=query_id)


# Global repository instance
_repository: Optional[DatabaseRepository] = None


async def get_repository() -> DatabaseRepository:
    """Get or create database repository."""
    global _repository
    if _repository is None:
        _repository = DatabaseRepository()
    return _repository
