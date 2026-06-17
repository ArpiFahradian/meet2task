import os
import re
import json
import uuid
import base64
from pathlib import Path
import streamlit as st
import requests
import assemblyai as aai
from groq import Groq
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

load_dotenv()

st.set_page_config(page_title="meetask", page_icon=None, layout="centered")

def clean_env_val(key):
    val = os.getenv(key, "")
    if not val: return ""
    return val.replace('"', '').replace("'", "").strip()

GROQ_KEY = clean_env_val("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_KEY)

AAI_KEY = clean_env_val("ASSEMBLYAI_API_KEY")
aai.settings.api_key = AAI_KEY

JIRA_DOMAIN = clean_env_val("JIRA_DOMAIN")
JIRA_EMAIL = clean_env_val("JIRA_EMAIL")
JIRA_TOKEN = clean_env_val("JIRA_API_TOKEN")
PROJECT_KEY = clean_env_val("JIRA_PROJECT_KEY")
base_url = f"https://{JIRA_DOMAIN}" if JIRA_DOMAIN else ""

# ──── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] p, div, h1, h2, h3, h4, span, label {
    font-family: 'Space Grotesk', sans-serif !important
}
footer,#MainMenu,.stDeployButton{visibility:hidden!important}
[data-testid="stMain"]>div{padding:1.5rem 2rem 5rem}
html{scroll-behavior:smooth}

