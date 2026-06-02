import requests, time, os
from dotenv import load_dotenv
load_dotenv()

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://127.0.0.1:7860")
FLOW_ID = os.getenv("FLOW_ID", "")
API_KEY = os.getenv("LANGFLOW_API_KEY", "")
PROJECT = "ForgeNova EV Battery Gigafactory Expansion"
QUESTIONS = [
    f"What is the timeline for {PROJECT}?",
    f"What are the objectives for {PROJECT}?",
    f"What governance checkpoints were used in {PROJECT}?",
    f"What lessons were learned from {PROJECT}?",
    f"What are the resource requirements for {PROJECT}?",
]

def query_mira(question, session_id):
    start = time.time()
    try:
        r = requests.post(
            f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",
            headers={"Content-Type": "application/json", "x-api-key": API_KEY},
            json={"input_value": question, "output_type": "chat",
                  "input_type": "chat", "session_id": session_id},
            timeout=120
        )
        elapsed = round(time.time() - start, 2)
        if r.status_code == 200:
            try:
                text = r.json()["outputs"][0]["outputs"][0]["results"]["message"]["data"]["text"]
            except Exception:
                text = ""
            return {"success": True, "response": text, "time": elapsed}
        return {"success": False, "response": f"HTTP {r.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "response": str(e), "time": round(time.time()-start, 2)}

if __name__ == "__main__":
    print("=" * 60)
    print(f"MIRA Single Project Test: {PROJECT}")
    print("=" * 60)
    for i, question in enumerate(QUESTIONS, 1):
        print(f"
[{i}/{len(QUESTIONS)}] {question}")
        print("-" * 40)
        result = query_mira(question, f"test-{i}-{int(time.time())}")
        print(f"Time: {result['time']}s")
        print(result["response"][:400])
        time.sleep(2)
    print("
Test complete!")
