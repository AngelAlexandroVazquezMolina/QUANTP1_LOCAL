"""QUANTP1 v3.1 - API Circuit Breaker"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from utils.logger_setup import get_logger
from config.api_config import (
    MAX_CALLS_PER_DAY,
    MAX_CALLS_PER_MINUTE,
    CIRCUIT_BREAKER_THRESHOLD,
    CIRCUIT_BREAKER_TIMEOUT,
    CIRCUIT_BREAKER_HALF_OPEN_CALLS
)

logger = get_logger()


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Blocking calls due to failures
    HALF_OPEN = "half_open"  # Testing if service recovered


class APICircuitBreaker:
    """
    Circuit breaker for API calls with rate limiting
    
    Protects against:
    - Exceeding daily API limits
    - Exceeding per-minute rate limits
    - Service failures
    """
    
    def __init__(self, max_daily_calls=MAX_CALLS_PER_DAY, max_calls_per_minute=MAX_CALLS_PER_MINUTE):
        """
        Initialize circuit breaker
        
        Args:
            max_daily_calls: Maximum calls allowed per day
            max_calls_per_minute: Maximum calls per minute
        """
        self.max_daily_calls = max_daily_calls
        self.max_calls_per_minute = max_calls_per_minute
        
        # Circuit breaker state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.opened_at: Optional[datetime] = None
        self.half_open_calls = 0
        
        # Rate limiting
        self.daily_calls = 0
        self.daily_reset_time = self._get_next_reset_time()
        self.minute_calls = []  # List of timestamps
        
        logger.info(f"Circuit breaker initialized: {max_daily_calls}/day, {max_calls_per_minute}/min")
    
    def _get_next_reset_time(self) -> datetime:
        """Get next daily reset time (midnight UTC)"""
        now = datetime.utcnow()
        next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_reset
    
    def _reset_daily_counter(self):
        """Reset daily counter if needed"""
        now = datetime.utcnow()
        if now >= self.daily_reset_time:
            self.daily_calls = 0
            self.daily_reset_time = self._get_next_reset_time()
            logger.info("Daily API call counter reset")
    
    def _clean_minute_calls(self):
        """Remove calls older than 1 minute"""
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        self.minute_calls = [t for t in self.minute_calls if t > cutoff]
    
    def can_make_call(self) -> tuple[bool, str]:
        """
        Check if API call is allowed
        
        Returns:
            tuple: (allowed: bool, reason: str)
        """
        self._reset_daily_counter()
        self._clean_minute_calls()
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            # Check if timeout elapsed
            if self.opened_at and datetime.utcnow() - self.opened_at > timedelta(seconds=CIRCUIT_BREAKER_TIMEOUT):
                logger.info("Circuit breaker timeout elapsed, entering HALF_OPEN state")
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                return False, "Circuit breaker is OPEN (too many failures)"
        
        # Check daily limit
        if self.daily_calls >= self.max_daily_calls:
            return False, f"Daily limit reached ({self.daily_calls}/{self.max_daily_calls})"
        
        # Check per-minute limit
        if len(self.minute_calls) >= self.max_calls_per_minute:
            return False, f"Per-minute limit reached ({len(self.minute_calls)}/{self.max_calls_per_minute})"
        
        # In HALF_OPEN state, limit test calls
        if self.state == CircuitState.HALF_OPEN and self.half_open_calls >= CIRCUIT_BREAKER_HALF_OPEN_CALLS:
            return False, "Circuit breaker is testing (HALF_OPEN)"
        
        return True, "OK"
    
    def record_call(self):
        """Record successful API call"""
        now = datetime.utcnow()
        self.daily_calls += 1
        self.minute_calls.append(now)
        
        # If in HALF_OPEN, increment test calls
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
        
        logger.debug(f"API call recorded: {self.daily_calls}/{self.max_daily_calls} daily, "
                    f"{len(self.minute_calls)}/{self.max_calls_per_minute} per minute")
    
    def record_success(self):
        """Record successful API response"""
        if self.state == CircuitState.HALF_OPEN:
            # If enough successful test calls, close circuit
            if self.half_open_calls >= CIRCUIT_BREAKER_HALF_OPEN_CALLS:
                logger.info("Circuit breaker closing after successful test calls")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.half_open_calls = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                self.failure_count = 0
    
    def record_failure(self, error: str = ""):
        """
        Record API failure
        
        Args:
            error: Error message
        """
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        logger.warning(f"API failure recorded ({self.failure_count}/{CIRCUIT_BREAKER_THRESHOLD}): {error}")
        
        # Open circuit if threshold reached
        if self.failure_count >= CIRCUIT_BREAKER_THRESHOLD:
            if self.state != CircuitState.OPEN:
                logger.error("Circuit breaker OPENED due to repeated failures")
                self.state = CircuitState.OPEN
                self.opened_at = datetime.utcnow()
        
        # If in HALF_OPEN and failure occurs, reopen circuit
        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker reopening due to failure in HALF_OPEN state")
            self.state = CircuitState.OPEN
            self.opened_at = datetime.utcnow()
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        self._reset_daily_counter()
        self._clean_minute_calls()
        
        return {
            "state": self.state.value,
            "daily_calls": self.daily_calls,
            "max_daily_calls": self.max_daily_calls,
            "daily_remaining": self.max_daily_calls - self.daily_calls,
            "minute_calls": len(self.minute_calls),
            "max_minute_calls": self.max_calls_per_minute,
            "failure_count": self.failure_count,
            "next_reset": self.daily_reset_time.isoformat()
        }
    
    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0
        self.opened_at = None
        logger.info("Circuit breaker manually reset")


if __name__ == "__main__":
    # Test circuit breaker
    breaker = APICircuitBreaker()
    
    # Test normal operation
    for i in range(5):
        allowed, reason = breaker.can_make_call()
        if allowed:
            breaker.record_call()
            breaker.record_success()
            print(f"Call {i+1}: Success")
    
    # Test failures
    for i in range(6):
        breaker.record_failure(f"Test error {i+1}")
    
    # Check status
    status = breaker.get_status()
    print(f"\nStatus: {status}")
    
    # Try call after opening
    allowed, reason = breaker.can_make_call()
    print(f"Can make call: {allowed} ({reason})")
    
    print("\n✅ Circuit breaker test completed")
