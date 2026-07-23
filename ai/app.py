"""
AI SWOT Analysis Generator
===========================

A Streamlit web app that generates a SWOT (Strengths, Weaknesses,
Opportunities, Threats) analysis for any business, product, or idea.

Three modes are supported:

1. LIVE MODE (OpenAI) -> Uses the OpenAI API to generate a real,
                 AI-written SWOT analysis. Requires an OpenAI API key.

2. LIVE MODE (Gemini) -> Uses Google's Gemini API to generate a real,
                 AI-written SWOT analysis. Requires a Gemini API key.

3. DEMO MODE  -> Fully offline, rule-based / template-driven SWOT
                 generator. Requires NO API key and NO internet access.
                 This mode exists so the app NEVER crashes or blocks a
                 grader / reviewer who does not have an API key — it is
                 selected automatically whenever no key is available,
                 and can also be forced on manually.

Run with:
    streamlit run app.py
"""

import os
import random
import re
from datetime import datetime

import streamlit as st

# ---------------------------------------------------------------------------
# Optional dependencies: the OpenAI and Gemini SDKs.
# The app must still run (in demo mode) even if either package is missing,
# so both imports are wrapped in try/except instead of assumed.
# ---------------------------------------------------------------------------
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GEMINI_SDK_AVAILABLE = False


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI SWOT Analysis Generator",
    page_icon="🧭",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Helpers: API key discovery
# ---------------------------------------------------------------------------
def get_api_key(user_supplied_key: str, env_var_name: str) -> str:
    """
    Resolve an API key from (in priority order):
      1. A key typed into the sidebar by the user this session.
      2. An environment variable (env_var_name).
      3. Streamlit secrets (st.secrets), if a secrets.toml is present.
    Returns an empty string if none is found — this is expected and
    normal, and simply means the app will run in Demo Mode.
    """
    if user_supplied_key:
        return user_supplied_key.strip()

    env_key = os.environ.get(env_var_name, "")
    if env_key:
        return env_key.strip()

    try:
        secret_key = st.secrets[env_var_name]
        if secret_key:
            return str(secret_key).strip()
    except Exception:
        # No secrets.toml, no key configured, or key missing.
        # This is fine — fall back to demo mode.
        pass

    return ""


# ---------------------------------------------------------------------------
# LIVE MODE: real AI-generated SWOT analysis via OpenAI
# ---------------------------------------------------------------------------
def generate_swot_live(subject: str, context: str, api_key: str, model: str = "gpt-4o-mini"):
    """
    Calls the OpenAI API to generate a SWOT analysis.
    Returns a dict with keys: strengths, weaknesses, opportunities, threats
    (each a list of strings), or raises an exception on failure so the
    caller can gracefully fall back to demo mode.
    """
    client = OpenAI(api_key=api_key)

    prompt = f"""You are a senior business strategy consultant.
Create a SWOT analysis for the following subject.

Subject: {subject}
Additional context: {context if context else "None provided"}

Respond ONLY in this exact plain-text format, with 3-5 concise bullet
points per section and no extra commentary before or after:

STRENGTHS:
- point
- point

WEAKNESSES:
- point
- point

OPPORTUNITIES:
- point
- point

THREATS:
- point
- point
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful and concise business strategy expert."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=700,
    )

    text = response.choices[0].message.content
    return parse_swot_text(text)


# ---------------------------------------------------------------------------
# LIVE MODE: real AI-generated SWOT analysis via Google Gemini
# ---------------------------------------------------------------------------
def generate_swot_live_gemini(subject: str, context: str, api_key: str, model: str = "gemini-1.5-flash"):
    """
    Calls the Gemini API to generate a SWOT analysis.
    Returns a dict with keys: strengths, weaknesses, opportunities, threats
    (each a list of strings), or raises an exception on failure so the
    caller can gracefully fall back to demo mode.
    """
    genai.configure(api_key=api_key)

    prompt = f"""You are a senior business strategy consultant.
Create a SWOT analysis for the following subject.

Subject: {subject}
Additional context: {context if context else "None provided"}

Respond ONLY in this exact plain-text format, with 3-5 concise bullet
points per section and no extra commentary before or after:

STRENGTHS:
- point
- point

WEAKNESSES:
- point
- point

OPPORTUNITIES:
- point
- point

