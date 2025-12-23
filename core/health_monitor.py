"""QUANTP1 v3.1 - System Health Monitor"""
import psutil
import requests
from datetime import datetime
from typing import Dict, Any
from utils.logger_setup import get_logger

logger = get_logger()


class HealthMonitor:
    """
    Monitor system health: CPU, RAM, disk, network
    """
    
    def __init__(self, cpu_threshold=80, ram_threshold=80, disk_threshold=90):
        """
        Initialize health monitor
        
        Args:
            cpu_threshold: CPU usage warning threshold (%)
            ram_threshold: RAM usage warning threshold (%)
            disk_threshold: Disk usage warning threshold (%)
        """
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold
        self.disk_threshold = disk_threshold
    
    def check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            status = "OK" if cpu_percent < self.cpu_threshold else "WARNING"
            
            return {
                "status": status,
                "usage_percent": cpu_percent,
                "cpu_count": cpu_count,
                "threshold": self.cpu_threshold
            }
        except Exception as e:
            logger.error(f"Failed to check CPU: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def check_memory(self) -> Dict[str, Any]:
        """Check RAM usage"""
        try:
            memory = psutil.virtual_memory()
            
            status = "OK" if memory.percent < self.ram_threshold else "WARNING"
            
            return {
                "status": status,
                "usage_percent": memory.percent,
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "threshold": self.ram_threshold
            }
        except Exception as e:
            logger.error(f"Failed to check memory: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def check_disk(self) -> Dict[str, Any]:
        """Check disk usage"""
        try:
            disk = psutil.disk_usage('/')
            
            status = "OK" if disk.percent < self.disk_threshold else "WARNING"
            
            return {
                "status": status,
                "usage_percent": disk.percent,
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "threshold": self.disk_threshold
            }
        except Exception as e:
            logger.error(f"Failed to check disk: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def check_network(self, test_url="https://www.google.com", timeout=5) -> Dict[str, Any]:
        """
        Check network connectivity
        
        Args:
            test_url: URL to test connectivity
            timeout: Request timeout in seconds
        """
        try:
            start_time = datetime.utcnow()
            response = requests.get(test_url, timeout=timeout)
            end_time = datetime.utcnow()
            
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            status = "OK" if response.status_code == 200 else "WARNING"
            
            return {
                "status": status,
                "latency_ms": round(latency_ms, 2),
                "status_code": response.status_code
            }
        except Exception as e:
            logger.error(f"Network check failed: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def full_health_check(self) -> Dict[str, Any]:
        """Perform complete health check"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": self.check_cpu(),
            "memory": self.check_memory(),
            "disk": self.check_disk(),
            "network": self.check_network()
        }
    
    def is_healthy(self) -> bool:
        """Check if all systems are healthy"""
        health = self.full_health_check()
        
        statuses = [
            health["cpu"]["status"],
            health["memory"]["status"],
            health["disk"]["status"],
            health["network"]["status"]
        ]
        
        return all(status == "OK" for status in statuses)
    
    def get_warnings(self) -> list:
        """Get list of current warnings"""
        health = self.full_health_check()
        warnings = []
        
        for component, data in health.items():
            if component == "timestamp":
                continue
            
            if data.get("status") == "WARNING":
                warnings.append(f"{component.upper()}: {data}")
            elif data.get("status") == "ERROR":
                warnings.append(f"{component.upper()} ERROR: {data.get('error')}")
        
        return warnings


if __name__ == "__main__":
    # Test health monitor
    monitor = HealthMonitor()
    
    print("Running health check...\n")
    health = monitor.full_health_check()
    
    for component, data in health.items():
        if component == "timestamp":
            print(f"Timestamp: {data}")
            continue
        
        print(f"\n{component.upper()}:")
        for key, value in data.items():
            print(f"  {key}: {value}")
    
    print(f"\nOverall Health: {'✅ HEALTHY' if monitor.is_healthy() else '⚠️ ISSUES DETECTED'}")
    
    warnings = monitor.get_warnings()
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("\n✅ Health monitor test completed")
