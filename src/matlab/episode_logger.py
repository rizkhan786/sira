"""Episode logger for MATLAB analytics integration."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Episode:
    """Represents a single query processing episode."""
    timestamp: str
    query: str
    patterns_retrieved: int
    pattern_ids: List[str]
    reasoning_steps: List[Dict[str, Any]]
    quality_scores: List[float]
    iteration_count: int
    timing_ms: Dict[str, float]
    response: str
    session_id: str
    query_id: str


class EpisodeLogger:
    """Logs query episodes for MATLAB analysis."""
    
    def __init__(
        self,
        log_path: str = "./data/matlab/episodes.mat",
        batch_size: int = 10,
        export_interval_seconds: int = 3600
    ):
        """Initialize episode logger.
        
        Args:
            log_path: Path to .mat file for episode logs
            batch_size: Number of episodes before auto-export
            export_interval_seconds: Time interval for auto-export
        """
        self.log_path = Path(log_path)
        self.batch_size = batch_size
        self.export_interval = export_interval_seconds
        self.episodes: List[Episode] = []
        self.last_export = datetime.now(timezone.utc)
        
        # Ensure directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "episode_logger_initialized",
            log_path=str(self.log_path),
            batch_size=batch_size
        )
    
    def log_episode(
        self,
        query_id: str,
        session_id: str,
        query: str,
        response: str,
        reasoning_steps: List[Dict[str, Any]],
        patterns_retrieved: List[Dict[str, Any]],
        quality_scores: List[float],
        iteration_count: int,
        timing_ms: Dict[str, float]
    ):
        """Log a query processing episode.
        
        Args:
            query_id: Unique query identifier
            session_id: Session identifier
            query: User query text
            response: Generated response
            reasoning_steps: List of reasoning steps
            patterns_retrieved: Retrieved pattern metadata
            quality_scores: Quality scores per iteration
            iteration_count: Number of refinement iterations
            timing_ms: Timing breakdown in milliseconds
        """
        # Extract pattern IDs
        pattern_ids = [p.get("pattern_id", "") for p in patterns_retrieved]
        
        episode = Episode(
            timestamp=datetime.now(timezone.utc).isoformat(),
            query=query,
            patterns_retrieved=len(patterns_retrieved),
            pattern_ids=pattern_ids,
            reasoning_steps=reasoning_steps,
            quality_scores=quality_scores,
            iteration_count=iteration_count,
            timing_ms=timing_ms,
            response=response,
            session_id=session_id,
            query_id=query_id
        )
        
        self.episodes.append(episode)
        
        logger.info(
            "episode_logged",
            query_id=query_id,
            episode_count=len(self.episodes),
            quality=quality_scores[-1] if quality_scores else 0
        )
        
        # Check if should export
        if len(self.episodes) >= self.batch_size:
            self._export_episodes()
        elif (datetime.now(timezone.utc) - self.last_export).total_seconds() >= self.export_interval:
            self._export_episodes()
    
    def _export_episodes(self):
        """Export episodes to .mat file."""
        if not self.episodes:
            return
        
        try:
            # Try scipy first (preferred for MATLAB compatibility)
            try:
                import scipy.io as sio
                self._export_with_scipy(sio)
            except ImportError:
                # Fallback to JSON if scipy not available
                logger.warning("scipy_not_available", fallback="json")
                self._export_to_json()
            
            logger.info(
                "episodes_exported",
                count=len(self.episodes),
                path=str(self.log_path)
            )
            
            self.episodes.clear()
            self.last_export = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(
                "episode_export_failed",
                error=str(e),
                episode_count=len(self.episodes)
            )
    
    def _export_with_scipy(self, sio):
        """Export episodes using scipy.io.savemat.
        
        Args:
            sio: scipy.io module
        """
        # Convert episodes to MATLAB-compatible structure
        matlab_data = {
            'episodes': [self._episode_to_dict(ep) for ep in self.episodes],
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'episode_count': len(self.episodes)
        }
        
        # Save to .mat file
        sio.savemat(
            str(self.log_path),
            matlab_data,
            do_compression=True,
            oned_as='column'
        )
    
    def _export_to_json(self):
        """Fallback: Export episodes to JSON format."""
        json_path = self.log_path.with_suffix('.json')
        
        data = {
            'episodes': [self._episode_to_dict(ep) for ep in self.episodes],
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'episode_count': len(self.episodes)
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("episodes_exported_json", path=str(json_path))
    
    def _episode_to_dict(self, episode: Episode) -> Dict[str, Any]:
        """Convert Episode to dictionary for export.
        
        Args:
            episode: Episode object
            
        Returns:
            Dictionary representation
        """
        return {
            'timestamp': episode.timestamp,
            'query_id': episode.query_id,
            'session_id': episode.session_id,
            'query': episode.query,
            'patterns_retrieved': episode.patterns_retrieved,
            'pattern_ids': episode.pattern_ids,
            'reasoning_steps': episode.reasoning_steps,
            'quality_scores': episode.quality_scores,
            'iteration_count': episode.iteration_count,
            'timing_ms': episode.timing_ms,
            'response': episode.response
        }
    
    def flush(self):
        """Manually flush all pending episodes."""
        if self.episodes:
            self._export_episodes()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current logger statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'pending_episodes': len(self.episodes),
            'batch_size': self.batch_size,
            'log_path': str(self.log_path),
            'last_export': self.last_export.isoformat()
        }