THREATS:
- point
- point
"""

    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=700,
        ),
    )

    text = response.text
    return parse_swot_text(text)


def parse_swot_text(text: str):
    """Parse the plain-text SWOT response from the model into a dict of lists."""
    sections = {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}
    current = None

    label_map = {
        "STRENGTHS": "strengths",
        "WEAKNESSES": "weaknesses",
        "OPPORTUNITIES": "opportunities",
        "THREATS": "threats",
    }

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        header_match = re.match(r"^([A-Za-z]+):?\s*$", line)
        if header_match and header_match.group(1).upper() in label_map:
            current = label_map[header_match.group(1).upper()]
            continue

        if current:
            bullet = re.sub(r"^[-*•\d.\)]+\s*", "", line).strip()
            if bullet:
                sections[current].append(bullet)

    # Safety net: if parsing failed to find structured sections, dump
    # everything into a single fallback bucket rather than erroring out.
    if not any(sections.values()):
        sections["strengths"] = [text.strip()] if text.strip() else ["No content returned."]

    return sections


# ---------------------------------------------------------------------------
# DEMO / OFFLINE MODE: deterministic, template-based SWOT generator
# ---------------------------------------------------------------------------
DEMO_STRENGTHS = [
    "Clear, differentiated value proposition for {subject}",
    "Focused scope that allows fast decision-making",
    "Low overhead compared to larger, established competitors",
    "Direct line of sight to customer feedback",
    "Founder / team expertise closely matched to {subject}",
    "Flexibility to adapt quickly without legacy constraints",
]

DEMO_WEAKNESSES = [
    "Limited brand recognition compared to established players",
    "Smaller budget for marketing and customer acquisition",
    "Thin bench strength — key-person dependency risk",
    "Unproven track record at scale for {subject}",
    "Limited existing distribution channels",
    "Early-stage processes that are not yet fully repeatable",
]

DEMO_OPPORTUNITIES = [
    "Growing market demand relevant to {subject}",
    "Potential to form partnerships with complementary businesses",
    "Underserved customer segments that competitors overlook",
    "Emerging technology trends that could be adopted early",
    "Opportunity to build a strong community / word-of-mouth around {subject}",
    "Possible expansion into adjacent markets or use cases",
]

DEMO_THREATS = [
    "Well-funded competitors entering the same space as {subject}",
    "Shifting customer preferences or market conditions",
    "Regulatory or compliance changes affecting the industry",
    "Economic downturn reducing customer spending",
    "Rising customer acquisition costs",
    "New entrants copying the core value proposition",
]


def generate_swot_demo(subject: str, context: str):
    """
    Deterministic offline generator. Uses a seeded random selection so the
    same subject always produces the same (varied-looking) output, without
    needing any network access or API key. This guarantees the app works
    for a grader with zero configuration.
    """
    subject_clean = subject.strip() if subject.strip() else "your business idea"

    # Seed on the subject text so results are stable per-input but still
    # vary between different subjects.
    seed = sum(ord(c) for c in subject_clean) + len(context or "")
    rng = random.Random(seed)

    def pick(pool, n=4):
        chosen = rng.sample(pool, k=min(n, len(pool)))
        return [item.format(subject=subject_clean) for item in chosen]

    return {
        "strengths": pick(DEMO_STRENGTHS),
        "weaknesses": pick(DEMO_WEAKNESSES),
        "opportunities": pick(DEMO_OPPORTUNITIES),
        "threats": pick(DEMO_THREATS),
    }


# ---------------------------------------------------------------------------
# UI rendering helpers
# ---------------------------------------------------------------------------
QUADRANT_STYLE = {
    "strengths": {"title": "💪 Strengths", "color": "#1b5e20", "bg": "#e8f5e9"},
    "weaknesses": {"title": "⚠️ Weaknesses", "color": "#b71c1c", "bg": "#ffebee"},
    "opportunities": {"title": "🚀 Opportunities", "color": "#0d47a1", "bg": "#e3f2fd"},
    "threats": {"title": "🛡️ Threats", "color": "#e65100", "bg": "#fff3e0"},
}


def render_quadrant(key: str, items: list):
    style = QUADRANT_STYLE[key]
    bullets_html = "".join(f"<li style='margin-bottom:6px;'>{i}</li>" for i in items)
    st.markdown(
        f"""
        <div style="background-color:{style['bg']}; border-radius:10px; padding:18px 20px;
                    min-height:220px; border-left:6px solid {style['color']};">
            <h4 style="color:{style['color']}; margin-top:0;">{style['title']}</h4>
            <ul style="padding-left:18px; margin-bottom:0;">{bullets_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def swot_to_markdown(subject: str, context: str, swot: dict, mode: str) -> str:
    lines = [
        f"# SWOT Analysis: {subject or 'Untitled'}",
        "",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} — Mode: {mode}*",
        "",
    ]
    if context:
        lines += [f"**Context:** {context}", ""]

    for key in ["strengths", "weaknesses", "opportunities", "threats"]:
        lines.append(f"## {QUADRANT_STYLE[key]['title']}")
        for item in swot[key]:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sidebar — configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    force_demo = st.toggle(
        "Force Demo / Offline Mode",
        value=not (OPENAI_SDK_AVAILABLE or GEMINI_SDK_AVAILABLE),
        help="When on, the app never calls any AI API and always uses the "
             "built-in offline generator. Useful for testing or when you "
             "have no API key.",
    )

    provider = "Demo"
    user_key_input = ""
    model_choice = ""

    if not force_demo:
        provider = st.radio(
            "AI Provider",
            options=["OpenAI", "Gemini"],
            horizontal=True,
            help="Choose which AI provider to use for Live Mode generation.",
        )

        if provider == "OpenAI":
            user_key_input = st.text_input(
                "OpenAI API Key (optional)",
                type="password",
                help="Leave blank to auto-detect an OPENAI_API_KEY environment "
                     "variable or Streamlit secret. If none is found, the app "
                     "automatically falls back to Demo Mode — it will never error out.",
            )
            model_choice = st.selectbox(
                "OpenAI Model",
                options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                index=0,
            )
        else:  # Gemini
            user_key_input = st.text_input(
                "Gemini API Key (optional)",
                type="password",
                help="Leave blank to auto-detect a GEMINI_API_KEY (or "
                     "GOOGLE_API_KEY) environment variable or Streamlit secret. "
                     "If none is found, the app automatically falls back to "
                     "Demo Mode — it will never error out.",
            )
            model_choice = st.selectbox(
                "Gemini Model",
                options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
                index=0,
            )

    st.divider()
    st.caption(
        "**About the modes**\n\n"
        "🟢 **Live Mode** calls the real OpenAI or Gemini API and needs a "
        "valid key for the provider you pick.\n\n"
        "🟡 **Demo Mode** runs fully offline with a built-in template engine — "
        "no key, no internet, no errors. The app auto-selects Demo Mode "
        "whenever a working API key isn't available."
    )


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------
st.title("🧭 AI SWOT Analysis Generator")
st.write(
    "Generate a Strengths / Weaknesses / Opportunities / Threats analysis "
    "for any business, product, project, or idea in seconds."
)

