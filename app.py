import base64
from pathlib import Path
import uuid
import time

import streamlit as st

from rag.pipeline import run_rag_pipeline
from rag.cache import get_redis_client
from rag.input_guardrails import validate_input


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Agri Assist AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PATHS / ASSETS
# =========================================================

APP_DIR = Path(__file__).resolve().parent
ASSETS_DIR = APP_DIR / "assets"

HERO_IMAGE = ASSETS_DIR / "hero.png"
SIDEBAR_IMAGE = ASSETS_DIR / "sidebar-card.png"
SUSTAINABLE_IMAGE = ASSETS_DIR / "sustainable.png"


# =========================================================
# SCHEME OPTIONS
# =========================================================

SCHEME_OPTIONS = {
    "All Schemes": None,
    "PM-KISAN": "PM_KISAN",
    "PMFBY – Crop Insurance": "PMFBY",
    "Kisan Credit Card (KCC)": "KCC",
    "PM Krishi Sinchai Yojana": "PM_KRISHI_SINCHAI",
    "Soil Health Card": "SOIL_HEALTH_CARD",
    "National Mission for Sustainable Agriculture": "NMSA",
    "Agricultural Mechanization": "AGRI_MECHANIZATION",
    "PM-KUSUM": "PM_KUSUM",
    "Weather Based Crop Insurance Scheme": "WBCIS",
    "Coconut Palm Insurance Scheme": "CPIS",
    "Unified Package Insurance Scheme": "UPIS",
    "PM Kisan Maandhan Yojana": "PM_KISAN_MAAN_DHAN",
    "Dairy Interest Subvention": "DAIRY_INTEREST_SUBVENTION",
}


# =========================================================
# ROLE INFORMATION
# =========================================================

ROLE_LABELS = {
    "farmer": "👨‍🌾 Farmer",
    "public": "👤 Public",
    "government": "🏛️ Government",
    "agency": "🤝 Agency",
}


# =========================================================
# DYNAMIC SCHEME CONTENT
# =========================================================

