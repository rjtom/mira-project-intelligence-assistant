import chromadb, glob, os, re
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "/Users/thomasraju/.langflow/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "MIRARAG")
DOCS_PATH = os.getenv("DOCS_PATH", "/Users/thomasraju/Desktop/mira-project-intelligence-assistant/historical_projects/*.md")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CACHE_PATH = os.getenv("EMBEDDING_CACHE_PATH", "/Users/thomasraju/.langflow/embedding_cache")

def run():
    print("MIRA Full Re-ingest")
    confirm = input("Type YES to confirm: ")
    if confirm != "YES":
        print("Cancelled")
        return
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try: client.delete_collection(COLLECTION_NAME)
    except Exception: pass
    col = client.create_collection(COLLECTION_NAME, metadata={'hnsw:space': 'cosine'})
    if os.path.exists(CACHE_PATH):
        for cf in glob.glob(f"{CACHE_PATH}/*.json"): os.remove(cf)
    oai = OpenAI(api_key=OPENAI_API_KEY)
    doc_files = sorted(glob.glob(DOCS_PATH))
    total = 0
    for filepath in doc_files:
        filename = os.path.basename(filepath)
        print(f"Ingesting: {filename}")
        content = open(filepath).read()
        header = content.split('##')[0].strip()
        sections = re.split(r'
(?=## )', content)
        base_id = int(datetime.now().timestamp())
        for i, section in enumerate(sections):
            if not section.strip(): continue
            chunk = (f"{header}

{section.strip()}"
                    if not section.startswith('#') else section.strip())
            emb = oai.embeddings.create(input=chunk[:8000], model='text-embedding-3-small')
            col.add(documents=[chunk], embeddings=[emb.data[0].embedding],
                   ids=[f"{filename.replace('.md','')}_{base_id}_{i}"],
                   metadatas=[{'source': filename}])
            total += 1
    print(f"Done. Total chunks: {col.count()}")

if __name__ == "__main__":
    run()
