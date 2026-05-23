import streamlit as st
from utils.shared.styles import inject_css


def render_sidebar(tool_name: str = "") -> str | None:
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        api_key = None
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
            st.success("✅ API key loaded")
        except Exception:
            key = st.text_input(
                "Anthropic API Key", type="password",
                placeholder="sk-ant-...", key="sidebar_api_key",
            )
            if key:
                api_key = key
                st.success("✅ API key set")
            else:
                st.warning("Enter your API key to begin")

        st.divider()
        if tool_name:
            st.markdown(f"**🔧 Tool:** {tool_name}")
            st.divider()

        st.markdown("**🔐 Privacy**")
        st.markdown("- Processed in memory only")
        st.markdown("- Not stored or trained on")
        st.markdown("- Files auto-deleted after session")
        st.divider()
        st.caption(
            "⚠️ This platform assists with legal work. "
            "It does not replace qualified legal advice."
        )

    return api_key


def setup_page(section: str = "") -> str | None:
    """
    One-call page initialiser for all new p_*.py pages.
    Injects CSS and renders the shared sidebar.
    Returns the api_key (or None if not provided).
    """
    inject_css()
    return render_sidebar(section)
