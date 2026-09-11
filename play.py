"""
llm-playground — Day 1

Goal: ek prompt bhejo, aur wapas milo: answer + tokens + cost + stop_reason.

Ye skeleton hai. Helpers already implemented hain (PRICES table, arg parsing,
output formatting). Tumhe do functions implement karne hain — neeche TODO
marked hain. Wahi pattern hai jo interview coding round mein aata hai.
"""

import os
import sys
import time
from typing import NamedTuple

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------- given ----

# $ per 1,000,000 tokens -> (input_rate, output_rate)
PRICES = {
    "claude-opus-5":    (5.00, 25.00),
    "claude-sonnet-5":  (2.00, 10.00),
    "claude-haiku-4-5": (1.00,  5.00),
}

DEFAULT_MODEL = "claude-sonnet-5"


class Result(NamedTuple):
    text: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    latency_s: float


def render(model: str, r: Result, cost: float) -> None:
    """Result ko terminal pe print karta hai. Modify mat karna."""
    print(f"\n{r.text}\n")
    print("-" * 52)
    print(f"{'model':<16} {model}")
    print(f"{'input tokens':<16} {r.input_tokens:,}")
    print(f"{'output tokens':<16} {r.output_tokens:,}")
    print(f"{'stop_reason':<16} {r.stop_reason}")
    print(f"{'latency':<16} {r.latency_s:.2f}s")
    print(f"{'cost':<16} ${cost:.6f}")
    print("-" * 52)


# ----------------------------------------------------------- implement ----

def call_model(client: anthropic.Anthropic, model: str, prompt: str,
               max_tokens: int = 1024) -> Result:
    """
    TODO: Claude ko call karo aur Result namedtuple return karo.

    Dhyan dene wali baatein:
    - response.content ek LIST hai content blocks ki, string nahi.
      Har block ka .type check karna padta hai ("text", "thinking", ...).
      Seedha response.content[0].text maan lena ek classic bug hai.
    - response.usage mein input_tokens aur output_tokens milte hain.
    - response.stop_reason zaroor capture karna — "max_tokens" aaya matlab
      answer beech mein kata hai.
    - latency khud measure karo (time.perf_counter() se, call ke aage-peeche).
    """
    raise NotImplementedError("call_model implement karo")


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    TODO: dollars mein cost return karo.

    Trap: input aur output ka rate ALAG hai (output ~5x mehnga). Dono ko ek
    hi rate se multiply kar diya to answer galat aayega — ye sabse common
    mistake hai.

    Edge case: model PRICES mein na ho to kya karoge? Silently 0.0 return
    karna galat hai — us decision ko justify kar pana chahiye.
    """
    raise NotImplementedError("estimate_cost implement karo")


# ---------------------------------------------------------------- main ----

def main() -> int:
    if len(sys.argv) < 2:
        print(f'usage: python play.py "your prompt here" [model]')
        return 1

    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY set nahi hai. .env banao (.env.example dekho).")
        return 1

    client = anthropic.Anthropic()

    result = call_model(client, model, prompt)
    cost = estimate_cost(model, result.input_tokens, result.output_tokens)
    render(model, result, cost)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