SCHEME_CONTENT = {
    None: {
        "tip": (
            "Explore agriculture government schemes for "
            "farmer benefits, insurance, irrigation, credit "
            "and other support."
        ),
        "questions": [
            "Who is eligible for PM-KISAN?",
            "How much financial assistance is available?",
            "What crop insurance schemes are available?",
            "What support is available for irrigation?",
            "What documents are usually required?",
        ],
    },

    "PM_KISAN": {
        "tip": (
            "PM-KISAN provides direct financial support to "
            "eligible landholding farmer families."
        ),
        "questions": [
            "Who is eligible for PM-KISAN?",
            "How much do eligible farmers get?",
            "How often is PM-KISAN paid?",
            "Who is excluded from PM-KISAN?",
            "What are the main benefits of PM-KISAN?",
        ],
    },

    "PMFBY": {
        "tip": (
            "Crop insurance can help protect farmers against "
            "covered crop losses and specified risks."
        ),
        "questions": [
            "What is PMFBY?",
            "Who can get crop insurance?",
            "What benefits are provided under PMFBY?",
            "What risks are covered?",
            "How can I apply for crop insurance?",
        ],
    },

    "KCC": {
        "tip": (
            "Kisan Credit Card helps farmers access timely "
            "credit for agricultural needs."
        ),
        "questions": [
            "Who is eligible for KCC?",
            "What benefits does KCC provide?",
            "How much financial assistance is available?",
            "What documents are required?",
            "How can I apply for KCC?",
        ],
    },

    "PM_KRISHI_SINCHAI": {
        "tip": (
            "PM Krishi Sinchai Yojana supports irrigation and "
            "better water management for agriculture."
        ),
        "questions": [
            "What assistance is available for micro irrigation?",
            "What support is available for drip irrigation?",
            "What support is available for sprinkler irrigation?",
            "What help is available for water management?",
            "What assistance is available for irrigation systems?",
        ],
    },

    "SOIL_HEALTH_CARD": {
        "tip": (
            "Soil Health Card support helps farmers understand "
            "soil conditions and nutrient requirements."
        ),
        "questions": [
            "What is the Soil Health Card?",
            "Who can benefit from the scheme?",
            "What information does the card provide?",
            "What are the benefits for farmers?",
            "How can farmers use the soil recommendations?",
        ],
    },

    "NMSA": {
        "tip": (
            "The National Mission on Sustainable Agriculture "
            "promotes climate-resilient and resource-efficient farming."
        ),
        "questions": [
            "What is NMSA?",
            "Who can benefit from NMSA?",
            "What support is available?",
            "How does NMSA support climate resilience?",
            "What resource-efficient practices are supported?",
        ],
    },

    "AGRI_MECHANIZATION": {
        "tip": (
            "Agricultural mechanization support can help farmers "
            "access modern equipment and improve farm efficiency."
        ),
        "questions": [
            "What agricultural machinery support is available?",
            "Who can get mechanization assistance?",
            "What equipment can be supported?",
            "What subsidy is available for farm machinery?",
            "What are the benefits of mechanization?",
        ],
    },

    "PM_KUSUM": {
        "tip": (
            "PM-KUSUM supports solar pumps and renewable energy "
            "solutions for agricultural irrigation."
        ),
        "questions": [
            "What is PM-KUSUM?",
            "Who can benefit from PM-KUSUM?",
            "What support is available for solar pumps?",
            "How can solar energy help farmers?",
            "What are the benefits of PM-KUSUM?",
        ],
    },

    "WBCIS": {
        "tip": (
            "Weather Based Crop Insurance Scheme supports "
            "farmers against specified weather-related risks."
        ),
        "questions": [
            "What is WBCIS?",
            "Who is eligible for WBCIS?",
            "What weather risks are covered?",
            "What benefits does WBCIS provide?",
            "How can I get weather-based crop insurance?",
        ],
    },

    "CPIS": {
        "tip": (
            "Coconut Palm Insurance Scheme provides insurance "
            "support for covered coconut palms."
        ),
        "questions": [
            "What is the Coconut Palm Insurance Scheme?",
            "Who can benefit from CPIS?",
            "What does CPIS cover?",
            "What are the benefits of CPIS?",
            "How can I apply?",
        ],
    },

    "UPIS": {
        "tip": (
            "The Unified Package Insurance Scheme brings together "
            "insurance-related support for eligible beneficiaries."
        ),
        "questions": [
            "What is the Unified Package Insurance Scheme?",
            "Who can benefit from UPIS?",
            "What coverage is available?",
            "What are the major benefits?",
            "How can I apply?",
        ],
    },

    "PM_KISAN_MAAN_DHAN": {
        "tip": (
            "PM Kisan Maandhan Yojana supports eligible small and "
            "marginal farmers through a pension-oriented scheme."
        ),
        "questions": [
            "What is PM Kisan Maandhan Yojana?",
            "Who is eligible?",
            "What benefits are available?",
            "How does the pension support work?",
            "How can I apply?",
        ],
    },

    "DAIRY_INTEREST_SUBVENTION": {
        "tip": (
            "Interest subvention can reduce the financing burden "
            "for eligible dairy-sector activities."
        ),
        "questions": [
            "What is dairy interest subvention?",
            "Who is eligible?",
            "What financial support is available?",
            "What activities are covered?",
            "How can I apply?",
        ],
    },
}


# =========================================================
# IMAGE HELPERS
# =========================================================

def image_data_uri(path: Path) -> str | None:
    """
    Convert a local image into a data URI so it can be safely
    embedded inside HTML/CSS rendered by Streamlit.
    """

    if not path.exists():
        return None

    try:
        mime = "image/png"

        if path.suffix.lower() in {".jpg", ".jpeg"}:
            mime = "image/jpeg"
        elif path.suffix.lower() == ".webp":
            mime = "image/webp"

        encoded = base64.b64encode(
            path.read_bytes()
        ).decode("utf-8")

        return f"data:{mime};base64,{encoded}"

    except OSError:
        return None


HERO_URI = image_data_uri(HERO_IMAGE)
SIDEBAR_URI = image_data_uri(SIDEBAR_IMAGE)
SUSTAINABLE_URI = image_data_uri(SUSTAINABLE_IMAGE)


# =========================================================
# UI STREAMING HELPER
# =========================================================

def stream_answer_text(
    placeholder,
    answer: str,
    delay: float = 0.018,
    chunk_size: int = 2,
) -> None:
    """
    Display an already-generated answer using a visible
    character-by-character typewriter effect.

    The RAG backend remains unchanged. This is presentation
    only, so the final generated answer is still the exact
    grounded answer returned by the pipeline.
    """

    if not answer:
        return

    text = str(answer)
    displayed = ""

    for index in range(0, len(text), max(1, chunk_size)):

        displayed += text[index:index + chunk_size]

        placeholder.markdown(
            displayed + '<span class="streaming-cursor">▌</span>',
            unsafe_allow_html=True,
        )

        time.sleep(delay)

    placeholder.markdown(
        displayed
    )


