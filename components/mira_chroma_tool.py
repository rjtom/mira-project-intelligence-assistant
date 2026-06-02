from langflow.custom import Component
from langflow.inputs import StrInput, SecretStrInput
from langflow.template import Output
from langflow.field_typing import Tool
from langchain.tools import StructuredTool
from pydantic import BaseModel
import chromadb
from openai import OpenAI
import hashlib
import json
import os


class MiraChromaTool(Component):
    display_name = "MIRA_Project_RAG"
    description = "Direct Chroma retrieval tool for MIRA agents"
    icon = "search"

    inputs = [
        StrInput(
            name="chroma_path",
            display_name="Chroma Path",
            value="/Users/thomasraju/.langflow/chroma_db",
        ),
        StrInput(
            name="collection_name",
            display_name="Collection Name",
            value="MIRARAG",
        ),
        SecretStrInput(
            name="openai_api_key",
            display_name="OpenAI API Key",
            value="",
        ),
        StrInput(
            name="embedding_model",
            display_name="Embedding Model",
            value="text-embedding-3-small",
        ),
        StrInput(
            name="n_results",
            display_name="Number of Results",
            value="8",
        ),
        StrInput(
            name="cache_path",
            display_name="Cache Path",
            value="/Users/thomasraju/.langflow/embedding_cache",
        ),
    ]

    outputs = [
        Output(
            display_name="Toolset",
            name="toolset",
            method="build_toolset",
            types=["Tool"],
        ),
    ]

    def build_toolset(self) -> Tool:
        chroma_path = self.chroma_path or "/Users/thomasraju/.langflow/chroma_db"
        collection_name = self.collection_name or "MIRARAG"
        openai_api_key = self.openai_api_key
        embedding_model = self.embedding_model or "text-embedding-3-small"
        n_results = int(self.n_results or "8")
        cache_path = self.cache_path or "/Users/thomasraju/.langflow/embedding_cache"

        def get_embedding(text, oai, cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            cache_key = hashlib.md5(
                f"{text}{embedding_model}".encode()
            ).hexdigest()
            cache_file = os.path.join(cache_dir, f"{cache_key}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
            response = oai.embeddings.create(
                input=text, model=embedding_model
            )
            embedding = response.data[0].embedding
            with open(cache_file, 'w') as f:
                json.dump(embedding, f)
            return embedding

        def retrieve_project_data(question: str) -> str:
            try:
                chroma_client = chromadb.PersistentClient(path=chroma_path)
                available = [c.name for c in chroma_client.list_collections()]
                if collection_name not in available:
                    return (
                        f"Collection '{collection_name}' not found. "
                        f"Available: {available}"
                    )

                col = chroma_client.get_collection(collection_name)
                oai = OpenAI(api_key=openai_api_key)

                # Clear stale cache for this question
                os.makedirs(cache_path, exist_ok=True)
                cache_key = hashlib.md5(
                    f"{question}{embedding_model}".encode()
                ).hexdigest()
                cache_file = os.path.join(cache_path, f"{cache_key}.json")
                if os.path.exists(cache_file):
                    os.remove(cache_file)

                query_embedding = get_embedding(question, oai, cache_path)
                question_lower = question.lower()

                # ─────────────────────────────
                # Cross-project detection
                # ─────────────────────────────
                cross_project_keywords = [
                    'all projects', 'which projects', 'list projects',
                    'projects are', 'currently in progress', 'in progress',
                    'all forgenova', 'status of all', 'overview of all',
                    'compare', 'across projects', 'multiple projects',
                    'planning phase', 'completed projects', 'active projects',
                    'how many projects', 'all active', 'all completed',
                    'project list', 'every project', 'summarize all',
                ]

                is_cross_project = any(
                    kw in question_lower for kw in cross_project_keywords
                )

                if is_cross_project:
                    results = col.query(
                        query_embeddings=[query_embedding],
                        n_results=min(50, col.count()),
                    )
                    docs = []
                    seen_sources = set()
                    for doc, meta in zip(
                        results['documents'][0],
                        results['metadatas'][0]
                    ):
                        if doc is None:
                            continue
                        source = meta.get('source', '') if meta else ''
                        if source not in seen_sources:
                            docs.append(doc)
                            seen_sources.add(source)
                    return "\n\n---\n\n".join(docs)

                # ─────────────────────────────
                # Single project query
                # ─────────────────────────────
                stop_words = {
                    'what', 'were', 'from', 'the', 'for', 'this', 'that',
                    'with', 'have', 'about', 'tell', 'give', 'show', 'list',
                    'are', 'did', 'does', 'how', 'when', 'where', 'which',
                    'used', 'using', 'please', 'can', 'could', 'would',
                    'should', 'will', 'their', 'there', 'they', 'them',
                    'then', 'than', 'been', 'being', 'was', 'had', 'has',
                    'its', 'also', 'more', 'some', 'into', 'over', 'after',
                    'before', 'during',
                }

                words = [
                    w.strip('?.,!') for w in question_lower.split()
                    if len(w.strip('?.,!')) > 3
                    and w.strip('?.,!') not in stop_words
                ]

                phrase_map = {
                    'gigafactory': ['gigafactory'],
                    'battery expansion': ['battery', 'expansion'],
                    'autonomous driving': ['autonomous', 'driving'],
                    'hydrogen': ['hydrogen'],
                    'recycling': ['recycling'],
                    'cybersecurity': ['cybersecurity'],
                    'digital twin': ['digital', 'twin'],
                    'supply chain': ['supply', 'chain'],
                    'erp': ['erp'],
                    'devops': ['devops', 'pipeline'],
                    'devops pipeline': ['devops', 'pipeline', 'transformation'],
                    'pipeline transformation': ['pipeline', 'devops'],
                    'electric suv': ['electric', 'suv'],
                    'connected car': ['connected', 'car'],
                    'urban air': ['urban', 'air'],
                    'blockchain': ['blockchain'],
                    'quantum': ['quantum'],
                    'quality control': ['quality', 'control'],
                    'employee experience': ['employee', 'experience'],
                    'data analytics': ['data', 'analytics'],
                    'multi-cloud': ['cloud', 'infrastructure'],
                    'sustainability': ['sustainability'],
                    'sdv': ['sdv'],
                    'circular economy': ['circular', 'economy'],
                    'logistics': ['logistics'],
                    'ai ethics': ['ethics', 'governance'],
                    'driver assistance': ['driver', 'assistance'],
                    'next-generation battery': ['next', 'generation', 'battery'],
                }

                key_phrases = []
                for phrase, terms in phrase_map.items():
                    if phrase in question_lower:
                        key_phrases.extend(terms)

                all_search_terms = list(set(words + key_phrases))

                # Score sources
                all_data = col.get()
                source_scores = {}

                for i, doc in enumerate(all_data['documents']):
                    if doc is None:
                        continue
                    meta = all_data['metadatas'][i]
                    source = meta.get('source', '') if meta else ''
                    if not source:
                        continue
                    doc_lower = doc.lower()
                    score = sum(
                        1 for w in all_search_terms if w in doc_lower
                    )
                    if source not in source_scores:
                        source_scores[source] = 0
                    source_scores[source] = max(source_scores[source], score)

                sorted_sources = sorted(
                    source_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                top_sources = [s[0] for s in sorted_sources[:2] if s[1] > 0]

                # Retrieve using col.get() — reliable with all ID types
                if top_sources:
                    try:
                        source_data = col.get(
                            where={"source": {"$in": top_sources}}
                        )
                        valid_docs = [
                            d for d in source_data['documents']
                            if d is not None
                        ]
                        if valid_docs:
                            return "\n\n---\n\n".join(valid_docs)
                    except Exception:
                        pass

                # Fallback — embedding search
                results = col.query(
                    query_embeddings=[query_embedding],
                    n_results=20
                )
                docs = [
                    d for d in results['documents'][0]
                    if d is not None
                ]

                if not docs:
                    return "No data found in project documentation."

                return "\n\n---\n\n".join(docs)

            except Exception as e:
                return f"Retrieval error: {str(e)}"

        class ProjectQuery(BaseModel):
            question: str

        tool = StructuredTool.from_function(
            func=retrieve_project_data,
            name="MIRA_Project_RAG",
            description=(
                "ALWAYS call this tool for ANY ForgeNova project question. "
                "Never answer without calling this tool first. "
                "Returns project documentation including timelines, "
                "objectives, governance, lessons learned, resources, "
                "and critical thinking analysis."
            ),
            args_schema=ProjectQuery,
        )

        return tool
