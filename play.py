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
    TODO: OpenRouter ko call karo aur Result namedtuple return karo.

    Call ka shape: client.chat.completions.create(model=..., max_tokens=...,
    messages=[{"role": "user", "content": prompt}])

    Response se 5 cheezein nikalni hain:

    - text            -> response.choices[0].message.content
                         `choices` ek LIST hai. Normally usme ek hi entry
                         hoti hai, par list hai isliye index blindly mat
                         maano — khaali list pe IndexError aayega.
                         Aur `.content` `None` ho sakta hai (e.g. model ne
                         sirf tool call kiya, ya reasoning-only turn). str
                         maan ke `.strip()` karoge to AttributeError.

    - input_tokens    -> response.usage.prompt_tokens
    - output_tokens   -> response.usage.completion_tokens
                         Naam alag hain Anthropic se (wahan input_tokens /
                         output_tokens hote hain). Ye OpenAI-shape hai.

    - finish_reason   -> response.choices[0].finish_reason
                         Values: "stop" (natural end), "length" (max_tokens
                         hit — answer kata hua hai), "tool_calls",
                         "content_filter". Anthropic ka "max_tokens" yahan
                         "length" hai.

    - latency_s       -> khud measure karo, time.perf_counter() se, call ke
                         aage-peeche. time.time() mat use karna.

    - reported_cost   -> response.usage.cost  (dollars mein, OpenRouter ka
                         apna hisaab). Ye har provider pe guaranteed nahi
                         hota, isliye safely access karna —
                         getattr(response.usage, "cost", None).

    Note: reasoning models ke thinking tokens `completion_tokens` mein hi
    count hote hain (breakdown `usage.completion_tokens_details.reasoning_tokens`
    mein milta hai). Day 5 ke comparison table mein ye matter karega.
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

    Bonus (OpenRouter ki wajah se possible): tumhara number aur
    response.usage.cost side-by-side print hote hain. Agar dono match nahi
    karte to kyun? Ye D-001 ka asli jawab hai.
    """
    raise NotImplementedError("estimate_cost implement karo")


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