# =========================================================
# REDIS CACHE HELPERS
# =========================================================

def clear_conversation_cache(
    role: str,
    conversation_id: str,
) -> None:
    """
    Delete Redis entries belonging only to the specified
    role + conversation.

    We do NOT flush the entire Redis database.
    """

    try:
        client = get_redis_client()

        pattern = (
            f"rag:{role}:{conversation_id}:*"
        )

        keys = list(
            client.scan_iter(
                match=pattern
            )
        )

        if keys:
            client.delete(*keys)

    except Exception:
        # Cache cleanup must never prevent the app from running.
        pass


# =========================================================
# SESSION STATE
# =========================================================

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = (
        f"streamlit_user_{uuid.uuid4().hex}"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_scheme" not in st.session_state:
    st.session_state.selected_scheme = "All Schemes"

if "role_selector" not in st.session_state:
    st.session_state.role_selector = "farmer"

if "active_role" not in st.session_state:
    st.session_state.active_role = "farmer"

if "active_scheme" not in st.session_state:
    st.session_state.active_scheme = "All Schemes"

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


# =========================================================
# RESET CALLBACKS
# =========================================================

def reset_for_role_change():
    """
    Start a brand-new conversation when the profile changes.
    """

    old_role = st.session_state.get(
        "active_role",
        "farmer",
    )

    old_conversation_id = st.session_state.get(
        "conversation_id",
        "",
    )

    clear_conversation_cache(
        old_role,
        old_conversation_id,
    )

    st.session_state.messages = []

    st.session_state.conversation_id = (
        f"streamlit_user_{uuid.uuid4().hex}"
    )

    st.session_state.active_role = (
        st.session_state.role_selector
    )

    st.session_state.pending_query = None


def reset_for_scheme_change():
    """
    Start a clean context when the selected scheme changes.

    This avoids carrying a follow-up such as "How much do
    they get?" from one scheme into another.
    """

    old_role = st.session_state.get(
        "active_role",
        "farmer",
    )

    old_conversation_id = st.session_state.get(
        "conversation_id",
        "",
    )

    clear_conversation_cache(
        old_role,
        old_conversation_id,
    )

    st.session_state.messages = []

    st.session_state.conversation_id = (
        f"streamlit_user_{uuid.uuid4().hex}"
    )

    st.session_state.active_scheme = (
        st.session_state.scheme_selector
    )

    st.session_state.pending_query = None
    st.session_state.selected_scheme = (
        st.session_state.scheme_selector
    )


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

:root {
    --agri-dark: #205b42;
    --agri-green: #3f7d4d;
    --agri-light: #eaf5e5;
    --agri-border: #d7e5d1;
    --agri-text: #24372a;
    --agri-muted: #617066;
}


/* ========================================================
   GLOBAL
======================================================== */

.stApp {
    background:
        radial-gradient(
            circle at 7% 8%,
            rgba(220, 239, 210, 0.72),
            transparent 26%
        ),
        radial-gradient(
            circle at 92% 10%,
            rgba(255, 239, 190, 0.42),
            transparent 24%
        ),
        linear-gradient(
            135deg,
            #f3f8ef 0%,
            #fffdf7 55%,
            #eef7ea 100%
        );
}

.main .block-container {
    max-width: 1450px;
    padding-top: 1.1rem;
    padding-bottom: 5.5rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
}


/* ========================================================
   SIDEBAR
======================================================== */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #edf7e8 0%,
            #f5faef 60%,
            #fffdf6 100%
        );

    border-right: 1px solid var(--agri-border);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--agri-dark);
}

.sidebar-brand {
    text-align: center;
    padding: 0.2rem 0 1rem;
}

.sidebar-brand-icon {
    font-size: 3.25rem;
    line-height: 1;
}

.sidebar-brand-name {
    color: var(--agri-dark);
    font-size: 1.42rem;
    font-weight: 800;
    margin-top: 0.4rem;
}

.sidebar-brand-tagline {
    color: #6d7d72;
    font-size: 0.8rem;
    margin-top: 0.15rem;
}

.sidebar-card {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid var(--agri-border);
    border-radius: 18px;
    overflow: hidden;
    margin-top: 1rem;
    box-shadow: 0 6px 18px rgba(45, 83, 52, 0.06);
}

