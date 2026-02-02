import os

from crewai import LLM


def use_openai_from_env() -> bool:
    """
    Returns True if USE_OPENAI=true (case-insensitive).
    Default is False (Anthropic).
    """
    return os.getenv("USE_OPENAI", "false").lower() == "true"


def make_llm_from_env() -> LLM:
    """
    Create a CrewAI LLM from environment variables.

    - Anthropic (default):
      - ANTHROPIC_API_KEY (required)
      - ANTHROPIC_BASE_URL (optional, default https://api.anthropic.com)
      - ANTHROPIC_MODEL (optional, default claude-3-5-sonnet-latest)

    - OpenAI (when USE_OPENAI=true):
      - OPENAI_API_KEY (required)
      - OPENAI_MODEL (optional, default gpt-4o-mini)
    """
    if use_openai_from_env():
        api_key = os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file")
        print(f"\n🤖 [LLM] provider=openai model={model} key_loaded=True\n")
        return LLM(model=f"openai/{model}", api_key=api_key)

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found. Please set it in your .env file")
    print(f"\n🤖 [LLM] provider=anthropic model={model} key_loaded=True\n")
    return LLM(model=f"anthropic/{model}", api_key=api_key, base_url=base_url)


