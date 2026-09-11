# llm-playground

Week 1 project of my [8-week Gen AI sprint](https://claude.ai/code/artifact/d07db259-4b51-4d99-bdd9-fc428122dac1).

Ek CLI tool jo LLM API ko **black box ki tarah nahi, ek measurable system
component ki tarah** treat karta hai — har call pe tokens, latency aur dollar
cost visible hote hain.

## Kyun

Gen AI interviews mein sabse common sawal hai: *"is feature ka cost kya
aayega?"* aur *"latency kahan ja rahi hai?"*. Un sawalon ka jawab documentation
padh ke nahi, khud measure karke aata hai. Ye tool wahi measurement layer hai.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # phir .env mein apni API key daalo
```

## Usage

```bash
python play.py "Explain cosine similarity in two sentences"
```

## Roadmap (Week 1, day by day)

- [ ] **Day 1** — single model call; tokens, cost, `stop_reason` print karna
- [ ] **Day 2** — streaming, aur TTFT vs total latency measure karna
- [ ] **Day 3** — prompt caching; `cache_read_input_tokens` se verify karna
- [ ] **Day 4** — structured output (Pydantic schema se validated JSON)
- [ ] **Day 5** — multi-model comparison + retry with exponential backoff
- [ ] **Day 6** — typed error handling (429 / 5xx / 400 alag-alag)
- [ ] **Day 7** — README mein final cost comparison table

## Cost comparison

_Day 5 ke baad yahan apne measured numbers bharne hain — copy-paste nahi,
khud ke runs se._

| Model | Input $/1M | Output $/1M | Latency (p50) | Cost / 1k requests |
|---|---|---|---|---|
| claude-opus-5 | 5.00 | 25.00 | — | — |
| claude-sonnet-5 | 2.00 | 10.00 | — | — |
| claude-haiku-4-5 | 1.00 | 5.00 | — | — |

## Decisions

Har technical choice ka reason [`DECISIONS.md`](./DECISIONS.md) mein hai.
