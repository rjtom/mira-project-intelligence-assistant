import chromadb
import glob
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "/Users/thomasraju/.langflow/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "MIRARAG")
DOCS_PATH = os.getenv("DOCS_PATH", "/Users/thomasraju/Desktop/mira-project-intelligence-assistant/historical_projects/*.md")

def run_health_check():
    print("=" * 55)
    print(f"MIRA Health Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    issues = []
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collections = [c.name for c in client.list_collections()]
        print(f"Collections: {collections}")
        if COLLECTION_NAME not in collections:
            print(f"MISSING collection {COLLECTION_NAME}")
            return False
        col = client.get_collection(COLLECTION_NAME)
        total = col.count()
        print(f"Total chunks: {total}")
        doc_files = glob.glob(DOCS_PATH)
        print(f"Project files: {len(doc_files)}")
        all_data = col.get()
        sources = set(m.get('source','') for m in all_data['metadatas'] if m)
        print(f"Unique sources: {len(sources)}")
        missing = [os.path.basename(f) for f in doc_files
                   if os.path.basename(f) not in sources]
        if missing:
            for m in missing:
                print(f"MISSING: {m}")
            issues.extend(missing)
        else:
            print(f"All {len(doc_files)} projects present")
        print(f"Status: {'HEALTHY' if not issues else 'UNHEALTHY'}")
        return not issues
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    healthy = run_health_check()
    exit(0 if healthy else 1)
