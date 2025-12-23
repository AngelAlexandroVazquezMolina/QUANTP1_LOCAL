"""QUANTP1 v3.1 - Cleanup Old Logs"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.paths_config import LOGS_DIR


def cleanup_logs(days: int = 30, dry_run: bool = False):
    """
    Delete log files older than specified days
    
    Args:
        days: Delete files older than this many days
        dry_run: If True, only show what would be deleted
    """
    if not LOGS_DIR.exists():
        print(f"❌ Logs directory not found: {LOGS_DIR}")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    print(f"🗑️  Cleaning logs older than {days} days (before {cutoff_date.strftime('%Y-%m-%d')})")
    print(f"📁 Directory: {LOGS_DIR}")
    
    if dry_run:
        print("🔍 DRY RUN - No files will be deleted\n")
    else:
        print()
    
    deleted_count = 0
    deleted_size = 0
    
    for log_file in LOGS_DIR.glob("*.log*"):
        if log_file.is_file():
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                file_size = log_file.stat().st_size
                
                if dry_run:
                    print(f"   Would delete: {log_file.name} ({file_size / 1024:.2f} KB)")
                else:
                    try:
                        log_file.unlink()
                        print(f"   ✅ Deleted: {log_file.name} ({file_size / 1024:.2f} KB)")
                        deleted_count += 1
                        deleted_size += file_size
                    except Exception as e:
                        print(f"   ❌ Failed to delete {log_file.name}: {e}")
    
    print()
    if dry_run:
        print(f"Would delete {deleted_count} files")
    else:
        print(f"✅ Deleted {deleted_count} files ({deleted_size / 1024 / 1024:.2f} MB)")


def main():
    parser = argparse.ArgumentParser(description='Cleanup old log files')
    parser.add_argument('--days', type=int, default=30, help='Delete files older than N days (default: 30)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("   QUANTP1 v3.1 - Log Cleanup")
    print("=" * 50)
    print()
    
    cleanup_logs(args.days, args.dry_run)


if __name__ == "__main__":
    main()