.sidebar-card img {
    width: 100%;
    display: block;
}

.sidebar-text-card {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid var(--agri-border);
    border-radius: 16px;
    padding: 1rem;
    margin-top: 1rem;
}

.sidebar-info-title {
    color: var(--agri-dark);
    font-weight: 800;
    margin-bottom: 0.45rem;
}

.sidebar-info-text {
    color: var(--agri-muted);
    font-size: 0.88rem;
    line-height: 1.6;
}


/* ========================================================
   SELECT BOXES
======================================================== */

div[data-baseweb="select"] > div {
    background: white;
    border: 1px solid #cbdcc5;
    border-radius: 13px;
    min-height: 44px;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: var(--agri-green);
    box-shadow: 0 0 0 2px rgba(63, 125, 77, 0.08);
}


/* ========================================================
   TOP BAR
======================================================== */

.top-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.15rem 0 0.75rem;
    color: #315c45;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.top-bar span {
    opacity: 0.88;
}


/* ========================================================
   HERO IMAGE
======================================================== */

.hero-image-wrap {
    width: 100%;
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 1.15rem;
    box-shadow:
        0 14px 35px rgba(35, 91, 66, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.75);
    background: linear-gradient(
        135deg,
        #205b42,
        #619b57
    );
}

.hero-image-wrap img {
    width: 100%;
    display: block;
}


/* ========================================================
   WELCOME / CHAT CARD
======================================================== */

.chat-shell {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #dce8d6;
    border-radius: 24px;
    padding: 1.2rem 1.35rem 0.65rem;
    box-shadow:
        0 8px 24px rgba(46, 79, 51, 0.07);
}

.welcome-heading {
    color: #183a2a;
    font-size: 1.25rem;
    font-weight: 800;
}

.welcome-description {
    color: #657368;
    font-size: 0.92rem;
    margin-top: 0.3rem;
    margin-bottom: 0.8rem;
}


/* ========================================================
   RIGHT PANEL
======================================================== */

.right-card {
    background: rgba(255, 255, 255, 0.93);
    border: 1px solid #dce8d6;
    border-radius: 20px;
    padding: 1rem 1rem 0.9rem;
    margin-bottom: 0.95rem;
    box-shadow: 0 7px 20px rgba(46, 79, 51, 0.055);
}

.right-card.tip {
    background:
        linear-gradient(
            145deg,
            #eff9e9 0%,
            #e4f4db 100%
        );
}

.right-title {
    color: #214f38;
    font-size: 1.02rem;
    font-weight: 800;
    margin-bottom: 0.55rem;
}

.right-body {
    color: #5e6f63;
    font-size: 0.88rem;
    line-height: 1.55;
}

.scheme-badge {
    display: inline-block;
    background: #eef7ea;
    color: #2d6446;
    border: 1px solid #d4e6ce;
    border-radius: 999px;
    padding: 0.33rem 0.65rem;
    font-size: 0.74rem;
    font-weight: 700;
    margin-bottom: 0.65rem;
}

/* ========================================================
   FINAL EXAMPLE QUESTIONS
   ======================================================== */

.example-questions-card {
    padding: 0.8rem 0.75rem 0.55rem !important;
}

.example-questions-card .right-title {
    margin-bottom: 0.25rem !important;
    line-height: 1.2 !important;
}

/* Remove Streamlit's extra vertical gaps around each button. */
.example-questions-card
div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

.example-questions-card
div[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
}

.example-questions-card
div[data-testid="stButton"] > button {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;

    width: 100% !important;
    min-height: 40px !important;
    height: auto !important;

    margin: 0 !important;
    padding: 0.38rem 1.2rem 0.38rem 1.15rem !important;

    background: transparent !important;
    border: 0 !important;
    border-bottom: 1px solid #edf1eb !important;
    border-radius: 7px !important;
    box-shadow: none !important;

    color: #405247 !important;
    text-align: left !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;

    font-size: 0.8rem !important;
    font-weight: 500 !important;
    line-height: 1.3 !important;
}

.example-questions-card
div[data-testid="stButton"] > button:hover {
    background: #f5faef !important;
    color: #24563c !important;
}

/* Bullet is fixed to the left of every row. */
.example-questions-card
div[data-testid="stButton"] > button::before {
    content: "•";
    position: absolute;
    left: 0.18rem;
    top: 50%;
    transform: translateY(-50%);
    color: #4c8a58;
    font-size: 0.92rem;
    font-weight: 700;
}