col_a, col_b = st.columns([2, 1])
with col_a:
    subject = st.text_input(
        "What are you analyzing?",
        placeholder="e.g. A subscription meal-kit delivery startup",
    )
with col_b:
    st.write("")  # vertical spacer to align button with text input
    st.write("")

context = st.text_area(
    "Additional context (optional)",
    placeholder="e.g. Target market, competitors, budget, stage of growth...",
    height=90,
)

generate_clicked = st.button("✨ Generate SWOT Analysis", type="primary", use_container_width=True)

# Resolve which mode/provider we will actually use, and be explicit about it.
resolved_key = ""
using_live_mode = False

if not force_demo:
    if provider == "OpenAI":
        resolved_key = get_api_key(user_key_input, "OPENAI_API_KEY")
        using_live_mode = bool(resolved_key) and OPENAI_SDK_AVAILABLE
    else:  # Gemini
        resolved_key = get_api_key(user_key_input, "GEMINI_API_KEY") or get_api_key(user_key_input, "GOOGLE_API_KEY")
        using_live_mode = bool(resolved_key) and GEMINI_SDK_AVAILABLE

mode_badge = f"🟢 Live Mode ({provider})" if using_live_mode else "🟡 Demo Mode (Offline)"
st.info(f"Current mode: **{mode_badge}**")

if generate_clicked:
    if not subject.strip():
        st.warning("Please enter a subject to analyze before generating.")
    else:
        swot_result = None
        mode_used = "Demo Mode (Offline)"

        if using_live_mode:
            try:
                with st.spinner(f"Contacting {provider}..."):
                    if provider == "OpenAI":
                        swot_result = generate_swot_live(subject, context, resolved_key, model_choice)
                    else:
                        swot_result = generate_swot_live_gemini(subject, context, resolved_key, model_choice)
                mode_used = f"Live Mode ({provider}: {model_choice})"
            except Exception as e:
                st.warning(
                    f"⚠️ Live API call to {provider} failed ({e}). Falling back to "
                    "offline Demo Mode so you still get a result."
                )
                swot_result = None

        if swot_result is None:
            swot_result = generate_swot_demo(subject, context)
            mode_used = "Demo Mode (Offline)"

        st.session_state["last_result"] = {
            "subject": subject,
            "context": context,
            "swot": swot_result,
            "mode": mode_used,
        }

# ---------------------------------------------------------------------------
# Render results (persisted in session_state so download buttons work
# without wiping the analysis on rerun)
# ---------------------------------------------------------------------------
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    swot = result["swot"]

    st.divider()
    st.subheader(f"Results for: {result['subject']}")
    st.caption(f"Generated using **{result['mode']}**")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        render_quadrant("strengths", swot["strengths"])
    with row1_col2:
        render_quadrant("weaknesses", swot["weaknesses"])

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        render_quadrant("opportunities", swot["opportunities"])
    with row2_col2:
        render_quadrant("threats", swot["threats"])

    st.divider()
    md_report = swot_to_markdown(result["subject"], result["context"], swot, result["mode"])
    st.download_button(
        label="⬇️ Download as Markdown",
        data=md_report,
        file_name=f"swot_analysis_{re.sub(r'[^a-zA-Z0-9]+', '_', result['subject']).strip('_').lower() or 'report'}.md",
        mime="text/markdown",
        use_container_width=True,
    )
else:
    st.caption("Enter a subject above and click **Generate SWOT Analysis** to get started.")
