import os

from dotenv import load_dotenv

import google.generativeai as genai

from rag.retriever import search_documents


load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def ask_question(question):

    results = search_documents(question)

    context = ""

    sources = []

    for item in results:

        context += item["content"] + "\n\n"

        sources.append(
            item["source"]
        )

    prompt = f"""
You are a Data Engineering Assistant.

Answer the user's question only using the provided context.

Context:
{context}

Question:
{question}
"""

    response = model.generate_content(
        prompt
    )

    unique_sources = list(
        set(sources)
    )

    source_text = "\n\nSources:\n"

    for source in unique_sources:

        source_text += f"- {source}\n"

    final_answer = (
        response.text +
        source_text
    )

    return final_answer