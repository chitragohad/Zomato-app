"""DineAI design tokens (from stitch_dineai_restaurant_recommender/DESIGN.md)."""

from __future__ import annotations

# Core palette — high contrast on light surfaces (WCAG AA)
PRIMARY = "#b7122a"
PRIMARY_CONTAINER = "#db313f"
PRIMARY_FIXED = "#ffdad8"
ON_PRIMARY = "#ffffff"
SURFACE = "#f9f9f9"
SURFACE_CONTAINER_LOW = "#f3f3f3"
SURFACE_CONTAINER = "#eeeeee"
SURFACE_CONTAINER_LOWEST = "#ffffff"
ON_SURFACE = "#1a1c1c"
ON_SURFACE_VARIANT = "#5b403f"
ON_SECONDARY_FIXED_VARIANT = "#45455b"
# Muted but WCAG AA on #eeeeee / #f3f3f3 (≥4.5:1)
ON_SURFACE_MUTED = "#45455b"
# Placeholder / hint text on white (≥4.5:1)
ON_SURFACE_PLACEHOLDER = "#5b403f"
OUTLINE_VARIANT = "#e4bebc"
SECONDARY_CONTAINER = "#e2e0fc"
TERTIARY_GOLD = "#e9c400"
STAR_GOLD = "#e9c400"

FONT_LINK = (
    "https://fonts.googleapis.com/css2?"
    "family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&"
    "family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
)

# Curated food imagery (Stitch mock) — fallback by rank
CARD_IMAGES = [
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=640&h=480&fit=crop",
    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=640&h=480&fit=crop",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=640&h=480&fit=crop",
    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=640&h=480&fit=crop",
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=640&h=480&fit=crop",
]

