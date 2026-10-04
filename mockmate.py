"""MockMate - a local interview practice partner (Ollama + Streamlit + SQLite).

Setup:
    pip install streamlit requests
    ollama pull qwen2.5:7b
    streamlit run mockmate.py
"""
import json
import sqlite3
import requests
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:7b"
DB = "mockmate.db"

TOPICS = {
    "Python": "Python basics and data packages (pandas, numpy)",
    "Excel": "Excel formulas, pivot tables, lookups",
    "SQL": "SQL queries, joins, aggregation, window functions",
    "Power BI": "Power BI, DAX basics, dashboards",
    "Cloud basics": "cloud fundamentals: AWS/Azure core services, storage, IAM",
}
LEVELS = ["Fresher", "Intermediate"]


def ask_llm(system: str, user: str, as_json: bool = False) -> str:
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if as_json:
        payload["format"] = "json"
    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def db():
    con = sqlite3.connect(DB)
    con.execute(
        "CREATE TABLE IF NOT EXISTS attempts ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT DEFAULT CURRENT_TIMESTAMP,"
        "topic TEXT, level TEXT, question TEXT, answer TEXT, score INTEGER,"
        "feedback TEXT)"
    )
    return con


def new_question(topic: str, level: str, avoid: list) -> str:
    system = (
        "You are a friendly interviewer for entry-level cloud and data analytics "
        "jobs in India. Ask ONE clear interview question. Output only the question."
    )
    user = f"Topic: {TOPICS[topic]}. Level: {level}. Do not repeat: {avoid[-5:]}"
    return ask_llm(system, user)


def evaluate(question: str, answer: str) -> dict:
    system = (
        "You are a kind but honest interviewer. Judge the candidate's answer. "
        'Reply ONLY with JSON: {"score": int 1-10, "good": str, '
        '"missing": str, "better_answer": str}. Keep each field short.'
    )
    raw = ask_llm(system, f"Question: {question}\nAnswer: {answer}", as_json=True)
    try:
        data = json.loads(raw)
        data["score"] = max(1, min(10, int(data.get("score", 5))))
        return data
    except (ValueError, TypeError):
        return {"score": 5, "good": raw, "missing": "", "better_answer": ""}


st.set_page_config(page_title="MockMate", page_icon="🎤")
st.title("🎤 MockMate")
st.caption("Interview practice that runs on your own machine.")

if "asked" not in st.session_state:
    st.session_state.asked = []
    st.session_state.question = None
    st.session_state.result = None

practice, progress = st.tabs(["Practice", "Progress"])

with practice:
    c1, c2 = st.columns(2)
    topic = c1.selectbox("Topic", list(TOPICS))
    level = c2.selectbox("Level", LEVELS)

    if st.button("New question", type="primary"):
        try:
            with st.spinner("Thinking..."):
                q = new_question(topic, level, st.session_state.asked)
            st.session_state.question = q
            st.session_state.asked.append(q)
            st.session_state.result = None
        except requests.RequestException:
            st.error("Can't reach Ollama. Is it running with qwen2.5:7b pulled?")

    if st.session_state.question:
        st.subheader(st.session_state.question)
        answer = st.text_area("Your answer", height=150, key="answer")
        if st.button("Evaluate") and answer.strip():
            with st.spinner("Reading your answer..."):
                res = evaluate(st.session_state.question, answer)
            st.session_state.result = res
            con = db()
            con.execute(
                "INSERT INTO attempts (topic, level, question, answer, score, feedback)"
                " VALUES (?,?,?,?,?,?)",
                (topic, level, st.session_state.question, answer,
                 res["score"], json.dumps(res)),
            )
            con.commit()
            con.close()

    res = st.session_state.result
    if res:
        st.metric("Score", f"{res['score']}/10")
        st.success(f"**Good:** {res.get('good', '')}")
        st.warning(f"**Missing:** {res.get('missing', '')}")
        st.info(f"**Stronger answer:** {res.get('better_answer', '')}")

with progress:
    con = db()
    rows = con.execute(
        "SELECT topic, ROUND(AVG(score),1), COUNT(*) FROM attempts GROUP BY topic"
    ).fetchall()
    con.close()
    if not rows:
        st.write("No attempts yet. Answer a question first.")
    else:
        for t, avg, n in rows:
            st.write(f"**{t}**: average {avg}/10 over {n} answers")
            st.progress(min(1.0, avg / 10))
        weakest = min(rows, key=lambda r: r[1])[0]
        st.info(f"Weakest topic right now: **{weakest}**")
