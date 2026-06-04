import requests
import json
import time
import csv
import os
import re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv('/Users/thomasraju/mira-project-intelligence-assistant/.env', override=False)

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://127.0.0.1:7860")
FLOW_ID = os.getenv("FLOW_ID", "")
API_KEY = os.getenv("LANGFLOW_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ENABLE_LLM_JUDGE = os.getenv("ENABLE_LLM_JUDGE", "true").lower() == "true"

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


def llm_judge(question, response):
    if not ANTHROPIC_API_KEY:
        return {}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = (
            f"You are an expert evaluator for MIRA AI risk assessment.\n"
            f"Question: {question}\n"
            f"Response: {response}\n\n"
            f"Score each 0-10. Return ONLY valid JSON:\n"
            f'{{"factual_accuracy":0,"groundedness":0,"completeness":0,'
            f'"hallucination_free":0,"relevance":0,"overall":0,'
            f'"issues":[""],"reasoning":"brief explanation"}}'
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


def content_pass_check(response, project):
    r = response.lower()
    generic_phrases = ["not available", "not retrieved", "unable to retrieve",
                      "cannot provide", "no specific", "i apologize"]
    is_generic = any(p in r for p in generic_phrases)
    project_words = [w for w in project.lower().split() if len(w) > 4]
    has_project = any(w in r for w in project_words)
    risk_keywords = ["risk", "delay", "mitigation", "impact", "challenge",
                    "issue", "concern", "defect", "failure", "vulnerability"]
    has_risk_kw = any(kw in r for kw in risk_keywords)
    return not is_generic and has_project and has_risk_kw and len(response) > 200


def run_risk_eval():
    print("=" * 60)
    print("MIRA Risk-Only Eval Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projects: {len(PROJECTS)} | LLM Judge: {'ON' if ENABLE_LLM_JUDGE else 'OFF'}")
    print("=" * 60)

    results = []
    passed = 0
    failed = 0
    judge_scores = []
    total_time = 0

    for i, project in enumerate(PROJECTS):
        question = f"What are the major risks for {project}?"
        session_id = f"risk-eval-{i}-{int(time.time())}"
        print(f"\n[{i+1}/{len(PROJECTS)}] {project[:55]}")
        print(f"  risks...", end=" ", flush=True)

        result = query_mira(question, session_id)
        content_ok = content_pass_check(result["response"], project)

        judge_result = {}
        if ENABLE_LLM_JUDGE and result["success"] and result["response"]:
            judge_result = llm_judge(question, result["response"])
            if judge_result.get("overall", 0) > 0:
                judge_scores.append(judge_result["overall"])

        if content_ok:
            passed += 1
        else:
            failed += 1
        total_time += result["time"]

        status = "PASS" if content_ok else "FAIL"
        judge_str = f" | Judge: {judge_result.get('overall', 0):.1f}/10" if judge_result else ""
        print(f"{status}{judge_str} ({result['time']}s)")

        for issue in judge_result.get("issues", [])[:1]:
            if issue:
                print(f"    Issue: {issue[:80]}")

        results.append({
            "project": project,
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
            "response_preview": result["response"][:400],
        })
        time.sleep(2)

    total = len(results)
    avg_judge = sum(judge_scores) / len(judge_scores) if judge_scores else 0
    avg_time = total_time / total if total > 0 else 0

    print("\n" + "=" * 60)
    print("RISK EVAL SUMMARY")
    print("=" * 60)
    print(f"Total queries:     {total}")
    print(f"Content passed:    {passed} ({passed/total*100:.1f}%)")
    print(f"Content failed:    {failed} ({failed/total*100:.1f}%)")
    if judge_scores:
        print(f"Avg judge score:   {avg_judge:.1f}/10")
        print(f"Judge evals:       {len(judge_scores)}")
    print(f"Avg response time: {avg_time:.1f}s")
    print(f"Total time:        {total_time:.1f}s")

    failed_list = [r for r in results if not r["content_pass"]]
    if failed_list:
        print(f"\nFailed ({len(failed_list)}):")
        for r in failed_list:
            print(f"  {r['project'][:50]}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("evals/results", exist_ok=True)
    csv_file = f"evals/results/mira_risk_eval_{timestamp}.csv"
    summary_file = f"evals/results/mira_risk_summary_{timestamp}.json"

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "timestamp": timestamp,
        "total_queries": total,
        "content_pass_rate": round(passed/total*100, 1),
        "avg_judge_score": round(avg_judge, 1),
        "avg_response_time": round(avg_time, 1),
        "total_time": round(total_time, 1),
        "data_source": "Google Sheets Risk Matrix"
    }
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nCSV: {csv_file}")
    print(f"Summary: {summary_file}")
    print("=" * 60)
    return results, summary


if __name__ == "__main__":
    run_risk_eval()
