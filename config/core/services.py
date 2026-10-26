import requests
import re
import logging
from .config import Config

logger = logging.getLogger(__name__)


def call_groq(messages, temperature=0.1):
    try:
        payload = {
            "model": Config.GROQ_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }
        # gpt-oss models are reasoning models, so keep their thinking short
        if "gpt-oss" in Config.GROQ_MODEL:
            payload["reasoning_effort"] = "low"

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return content or "Error: Empty AI response"

    except requests.HTTPError as e:
        logger.error(f"Groq API Failure: {e} | {e.response.text[:300]}")
        return "Error: AI Service Unavailable"
    except Exception as e:
        logger.error(f"Groq API Failure: {str(e)}")
        return "Error: AI Service Unavailable"


def get_sql_from_llm(user_question):
    logger.info(f"Generating SQL using {Config.GROQ_MODEL}")

    messages = [
        {"role": "system", "content": Config.PROMPT_SQL_SCHEMA},
        {"role": "user", "content": user_question}
    ]

    generated_text = call_groq(messages, temperature=0.1)

    if generated_text.startswith("Error"):
        return generated_text

    sql_query = clean_sql(generated_text)

    if not is_safe_sql(sql_query):
        logger.warning(f"Blocked unsafe SQL: {sql_query}")
        return "ERROR: Unsafe query detected."

    return sql_query


def summarize_results(question, results, columns):
    try:
        data_preview = [dict(zip(columns, row)) for row in results[:5]]

        messages = [
            {"role": "system", "content": Config.PROMPT_SUMMARY_TEMPLATE},
            {
                "role": "user",
                "content": f"Data:\n{data_preview}\n\nQuestion:\n{question}"
            }
        ]

        return call_groq(messages, temperature=0.3)

    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return "Error generating summary."


def clean_sql(text):
    text = re.sub(r'```sql', '', text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()
    return text


def is_safe_sql(sql):
    forbidden = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'GRANT']
    upper_sql = sql.upper()

    for word in forbidden:
        if re.search(r'\b' + word + r'\b', upper_sql):
            return False

    return True