/* Arrow is fixed to the far right and never wraps. */
.example-questions-card
div[data-testid="stButton"] > button::after {
    content: "›";
    position: absolute;
    right: 0.18rem;
    top: 50%;
    transform: translateY(-50%);
    color: #4c8a58;
    font-size: 1rem;
    line-height: 1;
    font-weight: 500;
}

.example-questions-card
div[data-testid="stButton"] > button > div {
    display: block !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
}

.example-questions-card
div[data-testid="stButton"] > button p {
    display: block !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
    line-height: 1.3 !important;
}

.example-questions-card
div[data-testid="stButton"]:last-child > button {
    border-bottom: none !important;
}

@media (max-width: 768px) {
    .example-questions-card
    div[data-testid="stButton"] > button {
        min-height: 38px !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
        font-size: 0.77rem !important;
    }
}

/* Keep the top slogan on the right. */
.top-bar {
    justify-content: flex-end !important;
    text-align: right !important;
}

/* ========================================================
   EXPLICIT CHAT ALIGNMENT
   ======================================================== */

.chat-user-slot {
    text-align: left;
}

.chat-assistant-slot {
    text-align: right;
}

@media (max-width: 768px) {
    div[data-testid="stButton"] > button {
        min-height: 40px !important;
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
        font-size: 0.8rem !important;
    }
}

.sustainable-wrap {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid #dce8d6;
    box-shadow: 0 7px 20px rgba(46, 79, 51, 0.055);
}

.sustainable-wrap img {
    width: 100%;
    display: block;
}


/* ========================================================
   CHAT MESSAGE APPEARANCE
======================================================== */

[data-testid="stChatMessage"] {
    border-radius: 18px;
    margin-bottom: 0.45rem;
}

[data-testid="stChatMessageContent"] {
    color: #2c3b31;
    line-height: 1.68;
}


/* ========================================================
   CHAT INPUT
======================================================== */

[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] > div {
    background: white !important;
    border: 2px solid #7fb687 !important;
    border-radius: 22px !important;
    padding: 4px 8px 4px 10px !important;
    box-shadow:
        0 6px 20px rgba(45, 83, 52, 0.10) !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: #3f7d4d !important;
    box-shadow:
        0 7px 22px rgba(45, 83, 52, 0.13),
        0 0 0 3px rgba(76, 138, 88, 0.10) !important;
}

[data-testid="stChatInput"] textarea {
    background-color: white !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #26352b !important;
    font-size: 1rem !important;
    line-height: 1.5 !important;
    padding: 12px 8px 12px 48px !important;

    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'%3E%3Cpath d='M14.5 25C14.5 17.4 15.8 10.4 23.6 5.2C24.4 4.7 25.4 4.1 26.3 3.7C25.7 6.8 24.3 10.3 22.1 12.8C19.9 15.3 17.4 16.8 15 17.8' fill='%23ecf7e8' stroke='%233f7d4d' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M14.7 25C14.1 18.2 10.8 12.2 3.7 8.9C3 8.6 2.3 8.3 1.7 8.2C2.1 11.5 3.2 14.4 5.5 16.4C7.7 18.4 10.3 19.2 13.8 20' fill='%23f1f9ed' stroke='%233f7d4d' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M14.5 25C14.5 18.6 13 13.1 8.5 8.8' fill='none' stroke='%233f7d4d' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat !important;
    background-position: 10px center !important;
    background-size: 30px 30px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #7b897e !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button {
    background: #3f7d4d !important;
    border: none !important;
    border-radius: 16px !important;
    width: 42px !important;
    height: 42px !important;
}

[data-testid="stChatInput"] button:hover {
    background: #285943 !important;
}

[data-testid="stChatInput"] button svg {
    color: white !important;
}


/* ========================================================
   BUTTONS
======================================================== */

.stButton > button {
    border-radius: 12px;
}


/* ========================================================
   CLEANUP
======================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}


/* ========================================================
   MOBILE
======================================================== */

@media (max-width: 1100px) {
    .main .block-container {
        max-width: 100%;
    }
}

@media (max-width: 768px) {

    .main .block-container {
        padding-top: 0.7rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
        padding-bottom: 5rem;
    }

    .hero-image-wrap {
        border-radius: 18px;
    }

    .chat-shell {
        border-radius: 18px;
        padding: 1rem;
    }

    .right-card {
        border-radius: 17px;
    }

}


