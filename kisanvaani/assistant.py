"""Question translation, source retrieval, and grounded answer generation."""

from typing import Dict, List

from groq import Groq

from kisanvaani.language import detect_language, language_name
from kisanvaani.rag import retrieve_documents


FALLBACKS = {
    "en": (
        "I could not find enough support for that question in my current agricultural "
        "knowledge base. I do not want to guess. Please try a more specific question "
        "or contact your local Krishi Vigyan Kendra (KVK) or agriculture department."
    ),
    "hi": (
        "मौजूदा कृषि जानकारी में इस प्रश्न के लिए पर्याप्त प्रमाण नहीं मिला। मैं अनुमान "
        "नहीं लगाना चाहता। कृपया प्रश्न को अधिक स्पष्ट करें या अपने स्थानीय कृषि विज्ञान "
        "केंद्र (KVK) अथवा कृषि विभाग से संपर्क करें।"
    ),
    "ta": (
        "தற்போதைய வேளாண் அறிவுத் தொகுப்பில் இந்தக் கேள்விக்கு போதுமான ஆதாரம் இல்லை. "
        "ஊகித்து பதிலளிக்க விரும்பவில்லை. கேள்வியை மேலும் தெளிவாகக் கேளுங்கள் அல்லது "
        "அருகிலுள்ள வேளாண் அறிவியல் மையம் (KVK) / வேளாண் துறையை அணுகுங்கள்."
    ),
}


def _chat(client: Groq, model: str, messages: List[Dict], temperature: float = 0.1) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    content = response.choices[0].message.content
    return (content or "").strip()


def translate_query_to_english(question: str, language_code: str, client: Groq, model: str) -> str:
    """Translate a Hindi/Tamil question into a concise English search query."""
    if language_code == "en":
        return question.strip()

    translated = _chat(
        client,
        model,
        [
            {
                "role": "system",
                "content": (
                    "Translate the user's agricultural question into concise English for document search. "
                    "Preserve the crop, symptom, quantity and intent. Return only the English translation. "
                    "Do not answer the question or add facts."
                ),
            },
            {"role": "user", "content": question.strip()},
        ],
        temperature=0.0,
    )
    return translated or question.strip()


def generate_grounded_answer(
    question: str,
    search_query: str,
    documents: List[Dict],
    response_language: str,
    client: Groq,
    model: str,
) -> str:
    """Generate a concise answer and ask for source markers such as [S1]."""
    if not documents:
        return FALLBACKS.get(response_language, FALLBACKS["en"])

    context_blocks = []
    for index, document in enumerate(documents, start=1):
        context_blocks.append(
            f"[S{index}] {document['title']}\n"
            f"Guidance: {document['content']}\n"
            f"Source: {document['source_title']} — {document['source_url']}"
        )
    context = "\n\n".join(context_blocks)

    prompt = f"""
You are KisanVaani, a cautious agricultural information assistant for Indian farmers.
Answer in {language_name(response_language)}. Use simple, practical language and short paragraphs.

STRICT EVIDENCE RULES:
- Use only the supplied source context for factual agricultural guidance.
- Cite material claims with the matching source marker, such as [S1] or [S2]. Do not invent sources.
- If the sources do not support a useful answer, clearly say that the available sources are insufficient.
- Do not invent pesticide names, application rates, fertilizer dosages, crop-disease diagnoses, prices, or guaranteed yields.
- For crop-specific treatments, uncertain symptoms, or location-dependent recommendations, advise the user to consult a local agricultural officer or Krishi Vigyan Kendra (KVK).
- Do not claim that you inspected a farm, image, live weather or current market data.
- Keep the answer useful and concise, ideally under 180 words.

User's original question: {question}
English search interpretation: {search_query}

Retrieved source context:
{context}
""".strip()

    answer = _chat(
        client,
        model,
        [
            {"role": "system", "content": "You answer agricultural questions cautiously and cite the provided evidence."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return answer or FALLBACKS.get(response_language, FALLBACKS["en"])


def ask_kisanvaani(
    question: str,
    input_language: str,
    response_preference: str,
    client: Groq,
    model: str,
) -> Dict:
    """Full pipeline: detect language -> translate for retrieval -> RAG -> answer."""
    question = (question or "").strip()
    if not question:
        raise ValueError("Please enter or record a question first.")

    detected_language = detect_language(question, input_language)
    response_language = detected_language if response_preference == "same" else response_preference
    if response_language not in {"en", "hi", "ta"}:
        response_language = "en"

    english_query = translate_query_to_english(question, detected_language, client, model)
    retrieved = retrieve_documents(english_query, top_k=4)
    answer = generate_grounded_answer(
        question=question,
        search_query=english_query,
        documents=retrieved,
        response_language=response_language,
        client=client,
        model=model,
    )

    return {
        "question": question,
        "detected_language": detected_language,
        "response_language": response_language,
        "english_search_query": english_query,
        "answer": answer,
        "documents": retrieved,
        "has_sources": bool(retrieved),
    }
