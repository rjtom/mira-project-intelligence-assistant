import requests
import json
import time
import csv
import os
import re
import glob
from datetime import datetime
from dotenv import load_dotenv
load_dotenv("/Users/thomasraju/mira-project-intelligence-assistant/.env", override=False)

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://127.0.0.1:7860")
FLOW_ID = os.getenv("FLOW_ID", "")
API_KEY = os.getenv("LANGFLOW_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DOCS_PATH = os.getenv("DOCS_PATH", "historical_projects/*.md")
ENABLE_LLM_JUDGE = os.getenv("ENABLE_LLM_JUDGE", "true").lower() == "true"
ENABLE_RISK_EVALS = os.getenv("ENABLE_RISK_EVALS", "true").lower() == "true"

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

RAG_TEMPLATES = [
    ("timeline", "What is the timeline for {project}?"),
    ("objectives", "What are the objectives for {project}?"),
    ("governance", "What governance checkpoints were used in {project}?"),
    ("lessons", "What lessons were learned from {project}?"),
    ("resources", "What are the resource requirements for {project}?"),
]
RISK_TEMPLATE = ("risks", "What are the major risks for {project}?")


def query_mira(question, session_id):
    start = time.time()
    try:
        r = requests.post(
            f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",
            headers={"Content-Type": "application/json", "x-api-key": API_KEY},
            json={
                "input_value": question,
                "output_type": "chat",
                "input_type": "chat",
                "session_id": session_id
            },
            timeout=120
        )
        elapsed = round(time.time() - start, 2)
        if r.status_code == 200:
            try:
                text = (r.json()["outputs"][0]["outputs"][0]
                       ["results"]["message"]["data"]["text"])
            except Exception:
                text = ""
            return {"success": True, "response": text, "time": elapsed}
        return {"success": False, "response": f"HTTP {r.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "response": str(e),
                "time": round(time.time() - start, 2)}


def extract_ground_truth(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    truth = {
        "project_name": "",
        "timeline": "",
        "status": "",
        "objectives": [],
        "milestones": [],
        "resources": [],
        "governance": [],
        "lessons": [],
        "full_content": content
    }
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
    sep = "\n## "
    sections = content.split(sep)
    for section in sections:
        lines = section.strip().split("\n")
        if not lines:
            continue
        name = lines[0].strip().lower()
        body = "\n".join(lines[1:]).strip()
        bullets = re.findall(r"^[-*]\s+(.+)$", body, re.MULTILINE)
        if "objectives" in name:
            truth["objectives"] = bullets
        elif "timeline" in name:
            truth["milestones"] = bullets
        elif "resource" in name:
            truth["resources"] = bullets
        elif "governance" in name:
            truth["governance"] = bullets
        elif "lesson" in name:
            truth["lessons"] = [body]
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


def get_ground_truth_text(truth, question_type):
    if question_type == "timeline":
        gt = (f"Timeline: {truth.get('timeline', 'N/A')}\n"
              f"Status: {truth.get('status', 'N/A')}\n"
              "Milestones:\n" +
              "\n".join(f"- {m}" for m in truth.get("milestones", [])))
    elif question_type == "objectives":
        gt = "Objectives:\n" + "\n".join(
            f"- {o}" for o in truth.get("objectives", []))
    elif question_type == "governance":
        gt = "Governance:\n" + "\n".join(
            f"- {g}" for g in truth.get("governance", []))
    elif question_type == "lessons":
        gt = "Lessons:\n" + "\n".join(
            truth.get("lessons", ["No lessons found"]))
    elif question_type == "resources":
        gt = "Resources:\n" + "\n".join(
            f"- {r}" for r in truth.get("resources", []))
    else:
        gt = "Risk data from Google Sheets"
    return gt[:2000]


def llm_judge(question, ground_truth, response, question_type):
    if not ANTHROPIC_API_KEY:
        return {}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = (
            f"You are an expert evaluator for MIRA AI project intelligence.\n"
            f"Question type: {question_type}\n"
            f"Question: {question}\n"
            f"Ground truth: {ground_truth}\n"
            f"MIRA response: {response}\n\n"
            f"Score each 0-10. Return ONLY valid JSON:\n"
            f'{{"factual_accuracy":0,"groundedness":0,"completeness":0,'
            f'"hallucination_free":0,"relevance":0,"overall":0,'
            f'"issues":[""],"reasoning":""}}'
        )
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        return {"overall": 0, "reasoning": f"Judge error: {e}", "issues": []}


def content_pass_check(response, q_type, project):
    r = response.lower()
    generic_phrases = [
        "not available", "not retrieved", "unable to retrieve",
        "cannot provide", "no specific", "i apologize", "technical issue"
    ]
    is_generic = any(p in r for p in generic_phrases)
    project_words = [w for w in project.lower().split() if len(w) > 4]
    has_project = any(w in r for w in project_words)
    type_keywords = {
        "timeline": ["q1", "q2", "q3", "q4", "month", "phase", "2024", "2025", "2026"],
        "objectives": ["objective", "goal", "success", "criteria", "achieve"],
        "governance": ["governance", "hil", "checkpoint", "review", "human"],
        "lessons": ["lesson", "insight", "learned", "reflect"],
        "resources": ["team", "member", "capital", "investment", "partner"],
        "risks": ["risk", "score", "mitigation", "impact", "likelihood"],
    }
    has_kw = any(kw in r for kw in type_keywords.get(q_type, []))
    return not is_generic and has_project and has_kw and len(response) > 200


def run_eval_suite():
    print("=" * 65)
    print("MIRA Complete Eval Suite -- RAG + Risk + LLM Judge")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"LLM Judge: {'ON' if ENABLE_LLM_JUDGE else 'OFF'}")
    print("=" * 65)

    rag_truth = load_all_ground_truth()
    projects = list(rag_truth.keys())
    all_templates = RAG_TEMPLATES.copy()
    if ENABLE_RISK_EVALS:
        all_templates.append(RISK_TEMPLATE)

    total_queries = len(projects) * len(all_templates)
    print(f"Projects: {len(projects)} | Questions: {len(all_templates)} | Total: {total_queries}")
    print("=" * 65)

    results = []
    passed = 0
    failed = 0
    judge_scores = []
    total_time = 0

    for i, project in enumerate(projects):
        truth = rag_truth.get(project, {})
        print(f"\n[{i+1}/{len(projects)}] {project[:55]}")
        print("-" * 45)

        for q_type, template in all_templates:
            question = template.format(project=project)
            session_id = f"suite-{i}-{q_type}-{int(time.time())}"
            print(f"  {q_type:<12}", end=" ", flush=True)

            result = query_mira(question, session_id)
            content_ok = content_pass_check(result["response"], q_type, project)

            judge_result = {}
            if ENABLE_LLM_JUDGE and result["success"] and result["response"]:
                gt_text = get_ground_truth_text(truth, q_type)
                judge_result = llm_judge(
                    question, gt_text, result["response"], q_type
                )
                if judge_result.get("overall", 0) > 0:
                    judge_scores.append(judge_result["overall"])

            if content_ok:
                passed += 1
            else:
                failed += 1
            total_time += result["time"]

            status = "PASS" if content_ok else "FAIL"
            judge_str = ""
            if judge_result:
                judge_str = f" | Judge: {judge_result.get('overall', 0):.1f}/10"
            print(f"{status}{judge_str} ({result['time']}s)")

            for issue in judge_result.get("issues", [])[:1]:
                if issue:
                    print(f"    Issue: {issue[:80]}")

            results.append({
                "eval_type": "RISK" if q_type == "risks" else "RAG",
                "project": project,
                "question_type": q_type,
                "question": question,
                "content_pass": content_ok,
                "judge_overall": judge_result.get("overall", "N/A"),
                "judge_factual_accuracy": judge_result.get("factual_accuracy", "N/A"),
                "judge_groundedness": judge_result.get("groundedness", "N/A"),
                "judge_completeness": judge_result.get("completeness", "N/A"),
                "judge_hallucination_free": judge_result.get("hallucination_free", "N/A"),
                "judge_relevance": judge_result.get("relevance", "N/A"),
                "judge_issues": "; ".join(judge_result.get("issues", [])),
                "judge_reasoning": judge_result.get("reasoning", ""),
                "response_length": len(result["response"]),
                "response_time": result["time"],
                "success": result["success"],
                "response_preview": result["response"][:400],
            })
            time.sleep(2)

    total = len(results)
    avg_judge = sum(judge_scores) / len(judge_scores) if judge_scores else 0
    avg_time = total_time / total if total > 0 else 0

    print("\n" + "=" * 65)
    print("MIRA EVAL SUITE SUMMARY")
    print("=" * 65)
    print(f"Total queries:     {total}")
    print(f"Content passed:    {passed} ({passed/total*100:.1f}%)")
    print(f"Content failed:    {failed} ({failed/total*100:.1f}%)")
    if judge_scores:
        print(f"Avg judge score:   {avg_judge:.1f}/10")
        print(f"Judge evals:       {len(judge_scores)}")
    print(f"Avg response time: {avg_time:.1f}s")
    print(f"Total time:        {total_time:.1f}s")

    print("\nBy Question Type:")
    print("-" * 55)
    for q_type, _ in all_templates:
        tr = [r for r in results if r["question_type"] == q_type]
        tp = sum(1 for r in tr if r["content_pass"])
        tt = len(tr)
        at = sum(r["response_time"] for r in tr) / tt if tt else 0
        scores = [
            r["judge_overall"] for r in tr
            if isinstance(r.get("judge_overall"), (int, float))
        ]
        avg_s = sum(scores) / len(scores) if scores else 0
        score_str = f"{avg_s:.1f}/10" if scores else "N/A"
        print(f"  {q_type:<12} pass:{tp}/{tt} score:{score_str} avg:{at:.1f}s")

    failed_list = [r for r in results if not r["content_pass"]]
    if failed_list:
        print(f"\nFailed ({len(failed_list)}):")
        for r in failed_list:
            print(f"  [{r['eval_type']}] {r['project'][:35]} -- {r['question_type']}")

    low_scores = [
        r for r in results
        if isinstance(r.get("judge_overall"), (int, float))
        and r["judge_overall"] < 6
    ]
    if low_scores:
        print(f"\nLow Judge Scores (<6/10):")
        for r in low_scores:
            print(f"  {r['project'][:35]} -- {r['question_type']}: {r['judge_overall']}/10")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"evals/results/mira_eval_suite_{timestamp}.csv"
    summary_file = f"evals/results/mira_summary_{timestamp}.json"
    os.makedirs("evals/results", exist_ok=True)

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "timestamp": timestamp,
        "total_queries": total,
        "content_pass_rate": round(passed / total * 100, 1),
        "avg_judge_score": round(avg_judge, 1),
        "avg_response_time": round(avg_time, 1),
        "total_time": round(total_time, 1),
    }
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nCSV: {csv_file}")
    print(f"Summary: {summary_file}")
    print("=" * 65)
    return results, summary


if __name__ == "__main__":
    run_eval_suite()