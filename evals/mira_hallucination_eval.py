import requests, time, csv, os, re, glob
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://127.0.0.1:7860")
FLOW_ID = os.getenv("FLOW_ID", "")
API_KEY = os.getenv("LANGFLOW_API_KEY", "")
DOCS_PATH = os.getenv("DOCS_PATH", "historical_projects/*.md")

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

def extract_ground_truth(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    truth = {"project_name": "", "timeline": "", "status": "",
             "objectives": [], "milestones": [], "resources": [],
             "governance": [], "lessons": []}
    name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if name_match:
        truth["project_name"] = name_match.group(1).strip()
    for field, pattern in [
        ("timeline", r"\*\*Timeline:\*\*\s*(.+)"),
        ("status", r"\*\*Status:\*\*\s*(.+)"),
    ]:
        match = re.search(pattern, content)
        if match:
            truth[field] = match.group(1).strip()
    sections = re.split(r"
## ", content)
    for section in sections:
        lines = section.strip().split("
")
        if not lines: continue
        name = lines[0].strip().lower()
        body = "
".join(lines[1:]).strip()
        bullets = re.findall(r"^[-*]\s+(.+)$", body, re.MULTILINE)
        if "objectives" in name: truth["objectives"] = bullets
        elif "timeline" in name: truth["milestones"] = bullets
        elif "resource" in name: truth["resources"] = bullets
        elif "governance" in name: truth["governance"] = bullets
        elif "lesson" in name: truth["lessons"] = [body]
    return truth

def load_all_ground_truth():
    ground_truth = {}
    files = glob.glob(DOCS_PATH)
    print(f"Loading ground truth from {len(files)} files...")
    for filepath in sorted(files):
        truth = extract_ground_truth(filepath)
        if truth["project_name"]:
            ground_truth[truth["project_name"]] = truth
    print(f"Loaded {len(ground_truth)} projects")
    return ground_truth

def detect_hallucinations(response, truth, question_type):
    r = response.lower()
    hallucinations = []
    verified = []
    warnings = []
    if question_type == "timeline" and truth.get("timeline"):
        actual_years = re.findall(r"\d{4}", truth["timeline"])
        for year in re.findall(r"\d{4}", r):
            if year not in actual_years and int(year) > 2020:
                hallucinations.append(f"Wrong year: {year} (actual: {', '.join(actual_years)})")
            elif year in actual_years:
                verified.append(f"Year {year} correct")
    if truth.get("status"):
        actual = truth["status"].lower()
        if "completed" in actual and "in progress" in r:
            hallucinations.append("Wrong status: says in progress but project completed")
        elif "in progress" in actual and "completed successfully" in r:
            hallucinations.append("Wrong status: says completed but project in progress")
    generic_phrases = ["typically","usually","in general","best practices","generally speaking"]
    generic_count = sum(1 for p in generic_phrases if p in r)
    if generic_count >= 3:
        warnings.append(f"Generic response ({generic_count} generic phrases)")
    return {
        "hallucinations": hallucinations, "verified_facts": verified,
        "warnings": warnings, "is_hallucinating": len(hallucinations) > 0,
        "has_warnings": len(warnings) > 0, "verified_count": len(verified),
    }

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
        return {"success": False, "response": "", "time": elapsed}
    except Exception as e:
        return {"success": False, "response": str(e), "time": round(time.time()-start, 2)}

def run_hallucination_evals():
    print("=" * 65)
    print("MIRA Hallucination Detection Eval")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    ground_truth_db = load_all_ground_truth()
    projects = list(ground_truth_db.keys())
    results = []
    passed = 0
    failed = 0
    hallucinated = 0
    total_time = 0
    for i, project in enumerate(projects):
        truth = ground_truth_db[project]
        print(f"\n[{i+1}/{len(projects)}] {project[:55]}")
        print("-" * 45)
        for q_type, template in QUESTION_TEMPLATES:
            question = template.format(project=project)
            session_id = f"hall-{i}-{q_type}-{int(time.time())}"
            print(f"  {q_type:<12}", end=" ", flush=True)
            result = query_mira(question, session_id)
            hall_check = detect_hallucinations(result["response"], truth, q_type)
            r = result["response"].lower()
            generic_phrases = ["not available","not retrieved","unable to retrieve",
                             "cannot provide","no specific","i apologize"]
            is_generic = any(p in r for p in generic_phrases)
            project_words = [w for w in project.lower().split() if len(w) > 4]
            has_project = any(w in r for w in project_words)
            type_kw = {
                "timeline": ["q1","q2","q3","q4","2024","2025","2026"],
                "objectives": ["objective","goal","success","achieve"],
                "governance": ["governance","hil","checkpoint","human"],
                "lessons": ["lesson","insight","learned","reflect"],
                "resources": ["team","member","capital","investment"],
            }
            has_kw = any(kw in r for kw in type_kw.get(q_type, []))
            content_pass = not is_generic and has_project and has_kw and len(result["response"]) > 200
            if content_pass: passed += 1
            else: failed += 1
            if hall_check["is_hallucinating"]: hallucinated += 1
            total_time += result["time"]
            status = "PASS" if content_pass else "FAIL"
            hall_str = " | HALLUCINATION" if hall_check["is_hallucinating"] else ""
            warn_str = " | WARNING" if hall_check["has_warnings"] else ""
            print(f"{status}{hall_str}{warn_str} ({result['time']}s)")
            for h in hall_check["hallucinations"]:
                print(f"    HALL: {h}")
            results.append({
                "project": project, "question_type": q_type,
                "question": question, "content_pass": content_pass,
                "is_hallucinating": hall_check["is_hallucinating"],
                "has_warnings": hall_check["has_warnings"],
                "hallucinations": "; ".join(hall_check["hallucinations"]),
                "warnings": "; ".join(hall_check["warnings"]),
                "verified_facts": "; ".join(hall_check["verified_facts"]),
                "verified_count": hall_check["verified_count"],
                "response_length": len(result["response"]),
                "response_time": result["time"],
                "response_preview": result["response"][:300],
            })
            time.sleep(2)
    total = len(results)
    print("\n" + "=" * 65)
    print("HALLUCINATION EVAL SUMMARY")
    print("=" * 65)
    print(f"Total:         {total}")
    print(f"Content pass:  {passed} ({passed/total*100:.1f}%)")
    print(f"Hallucinated:  {hallucinated} ({hallucinated/total*100:.1f}%)")
    print(f"Avg time:      {total_time/total:.1f}s")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"evals/results/mira_hallucination_{timestamp}.csv"
    os.makedirs("evals/results", exist_ok=True)
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved: {csv_file}")
    print("=" * 65)
    return results

if __name__ == "__main__":
    run_hallucination_evals()
