"""QUANTP1 v3.1 - Atomic State Manager with Anti-Corruption"""
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logger_setup import get_logger

logger = get_logger()


class StateManager:
    """
    Atomic state persistence with corruption protection
    
    Features:
    - Atomic writes using temp files
    - Automatic backups
    - Corruption recovery
    - fsync() for data integrity
    """
    
    def __init__(self, state_file: Path, backup_file: Optional[Path] = None):
        """
        Initialize state manager
        
        Args:
            state_file: Path to main state file
            backup_file: Path to backup file (optional)
        """
        self.state_file = state_file
        self.backup_file = backup_file or state_file.with_suffix('.backup.json')
        self.temp_file = state_file.with_suffix('.tmp.json')
        
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty state if doesn't exist
        if not self.state_file.exists():
            self._initialize_state()
    
    def _initialize_state(self):
        """Initialize empty state file"""
        initial_state = {
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "version": "3.1",
            "open_trades": [],
            "closed_trades": [],
            "daily_pnl": 0.0,
            "starting_balance": 0.0,
            "current_balance": 0.0,
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "api_calls_today": 0,
            "last_signal_id": 0
        }
        self.save_state(initial_state)
        logger.info("Initialized new state file")
    
    def load_state(self) -> Dict[str, Any]:
        """
        Load state with corruption recovery
        
        Returns:
            dict: State data
        """
        # Try loading main file
        try:
            return self._load_from_file(self.state_file)
        except Exception as e:
            logger.warning(f"Failed to load main state file: {e}")
            
            # Try loading backup
            if self.backup_file.exists():
                try:
                    logger.info("Attempting to restore from backup...")
                    state = self._load_from_file(self.backup_file)
                    
                    # Restore backup to main file
                    self.save_state(state)
                    logger.info("Successfully restored from backup")
                    return state
                except Exception as backup_error:
                    logger.error(f"Backup also corrupted: {backup_error}")
            
            # If all else fails, initialize new state
            logger.warning("Creating new state file")
            self._initialize_state()
            return self.load_state()
    
    def _load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and validate JSON from file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            dict: Parsed JSON data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ["created_at", "last_updated", "open_trades", "closed_trades"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return data
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """
        Atomically save state with backup
        
        Args:
            state: State dictionary to save
            
        Returns:
            bool: True if successful
        """
        try:
            # Update timestamp
            state["last_updated"] = datetime.utcnow().isoformat()
            
            # Write to temp file first
            with open(self.temp_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Backup existing file if it exists
            if self.state_file.exists():
                shutil.copy2(self.state_file, self.backup_file)
            
            # Atomic rename (atomic on POSIX, near-atomic on Windows)
            shutil.move(str(self.temp_file), str(self.state_file))
            
            logger.debug(f"State saved successfully to {self.state_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            
            # Clean up temp file if it exists
            if self.temp_file.exists():
                try:
                    self.temp_file.unlink()
                except:
                    pass
            
            return False
    
    def update_state(self, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields in state
        
        Args:
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if successful
        """
        state = self.load_state()
        state.update(updates)
        return self.save_state(state)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a specific value from state
        
        Args:
            key: Key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            Value from state or default
        """
        state = self.load_state()
        return state.get(key, default)
    
    def set_value(self, key: str, value: Any) -> bool:
        """
        Set a specific value in state
        
        Args:
            key: Key to set
            value: Value to set
            
        Returns:
            bool: True if successful
        """
        return self.update_state({key: value})


if __name__ == "__main__":
    from config.paths_config import STATE_FILE, STATE_BACKUP
    
    # Test state manager
    manager = StateManager(STATE_FILE, STATE_BACKUP)
    
    # Save test state
    test_state = {
        "open_trades": [{"id": 1, "symbol": "EURUSD"}],
        "daily_pnl": 150.50
    }
    manager.save_state(test_state)
    
    # Load state
    loaded = manager.load_state()
    print(f"Loaded state: {json.dumps(loaded, indent=2)}")
    
    # Update value
    manager.set_value("test_key", "test_value")
    print(f"Test key: {manager.get_value('test_key')}")
    
    print("\n✅ State manager test completed")
