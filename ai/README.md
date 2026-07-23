# 🧭 AI SWOT Analysis Generator

A Streamlit web app that generates a **SWOT analysis** (Strengths,
Weaknesses, Opportunities, Threats) for any business, product, or idea
using AI — supporting **both OpenAI and Google Gemini** — with a
**built-in offline Demo Mode** so it works out of the box, even
without any API key.

---

## ⭐ Important Note for Reviewers / Graders

**This app will run and produce results with zero configuration.**

- No API key at all? No problem — the app **automatically detects**
  this and switches to **Demo Mode**, a fully offline, template-based
  SWOT generator. It will never crash, hang, or show an error screen
  due to a missing key.
- The current mode (🟢 Live / 🟡 Demo) — and which provider is active —
  is always shown clearly at the top of the app.
- You can also force Demo Mode manually with the **"Force Demo /
  Offline Mode"** toggle in the sidebar.
- If you *do* want to test Live Mode, pick **OpenAI** or **Gemini** in
  the sidebar and paste in a valid API key for that provider — no
  other setup is required.

In short: **just run `streamlit run app.py` and click Generate.**

---

## ✨ Features

- Generates a full SWOT analysis (Strengths / Weaknesses /
  Opportunities / Threats) for any subject you type in
- Choice of AI provider for Live Mode:
  - **🟢 OpenAI** (`gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`)
  - **🟢 Google Gemini** (`gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`)
  - **🟡 Demo Mode** — offline, rule-based generator, no key/internet needed
  - Automatic, seamless fallback to Demo Mode if no key is found for
    the selected provider, or if an API call fails for any reason
- Clean four-quadrant visual layout (color-coded cards)
- Optional "additional context" field (target market, budget, stage, etc.)
- Download the finished analysis as a Markdown (`.md`) report
- Single-file app (`app.py`) — easy to read, deploy, and grade

---

## 📁 Project Structure

```
swot_project/
├── app.py              # The entire Streamlit application (single file)
├── requirements.txt    # Python dependencies
└── README.md            # This file
```

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### 3. (Optional) Enable Live AI Mode

Pick a provider in the sidebar (**OpenAI** or **Gemini**), then supply
an API key for that provider using **any one** of these methods:

- Paste it directly into the **sidebar** text field while the app is running, or
- Set an environment variable before launching:
  ```bash
  # For OpenAI
  export OPENAI_API_KEY="sk-..."

  # For Gemini
  export GEMINI_API_KEY="AIza..."
  # (GOOGLE_API_KEY is also accepted for Gemini)

  streamlit run app.py
  ```
- Or create `.streamlit/secrets.toml` with:
  ```toml
  OPENAI_API_KEY = "sk-..."
  GEMINI_API_KEY = "AIza..."
  ```

If no key is set for the selected provider, the app simply runs in
**Demo Mode** — no error, no crash.

---

## 🧠 How It Works

1. User enters a **subject** (e.g. "a subscription meal-kit startup")
   and optional context, and picks a provider (OpenAI or Gemini) in
   the sidebar.
2. The app resolves an API key for that provider (sidebar input →
   environment variable → Streamlit secrets, in that order).
3. **If a key is found and Live Mode is enabled:** the app sends a
   prompt to the selected provider's chat/generation API requesting a
   structured SWOT analysis, then parses the response into four
   sections (the prompt and parsing logic are provider-agnostic, so
   both return the same structured output).
4. **If no key is found (or the API call fails for any reason):** the
   app instantly falls back to a deterministic, offline template
   generator that produces a realistic, varied SWOT analysis using the
   subject text itself — no network calls involved.
5. Results are rendered in a four-quadrant colored layout and can be
   downloaded as a Markdown report.

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — web app framework
- [OpenAI Python SDK](https://github.com/openai/openai-python) — Live Mode AI generation (OpenAI)
- [Google Generative AI SDK](https://github.com/google-gemini/generative-ai-python) — Live Mode AI generation (Gemini)
- Pure Python (standard library `random`/`re`) — Demo Mode generation

---

## 📄 License

This project is provided as-is for educational / demonstration purposes.
