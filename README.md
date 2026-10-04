# 🎤 MockMate

A free interview practice partner for cloud and data analytics jobs. It runs on your own machine using an open-weight model, so your answers never leave your laptop and there is nothing to pay for.

Built for a friend for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01).

## What it does

- Asks interview questions on **Python, Excel, SQL, Power BI and Cloud basics**
- Lets you pick a level: **Fresher** or **Intermediate**
- Scores your answer out of 10 and shows **what was good**, **what was missing**, and a **stronger sample answer**
- Saves every attempt and shows your **average per topic** and your **weakest topic** in a Progress tab

## Tech stack (all open source)

| Part | Tool |
|------|------|
| Model | `qwen2.5:7b` (open weights) |
| Local inference | [Ollama](https://ollama.com) |
| Interface | [Streamlit](https://streamlit.io) |
| Storage | SQLite (a single local file, `mockmate.db`) |

## Setup

1. Install [Ollama](https://ollama.com/download) and pull the model:

   ```bash
   ollama pull qwen2.5:7b
   ```

2. Install the Python packages:

   ```bash
   pip install streamlit requests
   ```

3. Run the app:

   ```bash
   streamlit run mockmate.py
   ```

   Make sure Ollama is running in the background. Then open the link Streamlit prints (usually http://localhost:8501).

## How it works

1. **New question:** the model gets the topic and level and returns one interview question.
2. **Evaluate:** your answer goes back to the model in JSON mode, which forces a fixed structure (`score`, `good`, `missing`, `better_answer`). The score is clamped to 1 to 10.
3. **Progress:** each attempt is stored in SQLite, and the Progress tab averages scores per topic.

## Customise it

All in `mockmate.py`:

- **Different model:** change `MODEL = "qwen2.5:7b"` to any model you have pulled in Ollama.
- **Different topics:** edit the `TOPICS` dictionary.
- **Different job market or role:** edit the interviewer prompt in `new_question()`.

## Why open source matters here

Interview practice means giving weak answers you don't want on someone else's server. Running an open model locally keeps that private, makes it free to use every day, and lets you reshape the interviewer for one specific person.

## Troubleshooting

- **"Can't reach Ollama":** start Ollama and check that `ollama list` shows `qwen2.5:7b`.
- **Slow responses:** a 7B model on CPU can take a while. Try a smaller model such as `qwen2.5:3b`.

## Licence

MIT
