import httpx
import time
import os
from dotenv import load_dotenv
load_dotenv()

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://127.0.0.1:7860")
FLOW_ID = os.getenv("FLOW_ID", "")
API_KEY = os.getenv("LANGFLOW_API_KEY", "")

async def query_mira(question: str, session_id: str) -> dict:
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY
                },
                json={
                    "input_value": question,
                    "output_type": "chat",
                    "input_type": "chat",
                    "session_id": session_id
                }
            )
            elapsed = round(time.time() - start, 2)
            if response.status_code == 200:
                data = response.json()
                try:
                    text = (data["outputs"][0]["outputs"][0]
                           ["results"]["message"]["data"]["text"])
                except Exception:
                    text = ""
                return {"success": True, "response": text, "time": elapsed}
            return {
                "success": False,
                "response": f"Error: HTTP {response.status_code}",
                "time": elapsed
            }
    except Exception as e:
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "time": round(time.time() - start, 2)
        }
