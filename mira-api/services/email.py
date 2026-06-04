import os
import resend
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Optional
import re

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")


def md_to_html(text):
    if not text:
        return ""
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3 style="color:#028090;font-size:14px;margin:12px 0 4px">\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2 style="color:#1E2761;font-size:15px;margin:14px 0 6px;border-bottom:1px solid #CADCFC;padding-bottom:4px">\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1 style="color:#1E2761;font-size:17px;margin:14px 0 8px">\1</h1>', text, flags=re.MULTILINE)
    # Bold and italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Bullet lists
    text = re.sub(r'^- (.+)$', r'<li style="margin-bottom:4px">\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^[0-9]+\. (.+)$', r'<li style="margin-bottom:4px">\1</li>', text, flags=re.MULTILINE)
    # Paragraphs
    text = text.replace('\n\n', '</p><p style="margin-bottom:8px;line-height:1.6">')
    text = text.replace('\n', '<br>')
    return f'<p style="margin-bottom:8px;line-height:1.6">{text}</p>'


def generate_html_report(project, data):
    timeline = md_to_html(data.get("timeline", "No timeline data available"))
    objectives = md_to_html(data.get("objectives", "No objectives data available"))
    risks = md_to_html(data.get("risks", "No risk data available"))
    governance = md_to_html(data.get("governance", "No governance data available"))
    lessons = md_to_html(data.get("lessons", "No lessons data available"))

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f4f8;margin:0;padding:20px;color:#1E2761}}
.container{{max-width:700px;margin:0 auto;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
.header{{background:#1E2761;padding:24px 32px}}
.header h1{{color:white;margin:0;font-size:28px;letter-spacing:6px}}
.header p{{color:#CADCFC;margin:4px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px}}
.project-bar{{background:#028090;padding:12px 32px;color:white;font-size:14px;font-weight:600}}
.content{{padding:24px 32px}}
.section{{margin-bottom:20px;border-left:3px solid #028090;padding-left:16px}}
.section h2{{font-size:11px;color:#028090;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px}}
.hil-box{{background:#FEF3C7;border:1px solid #F59E0B;border-left:4px solid #F59E0B;border-radius:6px;padding:12px 16px;margin:16px 0}}
.hil-box h3{{color:#92400E;margin:0 0 4px;font-size:13px}}
.hil-box p{{color:#92400E;margin:0;font-size:12px}}
.timestamp{{font-size:11px;color:#94a3b8;text-align:right;margin-bottom:16px}}
.footer{{background:#EEF2F7;padding:16px 32px;text-align:center;font-size:11px;color:#94a3b8;font-style:italic}}
</style>
</head>
<body>
<div class="container">
  <div class="header"><h1>MIRA</h1><p>Project Intelligence Report</p></div>
  <div class="project-bar">{project}</div>
  <div class="content">
    <div class="timestamp">Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}</div>
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px">
      <tr>
        <td style="padding:8px;background:#EEF2F7;border-radius:6px;text-align:center;width:33%">
          <div style="font-size:18px;font-weight:700;color:#028090">26</div>
          <div style="font-size:10px;color:#64748b;text-transform:uppercase">Projects</div>
        </td>
        <td style="width:10px"></td>
        <td style="padding:8px;background:#EEF2F7;border-radius:6px;text-align:center;width:33%">
          <div style="font-size:18px;font-weight:700;color:#028090">99.2%</div>
          <div style="font-size:10px;color:#64748b;text-transform:uppercase">Eval Pass Rate</div>
        </td>
        <td style="width:10px"></td>
        <td style="padding:8px;background:#EEF2F7;border-radius:6px;text-align:center;width:33%">
          <div style="font-size:18px;font-weight:700;color:#028090">8.3/10</div>
          <div style="font-size:10px;color:#64748b;text-transform:uppercase">Judge Score</div>
        </td>
      </tr>
    </table>
    <div class="section"><h2>Timeline & Milestones</h2>{timeline}</div>
    <div class="section"><h2>Objectives</h2>{objectives}</div>
    <div class="section"><h2>Risk Assessment</h2>{risks}</div>
    <div class="section"><h2>Governance & HIL</h2>{governance}</div>
    <div class="hil-box">
      <h3>⚠️ Human Judgment Required</h3>
      <p>This report contains AI-generated insights grounded in project documentation.
         All critical decisions require human review and oversight.</p>
    </div>
    <div class="section"><h2>Lessons Learned</h2>{lessons}</div>
  </div>
  <div class="footer">Supporting human wisdom, not replacing it. — MIRA Project Intelligence Assistant</div>
</div>
</body></html>"""


def generate_context_html(project, last_question, last_response, hil_lines, sources, response_time, summary):
    hil_section = ""
    if hil_lines:
        items = "".join(f'<p style="color:#92400E;font-size:12px;margin:4px 0">{l}</p>' for l in hil_lines if l.strip())
        hil_section = f'<div class="hil-box"><h3>⚠️ Human Judgment Required</h3>{items}</div>'

    sources_section = ""
    if sources:
        items = "".join(f'<div style="font-size:12px;color:#64748b;margin-bottom:4px">[{i+1}] {s}</div>' for i, s in enumerate(sources) if s.strip())
        sources_section = f'<div style="background:#F8FAFC;border:1px solid #CADCFC;border-radius:6px;padding:12px 16px;margin-top:12px"><div style="font-size:10px;font-weight:700;color:#028090;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Sources</div>{items}</div>'

    meta = f'<div style="font-size:11px;color:#94a3b8;margin-top:8px">Response time: {response_time}s</div>' if response_time else ""

    q_section = f'<div style="background:#1E2761;border-radius:8px;padding:12px 16px;margin-bottom:16px"><div style="font-size:11px;color:#CADCFC;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Question Asked</div><div style="font-size:14px;color:white;font-weight:500">{last_question}</div></div>' if last_question else ""

    r_section = ""
    if last_response:
        r_section = f'<div class="section"><h2>MIRA Response</h2>{md_to_html(last_response[:4000])}</div>{hil_section}{sources_section}{meta}'

    s_section = f'<div class="section"><h2>Project Summary</h2>{md_to_html(summary[:800])}</div>' if summary else ""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f4f8;margin:0;padding:20px;color:#1E2761}}
.container{{max-width:700px;margin:0 auto;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
.header{{background:#1E2761;padding:24px 32px}}
.header h1{{color:white;margin:0;font-size:28px;letter-spacing:6px}}
.header p{{color:#CADCFC;margin:4px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px}}
.project-bar{{background:#028090;padding:12px 32px;color:white;font-size:14px;font-weight:600}}
.content{{padding:24px 32px}}
.section{{margin-bottom:20px;border-left:3px solid #028090;padding-left:16px}}
.section h2{{font-size:11px;color:#028090;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px}}
.hil-box{{background:#FEF3C7;border:1px solid #F59E0B;border-left:4px solid #F59E0B;border-radius:6px;padding:12px 16px;margin:16px 0}}
.hil-box h3{{color:#92400E;margin:0 0 4px;font-size:13px}}
.timestamp{{font-size:11px;color:#94a3b8;text-align:right;margin-bottom:16px}}
.footer{{background:#EEF2F7;padding:16px 32px;text-align:center;font-size:11px;color:#94a3b8;font-style:italic}}
</style>
</head>
<body>
<div class="container">
  <div class="header"><h1>MIRA</h1><p>Project Intelligence — Context Report</p></div>
  <div class="project-bar">{project}</div>
  <div class="content">
    <div class="timestamp">Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}</div>
    {q_section}
    {r_section}
    {s_section}
  </div>
  <div class="footer">Supporting human wisdom, not replacing it. — MIRA Project Intelligence Assistant</div>
</div>
</body></html>"""


async def send_project_report(project, recipient_email, data):
    try:
        html = generate_html_report(project, data)
        response = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [recipient_email],
            "subject": f"MIRA Project Report: {project}",
            "html": html,
        })
        return {"success": True, "message": f"Report sent to {recipient_email}", "email_id": response.get("id", ""), "project": project}
    except Exception as e:
        return {"success": False, "message": f"Email error: {str(e)}", "project": project}


async def send_context_report(project, recipient_email, last_question, last_response, hil_lines, sources, response_time, summary):
    try:
        html = generate_context_html(project, last_question, last_response, hil_lines, sources, response_time, summary)
        subject = f"MIRA: {last_question[:60]}..." if last_question else f"MIRA Project Report: {project}"
        response = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [recipient_email],
            "subject": subject,
            "html": html,
        })
        return {"success": True, "message": f"Context report sent to {recipient_email}", "email_id": response.get("id", ""), "project": project}
    except Exception as e:
        return {"success": False, "message": f"Email error: {str(e)}", "project": project}