/* Final Example Questions spacing/alignment override. */
.example-questions-card {
    overflow: hidden;
}

.example-questions-card div[data-testid="stVerticalBlock"] {
    gap: 0.1rem !important;
}

.example-questions-card div[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
}

.example-questions-card div[data-testid="stButton"] > button {
    justify-content: flex-start !important;
    text-align: left !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    margin: 0 !important;
    padding: 0.34rem 0.05rem !important;
    min-height: 40px !important;
    border-radius: 8px !important;
    line-height: 1.28 !important;
    font-size: 0.82rem !important;
}

.example-questions-card div[data-testid="stButton"] > button > div {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0 !important;
    margin: 0 !important;
}

.example-questions-card div[data-testid="stButton"] p {
    width: 100% !important;
    text-align: left !important;
    padding: 0 !important;
    margin: 0 !important;
}



/* ==========================================================
   POLISHED EXAMPLE QUESTION LIST
   ========================================================== */

.example-questions-card {
    padding: 0.85rem 0.85rem 0.7rem !important;
}

.example-questions-card .right-title {
    margin-bottom: 0.35rem !important;
    line-height: 1.2 !important;
}

.example-questions-card div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

.example-questions-card div[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
}

.example-questions-card div[data-testid="stButton"] > button {
    width: 100% !important;
    min-height: 42px !important;
    height: auto !important;

    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;

    padding: 0.38rem 0.1rem !important;
    margin: 0 !important;

    background: transparent !important;
    border: 0 !important;
    border-bottom: 1px solid #edf1eb !important;
    border-radius: 0 !important;
    box-shadow: none !important;

    color: #405247 !important;
    text-align: left !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;

    font-size: 0.82rem !important;
    font-weight: 500 !important;
    line-height: 1.32 !important;
}

.example-questions-card div[data-testid="stButton"]:last-child > button {
    border-bottom: 0 !important;
}

.example-questions-card div[data-testid="stButton"] > button:hover {
    color: #24563c !important;
    background: #f5faef !important;
}

.example-questions-card div[data-testid="stButton"] > button > div {
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 0 !important;
    margin: 0 !important;
}

.example-questions-card div[data-testid="stButton"] > button p {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
    line-height: 1.32 !important;
}

/* ==========================================================
   POLISHED CHAT MESSAGES
   ========================================================== */

[data-testid="stChatMessage"] {
    margin: 0.55rem 0 !important;
    padding: 0 !important;
    background: transparent !important;
}

[data-testid="stChatMessageContent"] {
    padding: 0.78rem 1rem !important;
    border-radius: 17px !important;
    line-height: 1.65 !important;
    color: #2c3b31 !important;
}

/* User bubble */
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #eef7e9 !important;
    border: 1px solid #d8e9d1 !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    border: 1px solid #dce8d6 !important;
    box-shadow: 0 3px 12px rgba(45, 83, 52, 0.055) !important;
}

/* Keep avatars clean and crop/person specific. */
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
    border-radius: 12px !important;
    border: 1px solid #d8e7d3 !important;
    background: #edf7e9 !important;
}

/* ==========================================================
   STREAMING CURSOR
   ========================================================== */

.streaming-cursor {
    display: inline-block;
    margin-left: 2px;
    opacity: 0.8;
}

/* ==========================================================
   RESPONSIVE
   ========================================================== */

@media (max-width: 768px) {
    .example-questions-card div[data-testid="stButton"] > button {
        min-height: 40px !important;
        font-size: 0.79rem !important;
        padding: 0.34rem 0.06rem !important;
    }

    [data-testid="stChatMessageContent"] {
        padding: 0.7rem 0.82rem !important;
    }
}


/* ========================================================
   FINAL LAYOUT REFINEMENTS
   ======================================================== */

.left-scheme-card {
    margin-bottom: 0.8rem !important;
}

.chat-shell {
    display: none !important;
}

.right-card {
    margin-bottom: 0.8rem;
}

.top-bar {
    justify-content: flex-end !important;
    text-align: right !important;
}


/* ========================================================
   FINAL CHAT SPACING
   ======================================================== */