[data-testid="stAppViewContainer"]{background:linear-gradient(-45deg,#07010f,#0a0e1a,#020b14,#0d0320,#040d1a);background-size:400% 400%;animation:aurora 18s ease infinite}

@keyframes heroBreath{0%,100%{box-shadow:0 0 80px rgba(147,51,234,.1)}50%{box-shadow:0 0 120px rgba(147,51,234,.18)}}
@keyframes blobFloat{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(20px,-15px) scale(1.05)}66%{transform:translate(-10px,10px) scale(.97)}}

.hero{position:relative;overflow:hidden;background:rgba(255,255,255,.018);backdrop-filter:blur(40px);-webkit-backdrop-filter:blur(40px);border:1px solid rgba(255,255,255,.07);border-radius:24px;padding:3.5rem 3rem 3rem;margin-bottom:2.5rem;animation:heroBreath 5s ease-in-out infinite}
.hero-blob1{position:absolute;top:-80px;left:-60px;width:350px;height:350px;border-radius:50%;background:radial-gradient(circle,rgba(147,51,234,.2) 0%,transparent 70%);animation:blobFloat 9s ease-in-out infinite;pointer-events:none}
.hero-blob2{position:absolute;bottom:-100px;right:-60px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(6,182,212,.15) 0%,transparent 70%);animation:blobFloat 7s ease-in-out infinite reverse;pointer-events:none}
.hero-tag{display:inline-flex;align-items:center;gap:6px;background:rgba(147,51,234,.15);border:1px solid rgba(147,51,234,.35);color:#c084fc;font-size:.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:1.2rem}
.hero p{color:rgba(255,255,255,.38);font-size:.95rem;line-height:1.7;margin:0}

@keyframes spinRing{to{transform:rotate(360deg)}}
.step-wrap{display:flex;align-items:center;gap:.9rem;margin:2.2rem 0 1rem}
.step-num-wrap{position:relative;width:36px;height:36px;flex-shrink:0}
.step-ring{position:absolute;inset:0;border-radius:50%;background:conic-gradient(#9333ea,#ec4899,#06b6d4,#9333ea);animation:spinRing 3s linear infinite}
.step-num-inner{position:absolute;inset:2px;border-radius:50%;background:#0a0114;display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700;color:#fff}
.step-title{font-size:1.05rem;font-weight:600;color:rgba(255,255,255,.85);margin:0}

[data-testid="stFileUploader"] > section {
    border: 2px dashed rgba(147,51,234,0.35) !important;
    border-radius: 16px !important;
    background: rgba(147,51,234,0.04) !important;
    padding: 20px !important;
}
.stButton>button[kind="primary"]{background:linear-gradient(90deg,#9333ea,#7c3aed,#06b6d4,#9333ea)!important;background-size:200% auto!important;border:none!important;color:#fff!important;font-weight:700!important;font-size:.9rem!important;border-radius:12px!important;padding:.7rem 2rem!important}

input,[data-testid="stTextInput"] input{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:10px!important;color:rgba(255,255,255,.85)!important;height:38px!important}
[data-testid="stSelectbox"]>div>div{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:10px!important;color:rgba(255,255,255,.85)!important;height:38px!important}

div[data-testid="stCheckbox"] input[type="checkbox"]{accent-color:#9333ea!important;filter:hue-rotate(60deg) saturate(1.5)!important}
div[data-testid="stCheckbox"]{padding-left:8px!important}

.transcript-box{background:rgba(255,255,255,.02);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.07);border-radius:18px;padding:1.5rem 1.75rem;max-height:450px;overflow-y:auto}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.25rem}
.metric-card{background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);border-radius:18px;padding:1.5rem;text-align:center}
.metric-val{font-size:2.8rem;font-weight:800;line-height:1;font-family:'Syne',sans-serif}
.metric-lbl{font-size:.68rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,255,255,.28);margin-top:.4rem}

.selected-panel{background:rgba(147,51,234,0.03);border:1px dashed rgba(147,51,234,0.3);border-radius:18px;padding:1.5rem;margin-top:1.5rem}
.selected-header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:0.8rem;margin-bottom:0.6rem}
.selected-title{font-size:1.1rem;font-weight:700;color:#fff;margin:0}
.selected-count-badge{background:linear-gradient(135deg,#9333ea,#06b6d4);color:#fff;font-size:0.8rem;font-weight:700;padding:3px 12px;border-radius:20px}
.badge-status{font-size:0.7rem;font-weight:700;text-transform:uppercase;padding:2px 8px;border-radius:6px;letter-spacing:0.5px}

div[data-testid="stMarkdown"]:has(.sel-row-marker) + div[data-testid="stHorizontalBlock"]{background:rgba(255,255,255,0.02)!important;border:1px solid rgba(255,255,255,0.05)!important;border-radius:10px!important;padding:0.15rem 0.5rem!important;margin-bottom:3px!important}

.hero-roadmap{display:flex;align-items:center;justify-content:center;gap:0;margin-top:2rem}
.hstep{display:flex;flex-direction:column;align-items:center;gap:.45rem;padding:.8rem 1.1rem;border-radius:14px;background:rgba(255,255,255,.04);border:1px solid rgba(147,51,234,.2);min-width:90px;text-align:center}
.hstep-n{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#9333ea,#06b6d4);display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700;color:#fff}
.hstep-t{font-size:.7rem;font-weight:600;color:rgba(255,255,255,.6);line-height:1.35}
.hstep-conn{display:flex;align-items:center;padding-bottom:1.5rem}
.hstep-line{width:28px;height:1.5px;background:linear-gradient(90deg,rgba(147,51,234,.35),rgba(6,182,212,.35))}
.hstep-tip{width:0;height:0;border-top:4px solid transparent;border-bottom:4px solid transparent;border-left:6px solid rgba(6,182,212,.4)}
.hero-logo-wrap{text-align:center;margin-bottom:.6rem}

.sup-badge{font-size:0.68rem;vertical-align:super;font-weight:800;background:rgba(0,0,0,0.18);padding:2px 6px;border-radius:4px;margin-left:4px;color:#000000!important;text-decoration:none!important;display:inline-block}
.sup-badge:hover{background:rgba(0,0,0,0.35)}

.task-num-link{display:flex;align-items:center;justify-content:center;background:rgba(147,51,234,0.15);border:1px solid rgba(147,51,234,0.35);border-radius:8px;color:#c084fc!important;font-weight:bold;height:32px;width:32px;text-decoration:none!important;transition:all 0.2s;font-size:0.85rem}
.task-num-link:hover{background:rgba(147,51,234,0.35);border-color:#c084fc}

/* === Step 3-ի task տողերը կոմպակտ ենք դարձնում === */
div[data-testid="stHorizontalBlock"]{align-items:center!important}

/* Anchor marker-ի div-ը դարձնում ենք անտեսանելի (height=0) */
div[data-testid="stMarkdown"]:has(.anchor-section){
    margin:0!important;
    padding:0!important;
    height:0!important;
    min-height:0!important;
    line-height:0!important;
    overflow:hidden!important;
}

/* Մարկերից անմիջապես հետո եկող task row-ը կպցնում ենք վերևից */
div[data-testid="stMarkdown"]:has(.anchor-section) + div[data-testid="stHorizontalBlock"]{
    margin-top:0!important;
    margin-bottom:6px!important;
}

/* Task row-երի ընդհանուր vertical gap-ը կրճատում ենք */
div[data-testid="stVerticalBlock"]:has(> div > div[data-testid="stMarkdown"] .anchor-section) > div{
    gap:0!important;
}

/* === Selected Tasks for Jira Sync — եզրագծված տուփ === */
div[data-testid="stVerticalBlock"]:has(> div:first-child > div[data-testid="stMarkdown"] .sel-panel-marker){
    background:rgba(147,51,234,0.05)!important;
    border:1px solid rgba(147,51,234,0.4)!important;
    border-radius:18px!important;
    padding:1.5rem 1.75rem 1.25rem!important;
    margin-top:1.5rem!important;
    box-shadow:0 4px 20px rgba(147,51,234,0.08)!important;
}

div[data-testid="stMarkdown"]:has(.sel-panel-marker){
    margin:0!important;
    padding:0!important;
    height:0!important;
    min-height:0!important;
    line-height:0!important;
    overflow:hidden!important;
}

div[data-testid="stMarkdown"]:has(.sel-row-marker){
    margin:0!important;
    padding:0!important;
    height:0!important;
    min-height:0!important;
    line-height:0!important;
    overflow:hidden!important;
}

div[data-testid="stMarkdown"]:has(.sel-row-marker) + div[data-testid="stHorizontalBlock"]{
    margin-top:0!important;
    margin-bottom:4px!important;
    padding:0.3rem 0.5rem!important;
    background:rgba(255,255,255,0.02)!important;
    border-radius:8px!important;
}

div[data-testid="stBlock"] button[key^="del_task_"]{height:32px!important;width:32px!important;max-width:32px!important;min-width:32px!important;padding:0!important;display:flex!important;align-items:center!important;justify-content:center!important;border-radius:8px!important;background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;color:rgba(255,255,255,.6)!important;transition:all 0.2s!important}
div[data-testid="stBlock"] button[key^="del_task_"]:hover{background:rgba(244,63,94,0.15)!important;border-color:#f43f5e!important;color:#f43f5e!important}

@keyframes softWordFlash{0%{background-color:#9333ea!important;color:#fff!important;box-shadow:0 0 20px #9333ea;border-radius:4px}100%{background-color:#bbf7d0;color:#166534}}
@keyframes softButtonFlash{0%{background-color:#9333ea!important;border-color:#c084fc!important;box-shadow:0 0 20px #9333ea;transform:scale(1.05)}100%{background-color:rgba(147,51,234,0.15);border-color:rgba(147,51,234,0.35);transform:scale(1)}}

.word-target:target{animation:softWordFlash 1.8s ease-out forwards;scroll-margin-top:160px}
.task-btn-target:target .task-num-link{animation:softButtonFlash 1.8s ease-out forwards;scroll-margin-top:160px}

.sync-result-row{display:flex;align-items:center;gap:12px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:0.55rem 1rem;margin-bottom:0.4rem}
.sync-key-badge{background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);color:#10b981!important;font-size:0.78rem;font-weight:700;padding:2px 10px;border-radius:6px;text-decoration:none!important;white-space:nowrap}
.sync-key-badge:hover{background:rgba(16,185,129,0.3)!important}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fix_word_spacing(text):
    return re.sub(r'(\D)(\d)(\w)', r'\1 \2\3', text)

def render_proc_steps(current: int, done: bool = False) -> str:
    labels = [
        "Upload audio to AssemblyAI Cloud",
        "Transcribe & diarize speakers",
        "Map speech segments",
        "Extract action items with Groq Llama 3.3",
    ]
    rows = ""
    for idx, label in enumerate(labels):
        if idx < current:
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:#10b981;color:#fff;font-size:0.75rem;font-weight:bold;flex-shrink:0;">✓</span>'
            c, fw = "#10b981", "600"
        elif idx == current:
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:rgba(245,158,11,0.15);border:2px solid #f59e0b;color:#f59e0b;font-size:0.65rem;flex-shrink:0;">●</span>'
            c, fw = "#f5f5f5", "600"
        else:
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.3);font-size:0.7rem;flex-shrink:0;">○</span>'
            c, fw = "rgba(255,255,255,0.3)", "400"
        rows += f'<div style="display:flex;align-items:center;gap:0.75rem;padding:0.38rem 0;">{dot}<span style="font-size:0.88rem;color:{c};font-weight:{fw};">{label}</span></div>'
    border_c = "rgba(16,185,129,0.4)" if done else "rgba(255,255,255,0.08)"
    return f'<div style="background:rgba(255,255,255,0.025);border:1px solid {border_c};border-radius:14px;padding:1rem 1.25rem;margin-bottom:0.5rem;">{rows}</div>'

# ─── Groq Task Extractor ───────────────────────────────────────────────────────
def extract_tasks_with_groq(transcript: str) -> list:
    prompt = f"""You are an elite scrum master AI assistant. Analyze the transcript and extract ALL explicit action items.
CRITICAL RULES:
1. COMPLETELY IGNORE introductory statements, agenda definitions, or summary requests made by the Scrum Master/Project Manager (e.g., statements like "Let's begin our daily standup", "please cover 3 points" must NEVER yield any tasks).
2. ONLY extract genuine tasks committed by team members.
3. For EACH task, you MUST map it to the EXACT sentence index from the transcript text from which it was born.
4. For EACH task, pick a SINGLE baseline root keyword that exists in that sentence (e.g., if sentence has "currently working", choose ONLY "work" or "working". Never choose a multi-word phrase).
5. Status must be exactly: DONE, IN_PROGRESS, or NEW_TASK.
6. FOR EACH TASK ALSO RETURN:
- utterance_index (integer)

Return ONLY a valid JSON object.
Transcript:
{transcript}

JSON format:
{{ 
  "tasks": [ 
    {{ 
      "text": "...", 
      "status": "DONE", 
      "keyword": "completed", 
      "source_sentence": "Yesterday, I completed the responsive dashboard layout...",
      "utterance_index": 0
    }} 
  ] 
}}"""
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}],
            temperature=0, response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content).get("tasks", [])
    except Exception: return []

# ─── Jira Logic ───────────────────────────────────────────────────────────────
def create_jira_issue(summary: str, description: str = ""):
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    fields = {"project": {"key": PROJECT_KEY}, "summary": summary, "issuetype": {"name": "Task"}}
    if description:
        fields["description"] = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]}
    try:
        r = requests.post(f"{base_url}/rest/api/3/issue",
                          headers={"Accept": "application/json", "Content-Type": "application/json"},
                          auth=auth, data=json.dumps({"fields": fields}))
        return r.json().get("key") if r.status_code == 201 else None
    except Exception: return None

def transition_jira_issue(issue_key: str, target_status: str):
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    try:
        r = requests.get(f"{base_url}/rest/api/3/issue/{issue_key}/transitions",
                         headers={"Accept": "application/json"}, auth=auth)
        if r.status_code != 200: return
        target_norm = target_status.lower().replace(" ", "")
        for t in r.json().get("transitions", []):
            to_name = t.get("to", {}).get("name", "").lower().replace(" ", "")
            if target_norm in to_name or to_name in target_norm:
                requests.post(
                    f"{base_url}/rest/api/3/issue/{issue_key}/transitions",
                    json={"transition": {"id": t["id"]}},
                    headers={"Accept": "application/json", "Content-Type": "application/json"},
                    auth=auth
                )
                return
    except Exception: pass

# ─── Session State ────────────────────────────────────────────────────────────
if "tasks" not in st.session_state: st.session_state.tasks = []
if "segments" not in st.session_state: st.session_state.segments = []
if "speaker_colors" not in st.session_state: st.session_state.speaker_colors = {}
if "master_select" not in st.session_state: st.session_state.master_select = False
if "final_sync_list" not in st.session_state: st.session_state.final_sync_list = []
if "synced_results" not in st.session_state: st.session_state.synced_results = []

# ─── Hero ─────────────────────────────────────────────────────────────────────
_logo_path = Path("meetask_logo-removebg-preview.png")
if _logo_path.exists():
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    _logo_html = f'<div class="hero-logo-wrap"><img src="data:image/png;base64,{_logo_b64}" alt="meetask" style="height:160px;mix-blend-mode:screen;filter:drop-shadow(0 0 35px rgba(6,182,212,.9)) drop-shadow(0 0 20px rgba(147,51,234,.8));"></div>'
else:
    _logo_html = '<div class="hero-logo-wrap"><h1 style="font-family:\'Syne\',sans-serif;font-size:3.2rem;font-weight:800;background:linear-gradient(90deg,#fff 0%,#c084fc 35%,#67e8f9 65%,#fff 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 .8rem">meetask</h1></div>'

st.markdown(f"""
<div class="hero fade-up">
<div class="hero-blob1"></div><div class="hero-blob2"></div>
<div class="hero-tag"><div class="hero-dot"></div>AI-Powered · Real-time · Jira-ready</div>
{_logo_html}
<p style="color:rgba(255,255,255,.55);font-size:1rem;margin:.5rem 0 .3rem;text-align:center">Turning meeting recordings into structured Jira tasks — automatically.</p>
<div class="hero-roadmap">
    <div class="hstep"><div class="hstep-n">1</div><div class="hstep-t">Upload<br>Recording</div></div>
    <div class="hstep-conn"><div class="hstep-line"></div><div class="hstep-tip"></div></div>
    <div class="hstep"><div class="hstep-n">2</div><div class="hstep-t">AI Transcribes<br>&amp; Analyzes</div></div>
    <div class="hstep-conn"><div class="hstep-line"></div><div class="hstep-tip"></div></div>
    <div class="hstep"><div class="hstep-n">3</div><div class="hstep-t">Review &amp;<br>Edit Tasks</div></div>
    <div class="hstep-conn"><div class="hstep-line"></div><div class="hstep-tip"></div></div>
    <div class="hstep"><div class="hstep-n">4</div><div class="hstep-t">Sync<br>to Jira</div></div>
</div>
</div>
""", unsafe_allow_html=True)

# ─── Step 1 ───────────────────────────────────────────────────────────────────
st.markdown('<div class="step-wrap"><div class="step-num-wrap"><div class="step-ring"></div><div class="step-num-inner">1</div></div><p class="step-title">Upload Recording</p></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload audio file", type=["ogg", "mp3", "wav"], label_visibility="collapsed")

if uploaded_file:
    size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.markdown(f'<div style="background:rgba(6,182,212,.12);border:1px solid rgba(6,182,212,.35);border-radius:10px;padding:.6rem 1rem;color:#67e8f9;font-size:.9rem">✓ Ready: <strong>{uploaded_file.name}</strong> ({size_mb:.1f} MB)</div>', unsafe_allow_html=True)

# ─── Step 2 ───────────────────────────────────────────────────────────────────
st.markdown('<div class="step-wrap"><div class="step-num-wrap"><div class="step-ring"></div><div class="step-num-inner">2</div></div><p class="step-title">Transcribe &amp; Extract</p></div>', unsafe_allow_html=True)

if st.button("Run AI Processing", type="primary", disabled=not uploaded_file):
    proc_ph = st.empty()
    proc_ph.markdown(render_proc_steps(0), unsafe_allow_html=True)

    temp_path = f"temp_{uuid.uuid4().hex}.wav"
    Path(temp_path).write_bytes(uploaded_file.getvalue())

    try:
        config = aai.TranscriptionConfig(speaker_labels=True)
        transcriber = aai.Transcriber()

        proc_ph.markdown(render_proc_steps(1), unsafe_allow_html=True)

        transcript_response = transcriber.transcribe(
            temp_path,
            config=config
        )

        if transcript_response.status == aai.TranscriptStatus.error:
            st.error(transcript_response.error)
            st.stop()

        proc_ph.markdown(render_proc_steps(2), unsafe_allow_html=True)

        st.session_state.segments = []

        for idx, utterance in enumerate(transcript_response.utterances):
            start_sec = utterance.start / 1000.0

            st.session_state.segments.append({
                "utt_index": idx,   
                "start": start_sec,
                "speaker": f"Speaker {utterance.speaker}",
                "text": fix_word_spacing(utterance.text.strip())
            })

        proc_ph.markdown(render_proc_steps(3), unsafe_allow_html=True)

        full_text_formatted = "\n".join(
            [
                f"[{s['start']:.1f}s] {s['speaker']}: {s['text']}"
                for s in st.session_state.segments
            ]
        )

        st.session_state.tasks = extract_tasks_with_groq(
            full_text_formatted
        )

        # ── Պահպանում ենք Groq-ի վերադարձրած JSON-ը՝ tasks.json ֆայլում ──
        # (Այս ֆայլը թարմացվում է ամեն մշակումից հետո, որպեսզի տեսանելի
        #  լինի, թե ինչ կառուցվածքային output է վերադարձնում Groq-ը։)
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(
                    {"tasks": st.session_state.tasks},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            st.warning(f"Could not save tasks.json: {e}")

        # ── Պահպանում ենք AssemblyAI-ի transcript-ը՝ transcript.json ֆայլում ──
        # (Այս ֆայլը ցույց է տալիս AssemblyAI-ի արդյունքը՝ utterance-ները
        #  իրենց ժամանականիշներով, խոսողներով, և տեքստով։)
        try:
            with open("transcript.json", "w", encoding="utf-8") as f:
                json.dump(
                    {"segments": st.session_state.segments},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            st.warning(f"Could not save transcript.json: {e}")

        palette = [
            "#c084fc", "#67e8f9", "#818cf8", "#a78bfa", "#2dd4bf", "#86efac", "#93c5fd"
        ]

        unique_raw_speakers = sorted(
            list(set([s["speaker"] for s in st.session_state.segments]))
        )

        st.session_state.speaker_colors = {}

        for idx, r_spk in enumerate(unique_raw_speakers):
            if idx == 0:
                st.session_state.speaker_colors[r_spk] = "#c084fc"
            elif idx == 1:
                st.session_state.speaker_colors[r_spk] = "#67e8f9"
            else:
                st.session_state.speaker_colors[r_spk] = palette[idx % len(palette)]

        st.session_state.master_select = False
        st.session_state.final_sync_list = []
        st.session_state.synced_results = []

        for i in range(len(st.session_state.tasks)):
            st.session_state[f"task_sel_{i}"] = False

        proc_ph.markdown(
            render_proc_steps(4, done=True),
            unsafe_allow_html=True
        )

        st.rerun()

    except Exception as e:
        st.error(f"Processing Error: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)  

# ─── Speaker Names ────────────────────────────────────────────────────────────
unique_speakers = sorted(list(set([s["speaker"] for s in st.session_state.segments]))) if st.session_state.segments else []
if "speaker_mapping" not in st.session_state:
    st.session_state.speaker_mapping = {}
speaker_mapping = st.session_state.speaker_mapping

if unique_speakers:
    st.markdown('<p style="font-size:0.9rem;color:rgba(255,255,255,0.5);margin-bottom:5px;"> Assign Real Names to Speakers:</p>', unsafe_allow_html=True)
    n = len(unique_speakers)
    if n == 1:
        col_spk, _ = st.columns([3, 7])
        cols = [col_spk]
    else:
        cols = st.columns(n)
    for idx, old_name in enumerate(unique_speakers):
        new_name = cols[idx].text_input(f"Name for {old_name}", value=old_name, key=f"spk_name_{idx}")
        speaker_mapping[old_name] = new_name.strip() if new_name.strip() else old_name

# ─── Transcript Display ───────────────────────────────────────────────────────
if st.session_state.segments:
    hl_config = {
        "DONE": ("#bbf7d0", "#166534"),
        "IN_PROGRESS": ("#bfdbfe", "#1e40af"),
        "NEW_TASK": ("#e5e7eb", "#374151")
    }

    STOP_WORDS = {
        'the','a','an','i','you','we','they','he','she','it',
        'is','are','was','were','be','been','being',
        'have','has','had','do','does','did',
        'will','would','should','could','can','may','might',
        'and','or','but','so','if','when','while',
        'to','of','in','on','at','for','with','by','from','as',
        'that','this','these','those','there','here',
        'my','your','our','their','his','her','its',
        'me','us','them','him','who','what','where',
        'm','s','t','ll','ve','re','d',
        'yeah','ok','okay','um','uh','like','just','also','still','only',
    }

    def _normalize(text):
        text = text.lower().strip()
        text = re.sub(r'\.{2,}', '', text)      
        text = re.sub(r'\s+', ' ', text)        
        return text.strip()

    def _stems_in(text):
        return {stemmer.stem(w) for w in re.findall(r'\w+', text.lower())}

    def _meaningful_words(text):
        return set(re.findall(r'\w+', text.lower())) - STOP_WORDS

    task_to_segment = {}  

    for task_idx, task in enumerate(st.session_state.tasks):
        src_sent = _normalize(task.get("source_sentence", ""))
        raw_kw = task.get("keyword", "").lower().strip()
        base_kw = raw_kw.split()[0] if raw_kw else ""
        if not src_sent or not base_kw:
            continue

        kw_stem = stemmer.stem(base_kw)
        src_meaningful = _meaningful_words(src_sent)

        best_seg = -1
        best_score = -1

        for seg_idx, seg in enumerate(st.session_state.segments):
            seg_text_norm = _normalize(seg['text'])

            if kw_stem not in _stems_in(seg_text_norm):
                continue

            score = 0
            if src_sent and src_sent in seg_text_norm:
                score = 1000  
            elif seg_text_norm and seg_text_norm in src_sent:
                score = 900   
            elif src_meaningful:
                seg_meaningful = _meaningful_words(seg_text_norm)
                overlap = len(src_meaningful & seg_meaningful)
                score = (overlap / len(src_meaningful)) * 100

            if score > best_score:
                best_score = score
                best_seg = seg_idx

        if best_seg >= 0:
            task_to_segment[task_idx] = (best_seg, base_kw)

    segment_to_tasks = {}
    for task_idx, (seg_idx, base_kw) in task_to_segment.items():
        segment_to_tasks.setdefault(seg_idx, []).append((base_kw, task_idx))

    def highlight_for_segment(text_segment, seg_idx):
        tasks_here = segment_to_tasks.get(seg_idx, [])
        if not tasks_here:
            return text_segment

        rendered = set()
        words = text_segment.split()
        new_words = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word).lower().strip()
            if not clean_word:
                new_words.append(word)
                continue

            found_task = None
            for base_kw, t_idx in tasks_here:
                if (
                    stemmer.stem(clean_word) == stemmer.stem(base_kw)
                    and t_idx not in rendered
                ):
                    found_task = (base_kw, t_idx)
                    break

            if found_task:
                _, task_idx = found_task
                bg, fg = hl_config.get(st.session_state.tasks[task_idx]["status"], hl_config["NEW_TASK"])
                new_words.append(
                    f'<span id="word_src_{task_idx}" class="word-target" '
                    f'style="background:{bg};color:{fg};border-radius:4px;padding:2px 6px;font-weight:bold;transition:all 0.3s;">'
                    f'{word}'
                    f'<a href="#task_anchor_{task_idx}" class="sup-badge">{task_idx+1}</a>'
                    f'</span>'
                )
                rendered.add(task_idx)
            else:
                new_words.append(word)
        return " ".join(new_words)

    lines_html = []
    for seg_idx, s in enumerate(st.session_state.segments):
        old_spk = s["speaker"]
        actual_spk = speaker_mapping.get(old_spk, old_spk)
        spk_color = st.session_state.speaker_colors.get(old_spk, "#fff")
        ts = s.get("start", 0)
        if isinstance(ts, float):
            m, s_time = int(ts // 60), int(ts % 60)
            ts = f"{m:02d}:{s_time:02d}"
        lines_html.append(
            f"<p style='margin:8px 0;font-size:.95rem;padding:2px 4px;color:rgba(255,255,255,0.9);'>"
            f"<span style='color:#67e8f9;margin-right:8px;font-size:0.85rem;font-weight:bold;'>[{ts}]</span>"
            f"<strong style='color:{spk_color};margin-right:6px'>{actual_spk}:</strong>"
            f"\"{highlight_for_segment(s['text'], seg_idx)}\""
            f"</p>"
        )
    st.markdown('<div class="transcript-box">' + "".join(lines_html) + "</div>", unsafe_allow_html=True)

# ─── Step 3 ───────────────────────────────────────────────────────────────────
if st.session_state.tasks:
    st.markdown('<div class="step-wrap"><div class="step-num-wrap"><div class="step-ring"></div><div class="step-num-inner">3</div></div><p class="step-title">Review Tasks</p></div>', unsafe_allow_html=True)

    col_m1, col_m2, col_m3 = st.columns([0.45, 0.55, 8.5])
    with col_m2:
        master_click = st.checkbox("", value=st.session_state.master_select, key="master_checkbox")
    with col_m3:
        st.markdown("<p style='margin-top:2px;font-size:0.92rem;font-weight:bold;color:rgba(255,255,255,0.75)'>Select / Unselect All Tasks</p>", unsafe_allow_html=True)

    if master_click != st.session_state.master_select:
        st.session_state.master_select = master_click
        for i in range(len(st.session_state.tasks)):
            st.session_state[f"task_sel_{i}"] = master_click
        st.rerun()

    st.session_state.final_sync_list = []
    to_delete = None

    for i, t in enumerate(st.session_state.tasks):
        task_text = t["text"]
        for old_spk, new_name in speaker_mapping.items():
            task_text = task_text.replace(old_spk, new_name)
        if task_text:
            task_text = task_text.strip().capitalize()

        st.markdown(f"<div id='task_anchor_{i}' class='anchor-section'>", unsafe_allow_html=True)
        col_num, col_check, col_content = st.columns([0.45, 0.55, 8.5])

        with col_num:
            st.markdown(f"<div id='task_btn_{i}' class='task-btn-target'>", unsafe_allow_html=True)
            st.markdown(f'<a href="#word_src_{i}" class="task-num-link">{i+1}</a>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_check:
            if f"task_sel_{i}" not in st.session_state: 
                st.session_state[f"task_sel_{i}"] = st.session_state.master_select
            is_sel = st.checkbox("", value=st.session_state[f"task_sel_{i}"], key=f"task_sel_{i}", label_visibility="collapsed")

        with col_content:
            sub_c1, sub_c2, sub_c3 = st.columns([7.2, 2.0, 0.8])
            with sub_c1:
                txt = st.text_input("", value=task_text, key=f"txt_{i}", label_visibility="collapsed")
            with sub_c2:
                curr_status = t["status"]
                default_idx = 0 if curr_status == "NEW_TASK" else 1 if curr_status == "IN_PROGRESS" else 2
                stat = st.selectbox("", ["To Do", "In Progress", "Done"], index=default_idx, key=f"st_{i}", label_visibility="collapsed")
            with sub_c3:
                if st.button("✕", key=f"del_task_{i}"): 
                    to_delete = i

        st.markdown("</div>", unsafe_allow_html=True)

        if is_sel:
            st.session_state.final_sync_list.append({
                "id": i+1, "text": txt, "status": stat,
                "source": t.get("source_sentence", "")
            })

    if to_delete is not None:
        st.session_state.tasks.pop(to_delete)
        for key in list(st.session_state.keys()):
            if key.startswith(("task_sel_", "txt_", "st_")):
                del st.session_state[key]
        st.rerun()

    done_c = sum(1 for t in st.session_state.tasks if t['status'] == 'DONE')
    prog_c = sum(1 for t in st.session_state.tasks if t['status'] == 'IN_PROGRESS')
    todo_c = sum(1 for t in st.session_state.tasks if t['status'] == 'NEW_TASK')

    st.markdown(f"""<div class="metrics">
        <div class="metric-card"><div class="metric-val" style="color:#10b981">{done_c}</div><div class="metric-lbl">Done</div></div>
        <div class="metric-card"><div class="metric-val" style="color:#60a5fa">{prog_c}</div><div class="metric-lbl">In Progress</div></div>
        <div class="metric-card"><div class="metric-val" style="color:#9ca3af">{todo_c}</div><div class="metric-lbl">To Do</div></div>
    </div>""", unsafe_allow_html=True)

    status_colors = {
        "To Do": ("rgba(156,163,175,0.15)", "#9ca3af"),
        "In Progress": ("rgba(96,165,250,0.15)", "#60a5fa"),
        "Done": ("rgba(16,185,129,0.15)", "#10b981")
    }

    with st.container():
        st.markdown('<div class="sel-panel-marker"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="selected-header">
            <h3 class="selected-title"> Selected Tasks for Jira Sync</h3>
            <span class="selected-count-badge">{len(st.session_state.final_sync_list)} Selected</span>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.final_sync_list:
            st.markdown('<p style="color:rgba(255,255,255,0.35);font-size:0.9rem;font-style:italic;text-align:center;margin:6px 0 0;">No tasks selected yet. Check items above to preview sync.</p>', unsafe_allow_html=True)
        else:
            _h1, _h2, _h3, _h4 = st.columns([0.6, 4.8, 1.9, 1.7])
            _h4.markdown(
                '<p title="When ON, the original transcript sentence that generated this task will be added to the Jira issue description." '
                'style="font-size:0.68rem;color:rgba(255,255,255,0.3);text-align:center;margin:0;letter-spacing:0.8px;'
                'text-transform:uppercase;cursor:help;">ADD DESC ℹ️</p>',
                unsafe_allow_html=True
            )

            for item in st.session_state.final_sync_list:
                bg, fg = status_colors.get(item["status"], ("rgba(255,255,255,0.1)", "#fff"))
                desc_key = f"desc_toggle_{item['id']}"
                if desc_key not in st.session_state:
                    st.session_state[desc_key] = True

                st.markdown('<div class="sel-row-marker"></div>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([0.6, 4.8, 1.9, 1.7])
                c1.markdown(f'<p style="color:#c084fc;font-weight:bold;text-align:center;margin:0;padding-top:7px;font-size:0.9rem;">#{item["id"]}</p>', unsafe_allow_html=True)
                c2.markdown(f'<p style="color:rgba(255,255,255,0.85);font-size:0.92rem;margin:0;padding-top:7px;">{item["text"]}</p>', unsafe_allow_html=True)
                c3.markdown(f'<div style="padding-top:5px;"><span class="badge-status" style="background:{bg};color:{fg};">{item["status"]}</span></div>', unsafe_allow_html=True)
                c4.toggle(
                    "Add description",
                    key=desc_key,
                    help="Include the original transcript sentence in the Jira issue description",
                    label_visibility="collapsed"
                )

if st.session_state.tasks:
    st.markdown('<div class="step-wrap"><div class="step-num-wrap"><div class="step-ring"></div><div class="step-num-inner">4</div></div><p class="step-title">Send to Jira</p></div>', unsafe_allow_html=True)

    if st.button("Sync Selected Tasks to Jira", type="primary", disabled=not st.session_state.final_sync_list):
        synced = []
        with st.spinner("Pushing to Jira..."):
            for item in st.session_state.final_sync_list:
                desc_key = f"desc_toggle_{item['id']}"
                use_desc = st.session_state.get(desc_key, True)
                desc = (item.get("source") or item["text"]) if use_desc else ""
                key = create_jira_issue(item["text"], desc)
                if key:
                    if item["status"] != "To Do":
                        transition_jira_issue(key, item["status"])
                    synced.append({"key": key, "text": item["text"], "status": item["status"]})
        st.session_state.synced_results = synced
        st.rerun()

    if st.session_state.synced_results:
        rows_html = ""
        status_colors = {
            "To Do": ("rgba(156,163,175,0.15)", "#9ca3af"),
            "In Progress": ("rgba(96,165,250,0.15)", "#60a5fa"),
            "Done": ("rgba(16,185,129,0.15)", "#10b981")
        }
        for r in st.session_state.synced_results:
            jira_url = f"https://{JIRA_DOMAIN}/browse/{r['key']}" if JIRA_DOMAIN else "#"
            s_bg, s_fg = status_colors.get(r.get("status", "To Do"), ("rgba(255,255,255,0.1)", "#fff"))
            rows_html += (
                f'<div class="sync-result-row">'
                f'<a href="{jira_url}" target="_blank" class="sync-key-badge">{r["key"]}</a>'
                f'<span style="color:rgba(255,255,255,0.8);font-size:0.9rem;flex-grow:1;">{r["text"]}</span>'
                f'<span class="badge-status" style="background:{s_bg};color:{s_fg};">{r["status"]}</span>'
                f'</div>'
            )
        st.markdown(
            f'<div style="margin-top:1rem;">'
            f'<p style="color:#10b981;font-size:0.88rem;font-weight:600;margin-bottom:0.6rem;">✓ {len(st.session_state.synced_results)} task(s) synced to Jira</p>'
            f'{rows_html}'
            f'</div>',
            unsafe_allow_html=True
        )