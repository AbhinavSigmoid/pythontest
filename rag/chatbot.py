import os

from dotenv import load_dotenv
import google.generativeai as genai

from rag.retriever import search_documents


def ask_question(question, active_pdf=None):

    load_dotenv(override=True)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "GEMINI_API_KEY not found in .env"

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    results = search_documents(
        question,
        source_file=active_pdf
    )

    context = ""
    sources = []

    for item in results:

        context += item["content"] + "\n\n"
        sources.append(item["source"])

    if not context.strip():
        return "No relevant information found in the uploaded document."

    prompt = f"""
You are a Senior Data Engineering Assistant.

Use ONLY the provided context.

Provide clear, professional answers.

If available, include:
- Direct answer
- Relevant details
- Business impact
- Related pipeline information

If the answer is not present in the context, say:
'I could not find that information in the uploaded document.'

Context:
{context}

Question:
{question}
"""

    try:

        response = model.generate_content(
            prompt
        )

        source_text = "\n\nSources:\n"

        for source in set(sources):

            source_text += (
                f"- {os.path.basename(source)}\n"
            )

        return (
            response.text +
            source_text
        )

    except Exception as e:

        return (
            f"Gemini Error: {str(e)}"
        )