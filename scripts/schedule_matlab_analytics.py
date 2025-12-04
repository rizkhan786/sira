#!/usr/bin/env python3
"""
MATLAB Analytics Scheduler

Automatically runs MATLAB analytics at scheduled intervals and sends notifications.

Usage:
    python scripts/schedule_matlab_analytics.py --mode daily
    python scripts/schedule_matlab_analytics.py --mode threshold  # Run when 100+ new episodes
    python scripts/schedule_matlab_analytics.py --run-now  # Manual trigger
"""

import os
import subprocess
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/matlab_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MATLABScheduler:
    """Scheduler for MATLAB analytics execution."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.episodes_file = self.project_root / "data" / "matlab" / "episodes.mat"
        self.state_file = self.project_root / "data" / "matlab" / "scheduler_state.json"
        self.matlab_script = self.project_root / "matlab" / "sira_dashboard.m"
        
        # Load state
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load scheduler state (last run time, episode count)."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "last_run": None,
            "last_episode_count": 0,
            "total_runs": 0
        }
    
    def _save_state(self):
        """Save scheduler state."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _get_episode_count(self) -> int:
        """Get current episode count from episodes.mat file."""
        if not self.episodes_file.exists():
            logger.warning(f"Episodes file not found: {self.episodes_file}")
            return 0
        
        try:
            # Use scipy to read .mat file
            from scipy.io import loadmat
            data = loadmat(str(self.episodes_file))
            
            # Episodes are stored as struct array
            if 'episodes' in data:
                episodes = data['episodes']
                return len(episodes[0]) if episodes.size > 0 else 0
            return 0
        except Exception as e:
            logger.error(f"Failed to read episodes file: {e}")
            return 0
    
    def should_run(self, mode: str) -> tuple[bool, str]:
        """
        Determine if MATLAB analytics should run.
        
        Args:
            mode: 'daily', 'weekly', 'threshold', or 'manual'
        
        Returns:
            (should_run, reason)
        """
        current_count = self._get_episode_count()
        last_run = self.state.get("last_run")
        last_count = self.state.get("last_episode_count", 0)
        
        if mode == "manual":
            return True, "Manual trigger"
        
        # Check if episodes file exists
        if current_count == 0:
            return False, "No episodes available yet"
        
        # Threshold mode: Run when 100+ new episodes
        if mode == "threshold":
            new_episodes = current_count - last_count
            if new_episodes >= 100:
                return True, f"{new_episodes} new episodes (threshold: 100)"
            return False, f"Only {new_episodes} new episodes (threshold: 100)"
        
        # Time-based modes
        if last_run is None:
            return True, "First run"
        
        last_run_time = datetime.fromisoformat(last_run)
        hours_since_last_run = (datetime.now() - last_run_time).total_seconds() / 3600
        
        if mode == "daily" and hours_since_last_run >= 24:
            return True, f"Daily schedule (last run: {hours_since_last_run:.1f}h ago)"
        
        if mode == "weekly" and hours_since_last_run >= 168:  # 7 days
            return True, f"Weekly schedule (last run: {hours_since_last_run/24:.1f} days ago)"
        
        return False, f"Too soon (last run: {hours_since_last_run:.1f}h ago)"
    
    def run_matlab_analytics(self) -> bool:
        """
        Execute MATLAB analytics dashboard.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info("Starting MATLAB Analytics Execution")
        logger.info("=" * 60)
        
        # Check if MATLAB is available
        if not self._check_matlab_available():
            logger.error("MATLAB not found. Please install MATLAB or add to PATH.")
            return False
        
        # Prepare MATLAB command
        matlab_cmd = [
            "matlab",
            "-batch",
            f"cd('{self.project_root}'); sira_dashboard(); exit;"
        ]
        
        try:
            logger.info(f"Executing: {' '.join(matlab_cmd)}")
            
            # Run MATLAB in batch mode
            result = subprocess.run(
                matlab_cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ MATLAB analytics completed successfully")
                logger.info("Output:")
                logger.info(result.stdout)
                
                # Update state
                self.state["last_run"] = datetime.now().isoformat()
                self.state["last_episode_count"] = self._get_episode_count()
                self.state["total_runs"] = self.state.get("total_runs", 0) + 1
                self._save_state()
                
                # Send success notification
                self._send_notification(
                    "✅ MATLAB Analytics Complete",
                    f"Report generated successfully. Episodes analyzed: {self.state['last_episode_count']}"
                )
                
                return True
            else:
                logger.error(f"❌ MATLAB analytics failed with code {result.returncode}")
                logger.error("Error output:")
                logger.error(result.stderr)
                
                # Send failure notification
                self._send_notification(
                    "❌ MATLAB Analytics Failed",
                    f"Error: {result.stderr[:200]}"
                )
                
                return False
        
        except subprocess.TimeoutExpired:
            logger.error("❌ MATLAB analytics timed out (10 minutes)")
            self._send_notification("❌ MATLAB Analytics Timeout", "Execution exceeded 10 minutes")
            return False
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            self._send_notification("❌ MATLAB Analytics Error", str(e))
            return False
    
    def _check_matlab_available(self) -> bool:
        """Check if MATLAB is available in PATH."""
        try:
            result = subprocess.run(
                ["matlab", "-help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _send_notification(self, title: str, message: str):
        """
        Send notification (console + optional email/Slack).
        
        TODO: Add email/Slack notifications based on config.
        """
        logger.info(f"\n📧 NOTIFICATION: {title}")
        logger.info(f"   {message}\n")
        
        # Could add email/Slack integration here
        # Example:
        # if settings.email_notifications:
        #     send_email(title, message)
    
    def get_status(self) -> dict:
        """Get scheduler status."""
        current_count = self._get_episode_count()
        last_run = self.state.get("last_run")
        
        status = {
            "current_episode_count": current_count,
            "last_episode_count": self.state.get("last_episode_count", 0),
            "new_episodes": current_count - self.state.get("last_episode_count", 0),
            "last_run": last_run,
            "total_runs": self.state.get("total_runs", 0),
            "matlab_available": self._check_matlab_available(),
            "episodes_file_exists": self.episodes_file.exists()
        }
        
        if last_run:
            last_run_time = datetime.fromisoformat(last_run)
            hours_since = (datetime.now() - last_run_time).total_seconds() / 3600
            status["hours_since_last_run"] = hours_since
        
        return status


def main():
    parser = argparse.ArgumentParser(description="MATLAB Analytics Scheduler")
    parser.add_argument(
        "--mode",
        choices=["daily", "weekly", "threshold", "manual"],
        default="daily",
        help="Scheduling mode (default: daily)"
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Force run immediately (ignores schedule)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show scheduler status and exit"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (keeps checking schedule)"
    )
    
    args = parser.parse_args()
    
    # Initialize scheduler
    scheduler = MATLABScheduler()
    
    # Status check
    if args.status:
        status = scheduler.get_status()
        print("\n" + "=" * 60)
        print("MATLAB Analytics Scheduler Status")
        print("=" * 60)
        print(f"Episodes: {status['current_episode_count']} (new: {status['new_episodes']})")
        print(f"Last run: {status['last_run'] or 'Never'}")
        if status.get('hours_since_last_run'):
            print(f"Hours since last run: {status['hours_since_last_run']:.1f}")
        print(f"Total runs: {status['total_runs']}")
        print(f"MATLAB available: {'✅' if status['matlab_available'] else '❌'}")
        print(f"Episodes file: {'✅' if status['episodes_file_exists'] else '❌'}")
        print("=" * 60 + "\n")
        return
    
    # Force run
    if args.run_now:
        logger.info("Manual execution requested")
        success = scheduler.run_matlab_analytics()
        exit(0 if success else 1)
    
    # Daemon mode (keeps checking)
    if args.daemon:
        logger.info(f"Starting scheduler in daemon mode (mode: {args.mode})")
        
        check_interval = 3600  # Check every hour
        
        while True:
            should_run, reason = scheduler.should_run(args.mode)
            
            if should_run:
                logger.info(f"Running analytics: {reason}")
                scheduler.run_matlab_analytics()
            else:
                logger.debug(f"Skipping run: {reason}")
            
            logger.info(f"Next check in {check_interval/3600:.1f} hours")
            time.sleep(check_interval)
    
    # Single check mode (default)
    else:
        should_run, reason = scheduler.should_run(args.mode)
        
        if should_run:
            logger.info(f"Running analytics: {reason}")
            success = scheduler.run_matlab_analytics()
            exit(0 if success else 1)
        else:
            logger.info(f"Skipping run: {reason}")
            exit(0)


if __name__ == "__main__":
    main()
