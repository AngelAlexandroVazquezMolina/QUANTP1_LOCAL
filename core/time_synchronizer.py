"""QUANTP1 v3.1 - Time Synchronizer (NTP without admin)"""
import ntplib
from datetime import datetime, timedelta
from typing import Optional
from utils.logger_setup import get_logger

logger = get_logger()


class TimeSynchronizer:
    """
    NTP time synchronization without modifying system clock
    
    Maintains internal offset to true time
    """
    
    def __init__(self, ntp_server="pool.ntp.org", sync_interval=3600):
        """
        Initialize time synchronizer
        
        Args:
            ntp_server: NTP server address
            sync_interval: Seconds between syncs (default 1 hour)
        """
        self.ntp_server = ntp_server
        self.sync_interval = sync_interval
        self.offset: Optional[float] = None
        self.last_sync: Optional[datetime] = None
        self.ntp_client = ntplib.NTPClient()
    
    def sync_time(self) -> bool:
        """
        Synchronize with NTP server
        
        Returns:
            bool: True if successful
        """
        try:
            response = self.ntp_client.request(self.ntp_server, version=3, timeout=10)
            
            # Calculate offset between system time and NTP time
            self.offset = response.offset
            self.last_sync = datetime.utcnow()
            
            logger.info(f"NTP sync successful: offset = {self.offset:.3f}s")
            return True
            
        except Exception as e:
            logger.error(f"NTP sync failed: {e}")
            return False
    
    def get_true_time(self) -> datetime:
        """
        Get current time adjusted for NTP offset
        
        Returns:
            datetime: True time (UTC)
        """
        system_time = datetime.utcnow()
        
        if self.offset is None:
            logger.warning("No NTP offset available, using system time")
            return system_time
        
        # Apply offset
        true_time = system_time + timedelta(seconds=self.offset)
        return true_time
    
    def needs_sync(self) -> bool:
        """Check if time sync is needed"""
        if self.last_sync is None:
            return True
        
        elapsed = datetime.utcnow() - self.last_sync
        return elapsed.total_seconds() >= self.sync_interval
    
    def get_status(self) -> dict:
        """Get synchronization status"""
        return {
            "offset": self.offset,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "needs_sync": self.needs_sync(),
            "server": self.ntp_server
        }


if __name__ == "__main__":
    # Test time synchronizer
    sync = TimeSynchronizer()
    
    print("Syncing with NTP...")
    if sync.sync_time():
        true_time = sync.get_true_time()
        system_time = datetime.utcnow()
        
        print(f"System Time: {system_time.isoformat()}")
        print(f"True Time:   {true_time.isoformat()}")
        print(f"Offset:      {sync.offset:.3f}s")
        
        status = sync.get_status()
        print(f"\nStatus: {status}")
        print("\n✅ Time synchronizer test completed")
    else:
        print("❌ Failed to sync with NTP")
