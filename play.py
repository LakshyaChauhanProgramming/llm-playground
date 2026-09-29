"""
llm-playground Day 1  —  provider: OpenRouter

Goal: ek prompt bhejo, aur wapas milo: answer + tokens + cost + finish_reason.

Ye skeleton hai. Helpers already implemented hain (PRICES table, arg parsing,
output formatting). Tumhe do functions implement karne hain neeche TODO
marked hain. Wahi pattern hai jo interview coding round mein aata hai.

Provider note: OpenRouter ek router hai — ek hi API key se Anthropic, OpenAI,
Google, Meta sab ke models. Uska API **OpenAI Chat Completions shape** follow
karta hai (provider chahe koi bhi ho, response ka shape same rehta hai).
Isliye SDK `openai` hai, `anthropic` nahi — sirf base_url badalta hai.
"""

import os
import sys
import time
from typing import NamedTuple, Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------- given ----

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# $ per 1,000,000 tokens -> (input_rate, output_rate)
# OpenRouter model IDs: "<provider>/<model>" — aur dots use hote hain,
# dashes nahi ("claude-haiku-4.5", NOT "claude-haiku-4-5"). Ye ek classic
# 404 ka source hai.
PRICES = {
    "anthropic/claude-opus-5":    (5.00, 25.00),
    "anthropic/claude-sonnet-5":  (2.00, 10.00),
    "anthropic/claude-haiku-4.5": (1.00,  5.00),
}

DEFAULT_MODEL = "anthropic/claude-sonnet-5"


class Result(NamedTuple):
    text: str
    input_tokens: int
    output_tokens: int
    finish_reason: str
    latency_s: float
    reported_cost: Optional[float]  # OpenRouter khud bhi cost batata hai


def render(model: str, r: Result, cost: float) -> None:
    """Result ko terminal pe print karta hai. Modify mat karna."""
    print(f"\n{r.text}\n")
    print("-" * 56)
    print(f"{'model':<18} {model}")
    print(f"{'input tokens':<18} {r.input_tokens:,}")
    print(f"{'output tokens':<18} {r.output_tokens:,}")
    print(f"{'finish_reason':<18} {r.finish_reason}")
    print(f"{'latency':<18} {r.latency_s:.2f}s")
    print(f"{'cost (mera calc)':<18} ${cost:.6f}")
    if r.reported_cost is not None:
        delta = cost - r.reported_cost
        print(f"{'cost (OpenRouter)':<18} ${r.reported_cost:.6f}")
        print(f"{'difference':<18} ${delta:+.6f}")
    print("-" * 56)


# ----------------------------------------------------------- implement ----

def call_model(client: OpenAI, model: str, prompt: str,
               max_tokens: int = 1024) -> Result:
    """
    OpenRouter API ko call karta hai aur saare details ko parse karke
    safely Result NamedTuple me return karta hai.
    """
    # 1. Latency measure karne ke liye high-precision timer call se pehle start kiya
    start_time = time.perf_counter()
    
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Call ke turant baad timer stop kiya taaki exact API latency mile
    latency_s = time.perf_counter() - start_time

    # 2. Choices list aur content ka safety check (IndexError / AttributeError se bachne ke liye)
    text = ""
    finish_reason = "unknown"
    if response.choices:
        choice = response.choices[0]
        # Agar content None hai (jaise tool call ke case me), toh empty string return karenge
        if choice.message and choice.message.content is not None:
            text = choice.message.content.strip()
        
        if choice.finish_reason is not None:
            finish_reason = choice.finish_reason

    # 3. Tokens parsing (Safely fallback to 0 agar usage field missing ho)
    input_tokens = 0
    output_tokens = 0
    if response.usage:
        input_tokens = getattr(response.usage, "prompt_tokens", 0)
        output_tokens = getattr(response.usage, "completion_tokens", 0)

    # 4. OpenRouter reported cost ko safely nikalna (Kyuki ye standard OpenAI spec ka part nahi hai)
    reported_cost = None
    if response.usage:
        reported_cost = getattr(response.usage, "cost", None)

    return Result(
        text=text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        finish_reason=finish_reason,
        latency_s=latency_s,
        reported_cost=reported_cost
    )


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Dono input aur output tokens ke rates ko PRICES table se nikal kar 
    total cost calculation karta hai.
    """
    # Edge case handle: Agar koi naya model pass ho jaye jo hamari local dictionary me nahi hai
    if model not in PRICES:
        # Silently 0.0 bhejna production me dangerous ho sakta hai (billing miss hogi).
        # Ek behtareen approach ye hai ki hum default model ka rate fallback bana lein ya log karein.
        # Interiew ke hisaab se hum DEFAULT_MODEL ka rate use kar rahe hain taaki calculation band na ho.
        raise KeyError(f"{model} PRICES me nahi hai — rate add karo")
    else:
        rates = PRICES[model]

    input_rate, output_rate = rates

    # Rates 1M tokens ke liye hain, isliye individual token cost nikalne ke liye 1,000,000 se divide kiya
    input_cost = (input_tokens * input_rate) / 1_000_000
    output_cost = (output_tokens * output_rate) / 1_000_000

    return input_cost + output_cost


# ---------------------------------------------------------------- main ----

def main() -> int:
    if len(sys.argv) < 2:
        print('usage: python play.py "your prompt here" [model]')
        print(f'models: {", ".join(PRICES)}')
        return 1

    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY set nahi hai. .env banao (.env.example dekho).")
        return 1

    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)

    result = call_model(client, model, prompt)
    cost = estimate_cost(model, result.input_tokens, result.output_tokens)
    render(model, result, cost)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
