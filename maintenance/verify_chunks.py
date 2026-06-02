import chromadb
import glob
import os
from dotenv import load_dotenv
load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "/Users/thomasraju/.langflow/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "MIRARAG")
DOCS_PATH = os.getenv("DOCS_PATH", "/Users/thomasraju/Desktop/mira-project-intelligence-assistant/historical_projects/*.md")

def verify():
    print("=" * 55)
    print("MIRA Chunk Verification")
    print("=" * 55)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    col = client.get_collection(COLLECTION_NAME)
    all_data = col.get()
    source_chunks = {}
    for i, meta in enumerate(all_data['metadatas']):
        if meta:
            source = meta.get('source', '')
            source_chunks[source] = source_chunks.get(source, 0) + 1
    doc_files = sorted(glob.glob(DOCS_PATH))
    issues = []
    for filepath in doc_files:
        filename = os.path.basename(filepath)
        count = source_chunks.get(filename, 0)
        if count == 0:
            issues.append(filename)
            print(f"MISSING: {filename}")
        elif count < 5:
            print(f"LOW: {filename} ({count} chunks)")
        else:
            print(f"OK: {filename} ({count} chunks)")
    print(f"
Total chunks: {col.count()}")
    print(f"Projects: {len(source_chunks)}/{len(doc_files)}")
    print(f"Status: {'PASS' if not issues else 'FAIL'}")
    return not issues

if __name__ == "__main__":
    passed = verify()
    exit(0 if passed else 1)
