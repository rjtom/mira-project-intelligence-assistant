import requests, time, csv, os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://127.0.0.1:7860")
FLOW_ID = os.getenv("FLOW_ID", "")
API_KEY = os.getenv("LANGFLOW_API_KEY", "")

PROJECTS = [
    "ForgeNova EV Battery Gigafactory Expansion",
    "ForgeNova Autonomous Driving Platform Development",
    "ForgeNova Electric SUV Launch Program",
    "ForgeNova Quantum Secure Software Platform",
    "ForgeNova Hydrogen Fuel Cell Vehicle Program",
    "ForgeNova Connected Car Ecosystem Platform",
    "ForgeNova Battery Recycling & Second-Life Program",
    "ForgeNova AI Driver Assistance System",
    "ForgeNova Global ERP System Migration",
    "ForgeNova Multi-Cloud Infrastructure Modernization",
    "ForgeNova Enterprise Cybersecurity Enhancement Program",
    "ForgeNova Data Analytics & Business Intelligence Platform",
    "ForgeNova DevOps Pipeline Transformation",
    "ForgeNova Digital Twin Factory Initiative",
    "ForgeNova Employee Experience Platform",
    "ForgeNova Global Supply Chain Visibility Platform",
    "ForgeNova Software Defined Vehicle Platform",
    "ForgeNova Next-Generation Battery Technology Program",
    "ForgeNova Urban Air Mobility Initiative",
    "ForgeNova Blockchain-Enabled Supply Chain Transparency",
    "ForgeNova AI-Powered Quality Control System",
    "ForgeNova Enterprise Sustainability Dashboard",
    "ForgeNova Autonomous Logistics Network",
    "ForgeNova Circular Economy Platform",
    "ForgeNova AI Ethics and Governance Framework",
    "ForgeNova Advanced Sustainability Intelligence Platform",
]

QUESTION_TEMPLATES = [
    ("timeline", "What is the timeline for {project}?"),
    ("objectives", "What are the objectives for {project}?"),
    ("governance", "What governance checkpoints were used in {project}?"),
    ("lessons", "What lessons were learned from {project}?"),
    ("resources", "What are the resource requirements for {project}?"),
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

def evaluate_response(response, question_type, project):
    r = response.lower()
    p = project.lower()
    generic_phrases = ["not available","not retrieved","unable to retrieve",
                      "cannot provide","no specific","i apologize","technical issue"]
    is_generic = any(ph in r for ph in generic_phrases)
    project_words = [w for w in p.split() if len(w) > 4]
    has_project = any(w in r for w in project_words)
    type_keywords = {
        "timeline": ["q1","q2","q3","q4","month","phase","2024","2025","2026"],
        "objectives": ["objective","goal","success","criteria","achieve"],
        "governance": ["governance","hil","checkpoint","review","human"],
        "lessons": ["lesson","insight","learned","reflect"],
        "resources": ["team","member","capital","investment","partner"],
    }
    has_kw = any(kw in r for kw in type_keywords.get(question_type, []))
    passed = not is_generic and has_project and has_kw and len(response) > 200
    return {"passed": passed, "is_generic": is_generic,
            "has_project_name": has_project, "has_keywords": has_kw,
            "response_length": len(response)}

def run_evals():
    print("=" * 60)
    print("MIRA Basic Eval Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total queries: {len(PROJECTS) * len(QUESTION_TEMPLATES)}")
    print("=" * 60)
    results = []
    passed = 0
    failed = 0
    total_time = 0
    for i, project in enumerate(PROJECTS):
        print(f"\n[{i+1}/{len(PROJECTS)}] {project}")
        print("-" * 40)
        for q_type, template in QUESTION_TEMPLATES:
            question = template.format(project=project)
            session_id = f"eval-{i}-{q_type}-{int(time.time())}"
            print(f"  {q_type}...", end=" ", flush=True)
            result = query_mira(question, session_id)
            ev = evaluate_response(result["response"], q_type, project)
            status = "PASS" if ev["passed"] else "FAIL"
            print(f"{status} ({result['time']}s)")
            if ev["passed"]: passed += 1
            else: failed += 1
            total_time += result["time"]
            results.append({
                "project": project, "question_type": q_type,
                "question": question, "passed": ev["passed"],
                "is_generic": ev["is_generic"],
                "has_project_name": ev["has_project_name"],
                "has_keywords": ev["has_keywords"],
                "response_length": ev["response_length"],
                "response_time": result["time"],
                "success": result["success"],
                "response_preview": result["response"][:300],
            })
            time.sleep(2)
    total = len(results)
    print("\n" + "=" * 60)
    print("MIRA EVAL SUMMARY")
    print("=" * 60)
    print(f"Total:    {total}")
    print(f"Passed:   {passed} ({passed/total*100:.1f}%)")
    print(f"Failed:   {failed}")
    print(f"Avg time: {total_time/total:.1f}s")
    print("\nBy Question Type:")
    for q_type, _ in QUESTION_TEMPLATES:
        tr = [r for r in results if r["question_type"] == q_type]
        tp = sum(1 for r in tr if r["passed"])
        at = sum(r["response_time"] for r in tr) / len(tr)
        print(f"  {q_type:<12} {tp}/{len(tr)} ({tp/len(tr)*100:.0f}%) avg {at:.1f}s")
    failed_list = [r for r in results if not r["passed"]]
    if failed_list:
        print(f"\nFailed ({len(failed_list)}):")
        for r in failed_list:
            print(f"  {r['project'][:40]} -- {r['question_type']}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"evals/results/mira_eval_{timestamp}.csv"
    os.makedirs("evals/results", exist_ok=True)
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved: {csv_file}")
    print("=" * 60)
    return results

if __name__ == "__main__":
    run_evals()