[data-testid="stChatMessage"] {
    margin-top: 0.25rem !important;
    margin-bottom: 0.4rem !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

[data-testid="stChatMessageContent"] {
    min-width: 0 !important;
}

[data-testid="stChatMessageContent"] p:first-child {
    margin-top: 0 !important;
}

[data-testid="stChatMessageContent"] p:last-child {
    margin-bottom: 0 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">🌾</div>
            <div class="sidebar-brand-name">
                Agri Assist AI
            </div>
            <div class="sidebar-brand-tagline">
                Support for a stronger tomorrow
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("👨‍🌾 Your profile")

    role = st.selectbox(
        "I am a",
        [
            "farmer",
            "public",
            "government",
            "agency",
        ],
        key="role_selector",
        format_func=lambda value: ROLE_LABELS.get(
            value,
            value.title(),
        ),
        on_change=reset_for_role_change,
    )

    st.markdown("### 🌾 Find a scheme")

    selected_scheme = st.selectbox(
        "Select a scheme",
        list(SCHEME_OPTIONS.keys()),
        index=list(
            SCHEME_OPTIONS.keys()
        ).index(
            st.session_state.selected_scheme
        ),
        key="scheme_selector",
        on_change=reset_for_scheme_change,
    )

    selected_scheme_id = SCHEME_OPTIONS[
        selected_scheme
    ]

    st.session_state.selected_scheme = selected_scheme

    if selected_scheme_id:
        st.caption(
            f"Searching within: {selected_scheme}"
        )
    else:
        st.caption(
            "Searching across all available schemes"
        )

    if SIDEBAR_URI:
        st.markdown(
            f"""
            <div class="sidebar-card">
                <img
                    src="{SIDEBAR_URI}"
                    alt="Empowering farmers and strengthening communities"
                >
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="sidebar-text-card">
                <div class="sidebar-info-title">
                    🌱 Empowering Farmers
                </div>
                <div class="sidebar-info-text">
                    Strengthening communities through
                    accessible agriculture support.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# MAIN LAYOUT
# =========================================================

left_col, right_col = st.columns(
    [3.25, 1.0],
    gap="large",
)


# =========================================================
# LEFT / MAIN COLUMN
# =========================================================

with left_col:

    st.markdown(
        """
        <div class="top-bar">
            <span>For Farmers. For a Greener Tomorrow. 🌿</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Hero
    # -----------------------------------------------------

    if HERO_URI:

        st.markdown(
            f"""
            <div class="hero-image-wrap">
                <img
                    src="{HERO_URI}"
                    alt="Agri Assist AI agriculture hero"
                >
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="hero-image-wrap"
                 style="
                    min-height:220px;
                    display:flex;
                    align-items:center;
                    padding:2rem;
                    color:white;
                 ">
                <div>
                    <div style="
                        font-size:2.4rem;
                        font-weight:800;
                    ">
                        🌾 Agri Assist AI
                    </div>
                    <div style="
                        margin-top:0.55rem;
                        font-size:1rem;
                        max-width:700px;
                    ">
                        Your simple AI assistant for agriculture
                        government schemes and farmer support.
                        Ask your question in everyday language.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------
    # Selected scheme card
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div class="right-card left-scheme-card">
            <div class="scheme-badge">
                🌾 {selected_scheme}
            </div>
            <div class="right-body">
                {(
                    "All agriculture schemes are available for "
                    "your question."
                    if not selected_scheme_id
                    else
                    f"You are exploring {selected_scheme}. "
                    "Questions and tips are tailored to this scheme."
                )}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="height:0.25rem;"></div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Existing conversation
    #
    # Render previous messages first and completely. The new
    # response is handled only in the processing section below.
    # This prevents a previous answer from appearing inside the
    # next response's loading/typing area.

    for message in st.session_state.messages:

        message_role = message.get(
            "role",
            "assistant",
        )

        content = message.get(
            "content",
            "",
        )

        if message_role == "assistant":

            left_spacer, assistant_col = st.columns(
                [0.18, 0.82],
                gap="small",
            )

            with assistant_col:

                with st.chat_message(
                    "assistant",
                    avatar="🌾",
                ):
                    st.markdown(content)

        else:

            user_col, right_spacer = st.columns(
                [0.82, 0.18],
                gap="small",
            )

            with user_col:

                with st.chat_message(
                    "user",
                    avatar="👨‍🌾",
                ):
                    st.markdown(content)


# =========================================================
# RIGHT COLUMN
# =========================================================

with right_col:

    scheme_content = SCHEME_CONTENT.get(
        selected_scheme_id,
        SCHEME_CONTENT[None],
    )

    # -----------------------------------------------------
    # Tip of the day
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div class="right-card tip">
            <div class="right-title">
                💡 Tip of the day
            </div>
            <div class="right-body">
                {scheme_content["tip"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # What can I ask?
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="right-card">
            <div class="right-title">
                🌱 What can I ask?
            </div>
            <div class="right-body">
                Ask about eligibility, financial benefits,
                subsidies, crop insurance, irrigation,
                agricultural credit and other farmer support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Example questions
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="right-card example-questions-card">
            <div class="right-title">
                💬 Example questions
            </div>
        """,
        unsafe_allow_html=True,
    )

    for index, example in enumerate(
        scheme_content["questions"]
    ):

        button_key = (
            f"example_question_"
            f"{selected_scheme_id or 'all'}_"
            f"{index}"
        )

        if st.button(
            example,
            key=button_key,
            use_container_width=True,
        ):
            st.session_state.pending_query = example
            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Sustainable agriculture image
    # -----------------------------------------------------

    if SUSTAINABLE_URI:

        st.markdown(
            f"""
            <div class="sustainable-wrap">
                <img
                    src="{SUSTAINABLE_URI}"
                    alt="Together for sustainable agriculture"
                >
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# CHAT INPUT
# =========================================================

pending_query = st.session_state.pending_query

if pending_query:
    st.session_state.pending_query = None

typed_query = st.chat_input(
    "Ask your agriculture question..."
)

user_query = typed_query or pending_query


# =========================================================
# PROCESS QUERY
# =========================================================

if user_query:

    # -----------------------------------------------------
    # INPUT GUARDRAIL
    # -----------------------------------------------------

    is_valid, guardrail_message = validate_input(
        user_query
    )

    if not is_valid:

        # Show the user's blocked question
        user_col, right_spacer = st.columns(
            [0.82, 0.18],
            gap="small",
        )

        with user_col:
            with st.chat_message(
                "user",
                avatar="👨‍🌾",
            ):
                st.markdown(user_query)

        # Show guardrail response
        left_spacer, assistant_col = st.columns(
            [0.18, 0.82],
            gap="small",
        )

        with assistant_col:
            with st.chat_message(
                "assistant",
                avatar="🌾",
            ):
                st.markdown(guardrail_message)

        # Save both messages
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_query,
            }
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": guardrail_message,
            }
        )

        # Do NOT send blocked input to RAG
        st.session_state.pending_query = None

        st.stop()


    # -----------------------------------------------------
    # Save valid user message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    # -----------------------------------------------------
    # User question: LEFT
    # -----------------------------------------------------

    user_col, right_spacer = st.columns(
        [0.82, 0.18],
        gap="small",
    )

    with user_col:

        with st.chat_message(
            "user",
            avatar="👨‍🌾",
        ):
            st.markdown(user_query)

    # -----------------------------------------------------
    # Assistant response: RIGHT
    #
    # Only the current response exists in this slot.
    # -----------------------------------------------------

    left_spacer, assistant_col = st.columns(
        [0.18, 0.82],
        gap="small",
    )

    with assistant_col:

        with st.chat_message(
            "assistant",
            avatar="🌾",
        ):

            loading_slot = st.empty()

            loading_slot.markdown(
                """
                <div style="
                    display:flex;
                    align-items:center;
                    gap:8px;
                    color:#617066;
                    padding:8px 0;
                ">
                    <span style="font-size:1rem;">🌱</span>
                    <span>Finding the right information...</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            try:

                trace = run_rag_pipeline(
                    query=user_query,
                    role=role,
                    conversation_id=(
                        st.session_state.conversation_id
                    ),
                    scheme_id=selected_scheme_id,
                )

                answer = trace.get(
                    "answer",
                    (
                        "I could not generate a reliable "
                        "answer right now."
                    ),
                )

            except Exception as error:

                answer = (
                    "I ran into a problem while finding "
                    "that information. Please try again."
                )

                print(
                    f"Agri Assist pipeline error: {error}"
                )

            # -------------------------------------------------
            # Remove loading state before starting the answer.
            # -------------------------------------------------

            loading_slot.empty()

            # -------------------------------------------------
            # Visible character-by-character streaming.
            # -------------------------------------------------

            answer_placeholder = st.empty()

            stream_answer_text(
                answer_placeholder,
                answer,
                delay=0.018,
                chunk_size=2,
            )

    # -----------------------------------------------------
    # Save the final assistant answer only after streaming.
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
