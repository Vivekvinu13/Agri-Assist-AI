import os
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    "gpt-4o-mini",
)


def get_llm():
    """Create the LLM used for query classification."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY was not found. "
            "Check your .env file."
        )

    return ChatOpenAI(
        model=MODEL,
        temperature=0,
        api_key=api_key,
    )


def classify_query(query: str):
    """
    Classify a user query before RAG retrieval.

    Returns:
    - domain
    - intent
    - confidence
    - should_retrieve
    - reason
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    prompt = f"""
You are the query classification component of Agri Assist AI.

Agri Assist AI is a RAG system focused on Indian
agricultural government schemes and related farmer
support information.

USER QUERY:
{query}

Classify the query using the following rules.

DOMAIN OPTIONS:

1. agriculture
   Use this for questions about:
   - Indian agricultural government schemes
   - farmer benefits
   - eligibility
   - subsidies
   - crop insurance
   - irrigation
   - agricultural credit
   - agricultural machinery
   - farmer pensions
   - agricultural assistance

2. general
   Use this for general questions that are not specifically
   about agricultural government schemes or farmer support.

3. weather
   Use this for weather forecasts or current weather
   questions.

4. other
   Use this for questions that do not fit the above categories.

INTENT OPTIONS:

- scheme_information
- eligibility
- benefits
- application
- subsidy_or_financial_assistance
- insurance
- credit
- irrigation
- pension
- weather_forecast
- general_information
- other

IMPORTANT:

- Do not answer the user's question.
- Do not invent information.
- Preserve the user's actual intent.
- A question about weather-related crop insurance is
  agriculture if it is asking about an agricultural
  insurance scheme.
- A request for an actual weather forecast is weather.
- Only agriculture queries should normally be sent to
  the agricultural RAG retrieval pipeline.
- Weather, general, and other queries should not be sent
  to the agricultural vector store.

Return ONLY valid JSON:

{{
    "domain": "agriculture",
    "intent": "scheme_information",
    "confidence": 0.0,
    "should_retrieve": true,
    "reason": "short explanation"
}}

Confidence must be between 0 and 1.

Set should_retrieve to true only when domain is
agriculture.

For weather, general, and other domains,
should_retrieve must be false.
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    content = response.content.strip()

    # Handle accidental markdown code fences.
    if content.startswith("```"):
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "domain": "other",
            "intent": "other",
            "confidence": 0.0,
            "should_retrieve": False,
            "reason": "Classifier returned invalid JSON.",
        }

    # Safety normalization.
    domain = result.get("domain", "other")

    if domain not in {
        "agriculture",
        "general",
        "weather",
        "other",
    }:
        domain = "other"

    should_retrieve = domain == "agriculture"

    return {
        "domain": domain,
        "intent": result.get("intent", "other"),
        "confidence": float(
            result.get("confidence", 0.0)
        ),
        "should_retrieve": should_retrieve,
        "reason": result.get(
            "reason",
            "No reason provided.",
        ),
    }