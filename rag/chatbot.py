import os

from dotenv import load_dotenv
import google.generativeai as genai

from rag.retriever import search_documents


def get_gemini_key():

    try:
        import streamlit as st
        return (
            os.getenv("GEMINI_API_KEY")
            or st.secrets.get("GEMINI_API_KEY")
        )
    except Exception:
        return os.getenv(
            "GEMINI_API_KEY"
        )


def ask_question(
    question,
    active_pdf=None
):

    load_dotenv(override=True)

    api_key = get_gemini_key()

    if not api_key:

        return (
            "Gemini API key is not configured. "
            "Check Streamlit Secrets."
        )

    print("GEMINI FOUND:", bool(api_key))
    genai.configure(
        api_key=api_key
    )

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    results = search_documents(
        question,
        source_file=active_pdf
    )

    context = ""
    sources = []
    fallback_used = False

    for item in results:

        context += (
            item["content"]
            + "\n\n"
        )

        sources.append(
            item["source"]
        )

    # Fallback to search all documents if no results found in the active PDF
    if not context.strip() and active_pdf:
        fallback_results = search_documents(
            question,
            source_file=None
        )
        for item in fallback_results:
            context += (
                item["content"]
                + "\n\n"
            )
            sources.append(
                item["source"]
            )
        if context.strip():
            fallback_used = True

    if not context.strip():

        return (
            "No relevant information found "
            "in the uploaded document."
        )

    prompt = f"""
You are a Senior Data Engineering Assistant.

Instructions:
1. Answer the question using ONLY the provided context. Do not make up information or use outside knowledge.
2. If the user asks for the SLA, look for parameters like SLA, Availability Target, Availability SLA, or Maximum Delay in the context, and report them.
3. Be professional and direct.
4. If the answer is not present in the context, respond with exactly: 'I could not find that information in the uploaded document.'

Context:
{context}

Question:
{question}
"""

    try:

        response = model.generate_content(
            prompt
        )

        source_text = (
            "\n\nSources:\n"
        )

        for source in set(sources):

            source_text += (
                f"- {os.path.basename(source)}\n"
            )

        if fallback_used:
            source_text += "\n*(Note: This information was not found in the active document, but was retrieved from the sources listed above.)*"

        return (
            response.text
            + source_text
        )

    except Exception as e:

        return (
            f"Gemini Error: {str(e)}"
        )