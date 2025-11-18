"""Configuration reader for MATLAB-generated optimizations."""
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone
import json
from src.core.logging import get_logger

logger = get_logger(__name__)


class ConfigReader:
    """Reads and applies MATLAB-generated configuration."""
    
    def __init__(
        self,
        config_path: str = "./data/matlab/optimized_config.json",
        reload_interval: int = 60
    ):
        """Initialize config reader.
        
        Args:
            config_path: Path to MATLAB-generated config file
            reload_interval: Seconds between config reload checks
        """
        self.config_path = Path(config_path)
        self.reload_interval = reload_interval
        self.current_config: Optional[Dict[str, Any]] = None
        self.last_reload = datetime.now(timezone.utc)
        self.last_modified = None
        
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try initial load
        self._try_load_config()
        
        logger.info(
            "config_reader_initialized",
            config_path=str(self.config_path),
            reload_interval=reload_interval
        )
    
    def get_config(self, key: str = None, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (dot-separated for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Check if should reload
        self._check_reload()
        
        if not self.current_config:
            return default
        
        if key is None:
            return self.current_config
        
        # Handle dot-separated nested keys
        keys = key.split('.')
        value = self.current_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def _check_reload(self):
        """Check if config file should be reloaded."""
        now = datetime.now(timezone.utc)
        
        # Check reload interval
        if (now - self.last_reload).total_seconds() < self.reload_interval:
            return
        
        self.last_reload = now
        
        # Check if file exists
        if not self.config_path.exists():
            return
        
        # Check if file was modified
        try:
            mtime = self.config_path.stat().st_mtime
            
            if self.last_modified is None or mtime > self.last_modified:
                self._try_load_config()
        except Exception as e:
            logger.error("config_reload_check_failed", error=str(e))
    
    def _try_load_config(self):
        """Attempt to load configuration from file."""
        if not self.config_path.exists():
            logger.debug(
                "config_file_not_found",
                path=str(self.config_path)
            )
            return
        
        try:
            with open(self.config_path, 'r') as f:
                new_config = json.load(f)
            
            # Update configuration
            old_config = self.current_config
            self.current_config = new_config
            self.last_modified = self.config_path.stat().st_mtime
            
            if old_config != new_config:
                logger.info(
                    "config_updated",
                    path=str(self.config_path),
                    keys=list(new_config.keys())
                )
            else:
                logger.debug("config_unchanged")
                
        except json.JSONDecodeError as e:
            logger.error(
                "config_parse_error",
                path=str(self.config_path),
                error=str(e)
            )
        except Exception as e:
            logger.error(
                "config_load_error",
                path=str(self.config_path),
                error=str(e)
            )
    
    def apply_config_to_dict(
        self,
        base_config: Dict[str, Any],
        matlab_overrides: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Apply MATLAB config overrides to base configuration.
        
        Args:
            base_config: Base configuration dictionary
            matlab_overrides: List of keys to override (None = all)
            
        Returns:
            Updated configuration dictionary
        """
        if not self.current_config:
            return base_config
        
        updated = base_config.copy()
        
        for key, value in self.current_config.items():
            # Check if this key should be overridden
            if matlab_overrides is None or key in matlab_overrides:
                updated[key] = value
                logger.debug(
                    "config_override_applied",
                    key=key,
                    value=value
                )
        
        return updated
    
    def get_stats(self) -> Dict[str, Any]:
        """Get config reader statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'config_path': str(self.config_path),
            'config_loaded': self.current_config is not None,
            'last_reload': self.last_reload.isoformat(),
            'last_modified': (
                datetime.fromtimestamp(self.last_modified, tz=timezone.utc).isoformat()
                if self.last_modified
                else None
            ),
            'reload_interval': self.reload_interval
        }
