"""Safe HTML rendering for Streamlit (avoids markdown code-block escaping)."""

from __future__ import annotations

import re
import textwrap
from typing import Any

import streamlit as st


def compact_html(html: str) -> str:
    """Collapse multiline HTML to one line so Streamlit markdown does not treat it as code."""
    dedented = textwrap.dedent(html).strip()
    # Collapse whitespace between tags; keep content spacing inside tags minimal
    return re.sub(r"\s+", " ", dedented)


def emit_html(html: str, *, context: Any = None) -> None:
    """
    Render HTML in Streamlit without showing raw tags as text.

    Prefers st.html when available; falls back to compact single-line markdown.
    """
    ctx = context or st
    cleaned = compact_html(html)
    if hasattr(ctx, "html"):
        ctx.html(cleaned)
    else:
        ctx.markdown(cleaned, unsafe_allow_html=True)
