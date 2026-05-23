import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature

setup_page()
slim_header("🔬", "Research", "Legal research, case summaries, statute explainers, and translation tools")

tab_research, tab_translation = st.tabs(["🔬 Research Tools", "🌍 Translation & Terminology"])

with tab_research:
    group_header("Research & Knowledge")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "🔬", "Legal Research Assistant",
            "Ask legal questions and receive structured research responses with authorities.",
            ["Ask any legal question in natural language", "Receive structured answer with citations",
             "Narrow results by jurisdiction and area of law", "Save research to matter"],
            ["Research summary with cited authorities", "Key principles list", "Research memo export"],
        )
    with c2:
        placeholder_feature(
            "📑", "Case Summary Generator",
            "Upload a judgment or case report and receive a structured summary.",
            ["Upload case PDF or paste text", "Receive structured case summary",
             "Extract key principles and ratio decidendi", "Save to knowledge base"],
            ["Case summary (parties, facts, held, ratio)", "Key principles", "Word/PDF export"],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        placeholder_feature(
            "📖", "Statute Explainer",
            "Paste a statute or regulation and receive a plain-English explanation with commentary.",
            ["Paste any statute, regulation, or ordinance", "Receive section-by-section plain-English summary",
             "Identify key obligations, prohibitions, and penalties"],
            ["Plain-English statute summary", "Key obligations list", "FAQ for common interpretations"],
        )
    with c4:
        placeholder_feature(
            "⚖️", "Authority Checker",
            "Verify whether a case or statute is still good law and check subsequent treatment.",
            ["Enter case citation or statute reference", "Check for overruling, distinguishing, or amendment",
             "See subsequent cases that have applied or distinguished"],
            ["Authority status report", "Subsequent treatment list", "Updated citation if overruled"],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "🗂️", "Knowledge Base Search",
        "Search across all AI outputs, summaries, and research saved from previous matters.",
        ["Search by keyword, matter, or document type", "Find past research, summaries, and memos",
         "Reuse existing work across matters", "Build the firm's institutional knowledge"],
        ["Matching results from past work", "Matter-linked research history",
         "Reusable summaries and memos"],
    )

with tab_translation:
    group_header("Legal Translation & Terminology")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "🌍", "Legal Translation",
            "Translate legal documents between languages while preserving legal terminology accuracy.",
            ["Upload document in source language", "Select target language",
             "AI translates with attention to legal meaning", "Review side-by-side (original vs. translated)"],
            ["Translated document (Word/PDF)", "Translator's notes on difficult terms",
             "Side-by-side bilingual view"],
        )
    with c2:
        placeholder_feature(
            "📝", "Bilingual Review",
            "Compare an original document with its translation to identify meaning discrepancies.",
            ["Upload both original and translated documents",
             "AI identifies meaning discrepancies and mistranslations",
             "Flag legally significant differences"],
            ["Discrepancy report", "Risk-flagged differences", "Suggested corrections"],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "🔤", "Legal Term Checker",
        "Verify the correct legal terminology for a given jurisdiction and area of law.",
        ["Enter a term or phrase to check", "Receive jurisdiction-specific correct terminology",
         "Compare how the same concept is expressed in different legal systems"],
        ["Term explanation and correct usage", "Jurisdiction comparison table",
         "Alternative terms list"],
    )