DINEAI_CSS = f"""
@import url('{FONT_LINK}');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* App shell — single scroll in main area */
.stApp {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
    overflow: hidden !important;
    height: 100vh !important;
}}

.stApp [data-testid="stAppViewContainer"] {{
    overflow: hidden !important;
    height: 100vh !important;
}}

.stApp [data-testid="stAppViewContainer"] > section.main {{
    overflow-y: auto !important;
    height: 100vh !important;
}}

header[data-testid="stHeader"] {{
    background: transparent;
}}

.block-container {{
    padding-top: 0.5rem;
    padding-bottom: 2rem;
    max-width: 100%;
}}

/* Sidebar — DineAI panel (fixed; no independent scroll) */
section[data-testid="stSidebar"] {{
    background-color: {SURFACE_CONTAINER_LOW} !important;
    border-right: 1px solid {OUTLINE_VARIANT};
    width: 350px !important;
    min-width: 350px !important;
    color-scheme: light;
    color: {ON_SURFACE};
    overflow: hidden !important;
    height: 100vh !important;
}}

section[data-testid="stSidebar"] > div {{
    background-color: {SURFACE_CONTAINER_LOW};
    overflow: hidden !important;
    height: 100% !important;
}}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {{
    color: {ON_SURFACE_MUTED} !important;
}}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stTextArea label {{
    color: {ON_SURFACE} !important;
}}

section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {ON_SURFACE_VARIANT} !important;
}}

/* Captions & secondary sidebar text */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
section[data-testid="stSidebar"] .stCaption {{
    color: {ON_SURFACE_MUTED} !important;
}}

section[data-testid="stSidebar"] .stSelectbox > div > div {{
    position: relative !important;
}}

section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextArea textarea {{
    background: {SURFACE_CONTAINER_LOWEST} !important;
    border: 1px solid {OUTLINE_VARIANT} !important;
    border-radius: 8px !important;
    color: {ON_SURFACE} !important;
}}

section[data-testid="stSidebar"] .stTextArea textarea::placeholder {{
    color: {ON_SURFACE_PLACEHOLDER} !important;
    opacity: 1 !important;
}}

section[data-testid="stSidebar"] .stSelectbox {{
    margin-bottom: 0.25rem !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] {{
    width: 100% !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background: {SURFACE_CONTAINER_LOWEST} !important;
    border-color: {OUTLINE_VARIANT} !important;
    border-radius: 8px !important;
    min-height: 2.5rem !important;
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.75rem !important;
    padding-right: 2.75rem !important;
    align-items: center !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div > div:first-child {{
    flex: 1 1 auto !important;
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div > div:last-child {{
    position: absolute !important;
    right: 0.75rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 1.25rem !important;
    height: 1.25rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
    width: 1.25rem !important;
    height: 1.25rem !important;
    flex-shrink: 0 !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-baseweb="select"] div[value] {{
    color: {ON_SURFACE} !important;
}}

/* Segmented controls (Budget, Min Rating) — readable labels */
section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] button,
section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] label,
section[data-testid="stSidebar"] .stButtonGroup button,
section[data-testid="stSidebar"] .stButtonGroup [data-testid="stMarkdownContainer"] p {{
    color: {ON_SURFACE} !important;
    font-weight: 500 !important;
}}

section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] button[aria-pressed="true"],
section[data-testid="stSidebar"] .stButtonGroup button[aria-pressed="true"],
section[data-testid="stSidebar"] .stButtonGroup button[kind="primary"] {{
    background: {PRIMARY} !important;
    color: {ON_PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}

section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] button[aria-pressed="true"] p,
section[data-testid="stSidebar"] .stButtonGroup button[aria-pressed="true"] p {{
    color: {ON_PRIMARY} !important;
}}

section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] button[aria-pressed="false"],
section[data-testid="stSidebar"] .stButtonGroup button[aria-pressed="false"] {{
    background: {SURFACE_CONTAINER_LOWEST} !important;
    color: {ON_SURFACE} !important;
    border: 1px solid {OUTLINE_VARIANT} !important;
}}

/* Radio fallback — unselected must stay dark on grey track */
section[data-testid="stSidebar"] .stRadio > div,
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {{
    background: {SURFACE_CONTAINER} !important;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}}

section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    background: transparent !important;
    color: {ON_SURFACE} !important;
    font-weight: 500 !important;
    border-radius: 6px;
    padding: 6px 12px;
}}

/* Force label text nodes (Streamlit nests text in p/span/div) */
section[data-testid="stSidebar"] .stRadio label p,
section[data-testid="stSidebar"] .stRadio label span,
section[data-testid="stSidebar"] .stRadio label div,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div,
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {{
    color: {ON_SURFACE} !important;
    opacity: 1 !important;
}}

section[data-testid="stSidebar"] .stRadio label:has(input:checked),
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked),
section[data-testid="stSidebar"] .stRadio label[data-checked="true"] {{
    background: {PRIMARY} !important;
    color: {ON_PRIMARY} !important;
}}

section[data-testid="stSidebar"] .stRadio label:has(input:checked) p,
section[data-testid="stSidebar"] .stRadio label:has(input:checked) span,
section[data-testid="stSidebar"] .stRadio label:has(input:checked) div,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) p,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) span,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) div,
section[data-testid="stSidebar"] .stRadio label:has(input:checked) [data-testid="stMarkdownContainer"] p {{
    color: {ON_PRIMARY} !important;
    opacity: 1 !important;
}}

/* Unselected radio options — override Streamlit theme grey text */
section[data-testid="stSidebar"] .stRadio label:not(:has(input:checked)),
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:not(:has(input:checked)) {{
    color: {ON_SURFACE} !important;
}}

section[data-testid="stSidebar"] .stRadio label:not(:has(input:checked)) *:not(svg):not(path):not(circle):not(rect),
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:not(:has(input:checked)) *:not(svg):not(path):not(circle):not(rect) {{
    color: {ON_SURFACE} !important;
    opacity: 1 !important;
    -webkit-text-fill-color: {ON_SURFACE} !important;
}}

/* Checkbox */
section[data-testid="stSidebar"] .stCheckbox label,
section[data-testid="stSidebar"] .stCheckbox label p,
section[data-testid="stSidebar"] .stCheckbox [data-testid="stWidgetLabel"] p {{
    color: {ON_SURFACE_VARIANT} !important;
}}

section[data-testid="stSidebar"] .stCheckbox label span {{
    color: {ON_SURFACE} !important;
}}

/* Slider — value, track, thumb */
section[data-testid="stSidebar"] .stSlider label {{
    color: {ON_SURFACE_VARIANT} !important;
}}

section[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"],
section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
section[data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] + div {{
    color: {ON_SURFACE} !important;
}}

section[data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] > div > div:first-child {{
    background: #b8b8b8 !important;
}}

section[data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] [role="slider"] {{
    background: {ON_SURFACE_MUTED} !important;
    border: 2px solid {ON_SURFACE} !important;
}}

section[data-testid="stSidebar"] .stButton > button {{
    width: 100%;
    background: {PRIMARY} !important;
    color: {ON_PRIMARY} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    box-shadow: 0 1px 3px rgba(26, 26, 46, 0.12);
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {PRIMARY_CONTAINER} !important;
    color: {ON_PRIMARY} !important;
}}

section[data-testid="stSidebar"] .stButton > button:disabled {{
    opacity: 0.85;
    background: {PRIMARY_CONTAINER} !important;
    color: {ON_PRIMARY} !important;
}}

section[data-testid="stSidebar"] .stButton > button:not(:disabled) {{
    background: {PRIMARY} !important;
    color: {ON_PRIMARY} !important;
}}

/* Main area */
.main .block-container {{
    padding-left: 2rem;
    padding-right: 2rem;
}}

div[data-testid="stVerticalBlock"] > div:has(.dineai-results) {{
    gap: 1.5rem;
}}

/* Alerts — readable on light bg */
.stAlert {{
    border-radius: 12px;
}}
"""
