"""
styles.py — All visual styling lives here, separate from app logic.

Two text colors are used deliberately:
  --text-light (cream)  -> for anything sitting directly on the dark maroon page background
  --text-dark  (charcoal) -> for anything sitting inside a light card/surface/button

Inject CSS once at the top of the app, and use stamp_html() anywhere
a moment deserves the 'official ink stamp' treatment.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700;800&family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #3A0D12;
    --surface: #FFF8F0;
    --border: #E8D4C2;
    --gold: #E8B339;
    --green: #2E9E72;
    --red: #D6483F;
    --gray: #6B6F76;
    --text-light: #F5E8DA;
    --text-dark: #2E1B14;
    --muted: #8C6F62;
}

/* Slightly larger base font size site-wide — most rem-based sizes below
   scale automatically from this, since 1rem = the html font-size. */
html {
    font-size: 19px;
}

/* App background + default body text (sits directly on the dark bg) */
.stApp {
    background-color: var(--bg);
    color: var(--text-light);
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
}

.stApp p, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3,
.stApp .stMarkdown, .stApp .stRadio, .stApp .stSelectbox {
    color: var(--text-light);
    font-size: 1.05rem;
}

/* Arabic app title */
.app-title {
    font-family: 'Cairo', sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    color: var(--gold);
    text-align: center;
    margin-bottom: 0.2rem;
}

.app-subtitle {
    text-align: center;
    color: var(--text-light);
    opacity: 0.75;
    font-size: 0.85rem;
    margin-bottom: 1.2rem;
}

/* Score card (light surface -> needs dark text) */
.score-card {
    background-color: var(--surface);
    border-radius: 18px;
    padding: 1.4rem 1rem;
    text-align: center;
    margin-bottom: 1rem;
    border: 1px solid var(--border);
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}

.score-team-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: var(--muted);
    letter-spacing: 0.03em;
}

.score-number {
    font-family: 'Space Grotesk', monospace;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--text-dark);
}

.score-number.winning {
    color: var(--green);
}

/* ===== Buttons ===== */
div.stButton > button, div.stFormSubmitButton > button {
    border-radius: 12px;
    font-weight: 600;
    font-size: 1.05rem;
    border: none;
    padding: 0.7rem 1rem;
    color: #FFFFFF;
    background-color: var(--gray);
}

/* Primary actions (Start Game, Confirm & Save, Continue) -> gold, dark text */
div.stButton > button[kind="primary"] {
    background-color: var(--gold) !important;
    color: var(--text-dark) !important;
}

/* Add Round -> green, white text */
.st-key-btn_add_round button {
    background-color: var(--green) !important;
    color: #FFFFFF !important;
}

/* Qaid -> red, white text */
.st-key-btn_qaid button {
    background-color: var(--red) !important;
    color: #FFFFFF !important;
}

/* Undo -> gray, white text */
.st-key-btn_undo button {
    background-color: var(--gray) !important;
    color: #FFFFFF !important;
}

/* Confirm buttons inside panels -> gold, dark text */
.st-key-btn_confirm_round button,
.st-key-btn_confirm_qaid button {
    background-color: var(--gold) !important;
    color: var(--text-dark) !important;
}

/* Cancel buttons inside panels -> cream (light button), dark text */
.st-key-btn_cancel_round button,
.st-key-btn_cancel_qaid button {
    background-color: var(--surface) !important;
    border: 1px solid var(--muted) !important;
    color: var(--text-dark) !important;
}

/* Round history row (light surface -> needs dark text) */
.round-row {
    display: flex;
    justify-content: space-between;
    background-color: var(--surface);
    border-radius: 10px;
    padding: 0.5rem 0.9rem;
    margin-bottom: 0.4rem;
    font-family: 'Space Grotesk', monospace;
    font-size: 1.05rem;
    border: 1px solid var(--border);
    color: var(--text-dark);
}

.round-row.qaid {
    border: 1px solid var(--red);
    color: var(--red);
}

/* Ink stamp badge (sits on light surface) */
.stamp {
    font-family: 'Cairo', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    text-align: center;
    padding: 0.8rem 1.2rem;
    border: 4px solid currentColor;
    border-radius: 10px;
    display: block;
    width: fit-content;
    margin: 1rem auto;
    transform: rotate(-4deg);
    letter-spacing: 0.08em;
    animation: stamp-hit 0.25s ease-out;
    background-color: var(--surface);
}

@keyframes stamp-hit {
    0%   { transform: rotate(-4deg) scale(1.6); opacity: 0; }
    60%  { transform: rotate(-4deg) scale(0.95); opacity: 1; }
    100% { transform: rotate(-4deg) scale(1); }
}

.stamp.win { color: var(--green); }
.stamp.qaid { color: var(--red); }
</style>
"""


def stamp_html(text: str, kind: str = "win") -> str:
    """
    Returns an HTML snippet for an ink-stamp style badge.
    kind: 'win' (green) or 'qaid' (red)
    """
    return f'<div class="stamp {kind}">{text}</div>'