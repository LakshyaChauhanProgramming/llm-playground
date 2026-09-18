# llm-playground

Week 1 project of my [8-week Gen AI sprint](https://claude.ai/code/artifact/d07db259-4b51-4d99-bdd9-fc428122dac1).

Ek CLI tool jo LLM API ko **black box ki tarah nahi, ek measurable system
component ki tarah** treat karta hai — har call pe tokens, latency aur dollar
cost visible hote hain.

## Kyun

Gen AI interviews mein sabse common sawal hai: *"is feature ka cost kya
aayega?"* aur *"latency kahan ja rahi hai?"*. Un sawalon ka jawab documentation
padh ke nahi, khud measure karke aata hai. Ye tool wahi measurement layer hai.

## Provider — OpenRouter

Direct provider SDK ki jagah **[OpenRouter](https://openrouter.ai)** use kar
raha hoon: ek API key se Anthropic, OpenAI, Google, Meta — sab ke models.

Multi-model comparison is project ka core deliverable hai, aur OpenRouter pe
wo sirf **model string badalne** se ho jaata hai — teen alag SDK, teen alag
auth, teen alag response shape handle karne ki zaroorat nahi.

Uska API **OpenAI Chat Completions shape** follow karta hai, isliye SDK
`openai` hai — sirf `base_url` `https://openrouter.ai/api/v1` pe point karta
hai. Provider koi bhi ho, response ka shape same rehta hai.

| | OpenRouter (OpenAI shape) | Native Anthropic API |
|---|---|---|
| Text | `choices[0].message.content` (string) | `content[]` (blocks list, `.type` check karo) |
| Input tokens | `usage.prompt_tokens` | `usage.input_tokens` |
| Output tokens | `usage.completion_tokens` | `usage.output_tokens` |
| Why it stopped | `choices[0].finish_reason` → `"stop"` / `"length"` | `stop_reason` → `"end_turn"` / `"max_tokens"` |
| Cached tokens | `usage.prompt_tokens_details.cached_tokens` | `usage.cache_read_input_tokens` |
| Cost | **`usage.cost`** — server khud batata hai | khud calculate karna padta hai |

Wo aakhri row is project ke liye bonus hai: apna calculated cost aur
OpenRouter ka reported cost side-by-side compare kar sakta hoon.

**Model IDs** mein dots hote hain, dashes nahi —
`anthropic/claude-haiku-4.5`, **not** `claude-haiku-4-5`.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # phir .env mein OPENROUTER_API_KEY daalo
```

Key yahan se: <https://openrouter.ai/keys>

## Usage

```bash
python play.py "Explain cosine similarity in two sentences"
python play.py "Explain cosine similarity in two sentences" anthropic/claude-haiku-4.5
```

## Roadmap (Week 1, day by day)

- [ ] **Day 1** — single model call; tokens, cost, `finish_reason` print karna
- [ ] **Day 2** — streaming, aur TTFT vs total latency measure karna
- [ ] **Day 3** — prompt caching; `prompt_tokens_details.cached_tokens` se verify karna
- [ ] **Day 4** — structured output (Pydantic schema se validated JSON)
- [ ] **Day 5** — multi-model comparison + retry with exponential backoff
- [ ] **Day 6** — typed error handling (429 / 5xx / 400 alag-alag)
- [ ] **Day 7** — README mein final cost comparison table

## Cost comparison

_Day 5 ke baad yahan apne measured numbers bharne hain — copy-paste nahi,
khud ke runs se._

| Model | Input $/1M | Output $/1M | Latency (p50) | Cost / 1k requests |
|---|---|---|---|---|
| `anthropic/claude-opus-5` | 5.00 | 25.00 | — | — |
| `anthropic/claude-sonnet-5` | 2.00 | 10.00 | — | — |
| `anthropic/claude-haiku-4.5` | 1.00 | 5.00 | — | — |

Rates OpenRouter ke `/api/v1/models` endpoint se verify kiye (2026-09-17) —
Anthropic ke direct rates se exactly match karte hain. OpenRouter **inference
pe markup nahi lagata**; fee sirf credits kharidte waqt lagti hai (Stripe
5.5%, minimum $0.80). Matlab per-token math wahi rehta hai, par *effective*
cost ~5.5% zyada — ye distinction cost estimate karte waqt bolna padta hai.

## Decisions

Har technical choice ka reason [`DECISIONS.md`](./DECISIONS.md) mein hai.
