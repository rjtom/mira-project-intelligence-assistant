import chromadb, glob, os, re, json, hashlib
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "/Users/thomasraju/.langflow/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "MIRARAG")
DOCS_PATH = os.getenv("DOCS_PATH", "/Users/thomasraju/Desktop/mira-project-intelligence-assistant/historical_projects/*.md")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CACHE_PATH = os.getenv("EMBEDDING_CACHE_PATH", "/Users/thomasraju/.langflow/embedding_cache")
STATE_FILE = os.path.expanduser("~/.langflow/mira_ingest_state.json")

def get_hash(f):
    with open(f, 'rb') as fh: return hashlib.md5(fh.read()).hexdigest()

def load_state():
    return json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump(state, open(STATE_FILE, 'w'), indent=2)

def run(force=False):
    print(f"MIRA Smart Re-ingest — {'FORCE' if force else 'CHANGED ONLY'}")
    state = load_state()
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    cols = [c.name for c in client.list_collections()]
    col = (client.get_collection(COLLECTION_NAME) if COLLECTION_NAME in cols
           else client.create_collection(COLLECTION_NAME, metadata={'hnsw:space': 'cosine'}))
    oai = OpenAI(api_key=OPENAI_API_KEY)
    doc_files = sorted(glob.glob(DOCS_PATH))
    changed = [f for f in doc_files if force or state.get(os.path.basename(f)) != get_hash(f)]
    print(f"Changed: {len(changed)} | Unchanged: {len(doc_files)-len(changed)}")
    new_state = dict(state)
    total = 0
    for filepath in changed:
        filename = os.path.basename(filepath)
        print(f"Ingesting: {filename}")
        existing = col.get(where={"source": {"$eq": filename}})
        if existing['ids']: col.delete(ids=existing['ids'])
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
        new_state[filename] = get_hash(filepath)
    if os.path.exists(CACHE_PATH):
        for cf in glob.glob(f"{CACHE_PATH}/*.json"): os.remove(cf)
    save_state(new_state)
    print(f"Done. Added: {total} | Total: {col.count()}")

if __name__ == "__main__":
    import sys
    run(force="--force" in sys.argv)
