import glob
import os
import time
from dotenv import load_dotenv
load_dotenv()

CACHE_PATH = os.getenv("EMBEDDING_CACHE_PATH", "/Users/thomasraju/.langflow/embedding_cache")
MAX_CACHE_SIZE_MB = 500
MAX_CACHE_AGE_DAYS = 7

def get_stats():
    if not os.path.exists(CACHE_PATH):
        return {"file_count": 0, "size_mb": 0, "oldest_days": 0}
    files = glob.glob(f"{CACHE_PATH}/*.json")
    if not files:
        return {"file_count": 0, "size_mb": 0, "oldest_days": 0}
    total_size = sum(os.path.getsize(f) for f in files)
    mtimes = [os.path.getmtime(f) for f in files]
    return {
        "file_count": len(files),
        "size_mb": round(total_size / 1024 / 1024, 2),
        "oldest_days": round((time.time() - min(mtimes)) / 86400, 1)
    }

def clear_all():
    files = glob.glob(f"{CACHE_PATH}/*.json")
    for f in files:
        os.remove(f)
    return len(files)

def clear_expired(max_days=None):
    if max_days is None:
        max_days = MAX_CACHE_AGE_DAYS
    cutoff = time.time() - (max_days * 86400)
    files = glob.glob(f"{CACHE_PATH}/*.json")
    removed = 0
    for f in files:
        if os.path.getmtime(f) < cutoff:
            os.remove(f)
            removed += 1
    return removed

def run(action="status"):
    print(f"MIRA Cache Manager — {action.upper()}")
    stats = get_stats()
    print(f"Files: {stats['file_count']} | Size: {stats['size_mb']} MB | Oldest: {stats['oldest_days']} days")
    if action == "auto":
        if stats['size_mb'] > MAX_CACHE_SIZE_MB:
            removed = clear_all()
            print(f"Auto-cleared {removed} files (size exceeded)")
        elif stats['oldest_days'] > MAX_CACHE_AGE_DAYS:
            removed = clear_expired()
            print(f"Auto-cleared {removed} expired files")
        else:
            print("Cache healthy")
    elif action == "clear-all":
        removed = clear_all()
        print(f"Cleared {removed} files")
    elif action == "clear-expired":
        removed = clear_expired()
        print(f"Cleared {removed} expired files")

if __name__ == "__main__":
    import sys
    action = "status"
    if "--auto" in sys.argv: action = "auto"
    elif "--clear-all" in sys.argv: action = "clear-all"
    elif "--clear-expired" in sys.argv: action = "clear-expired"
    run(action)
