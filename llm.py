import json

from openai import OpenAI

from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL, PERPLEXITY_MODEL
from schemas import SuggestItem

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_BASE_URL) if PERPLEXITY_API_KEY else None


def strip_markdown_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return text


def build_prompt(user_text: str) -> str:
    return f"""
You are a senior engineer assistant.
Given the user change description, generate exactly 9 items.

Rules:
- branch must be in format <type>/<kebab-case-name>
- type must be one of: feat|fix|chore|refactor|docs|test|perf|ci|build
- commit must be imperative and start with "<type>: "
- <type> in commit must match branch prefix

Return strictly valid JSON array:
[{{"branch":"type/name","commit":"type: message"}}, ...]
No markdown, no explanations.

User text:
{user_text}
""".strip()


def generate_suggestions(user_text: str) -> list[SuggestItem]:
    if not client:
        raise RuntimeError("PERPLEXITY_API_KEY is not configured")

    prompt = build_prompt(user_text)

    try:
        response = client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            max_tokens=512,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        raise ValueError(f"OpenAI request failed: {exc}") from exc

    raw = response.choices[0].message.content

    if not raw:
        raise ValueError("Empty response from model")
    if not isinstance(raw, str):
        raise ValueError("Unexpected response format from model")

    raw = strip_markdown_fences(raw)

    try:
        data = json.loads(raw)
    except Exception as exc:
        raise ValueError(f"Failed to parse model JSON: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("Model response is not a JSON array")
    if len(data) != 9:
        raise ValueError(f"Model returned {len(data)} items, expected 9")

    try:
        return [SuggestItem.model_validate(item) for item in data]
    except Exception as exc:
        raise ValueError(f"Invalid item shape in model JSON: {exc}") from exc
