# Decisions

> Har technical choice, uska reason, aur kaunsa alternative reject kiya aur kyun.
> Interview ke "project deep-dive" round ki cheat-sheet yahi file hai —
> 6 hafte baad khud yaad nahi rahega ki kya kyun kiya tha.

Format: ek entry per decision.

---

## D-001 — Cost calculation client-side, API se nahi

**Date:** ```September 23, 2026```

**Context:** ```Hamen OpenRouter API ko call karne ke baad response ke tokens aur unki total dynamic cost calculate karni thi. OpenRouter response object ke andar response.usage.cost (reported_cost) provide toh karta hai, par yeh har provider ya custom local setup par guaranteed nahi hota. Iske alawa, upstream API gateways par billing updates me thoda network lag ya discrepancy ho sakti hai. ```

**Decision:** ```Humne cost calculation ko client-side (estimate_cost function ke andar) implement karne ka faisla kiya hai. Iske liye hum local PRICES configuration dictionary aur strict input/output tracking mechanism ka use kar rahe hain.```

**Alternatives rejected:** 

- **Fully relying on API Reported Cost:** OpenRouter ka response.usage.cost field OpenAI spec ka official part nahi hai. Agar hum future me OpenRouter se directly kisi open-source provider (jaise vLLM ya Ollama) ya seedhe official OpenAI SDK par switch karte hain, toh yeh custom attribute crash kar jayega. Isliye ise primary source banana reject kiya gaya.

- **Blending average token pricing:** Input aur output tokens dono ko single flat rate par treat karna reject kar diya gaya, kyunki LLM ecosystem me output generation humesha input parsing se 4x-5x zyada computation-heavy aur mehngi hoti hai.

**Tradeoff:**

- **Maintenance Overhead:** Jab bhi providers (jaise Anthropic ya OpenAI) apne token prices badlenge ya naye models launch karenge, hamen local PRICES table ko manually up-to-date rakhna padega.

- **Accuracy Mismatch:** Agar OpenRouter background me koi extra discount, free tier, ya internal rounding apply karta hai, toh hamare local calculation (cost (mera calc)) aur OpenRouter ke exact balance deduction (cost (OpenRouter)) me chhota sa difference (delta) dikh sakta hai.

---

## D-002 — Provider: OpenRouter, direct Anthropic SDK nahi

**Date:** 2026-09-17

**Context:** Is project ka core deliverable **multi-model cost aur latency
comparison** hai (Opus vs Sonnet vs Haiku, aage chal ke open-weight models
bhi). Mere paas OpenRouter ka key already hai.

**Decision:** OpenRouter (`https://openrouter.ai/api/v1`) ko `openai` SDK ke
through use kar raha hoon — `base_url` override karke. Ek key, ek client, ek
response shape; model switch karne ke liye sirf model string badalti hai.

**Alternatives rejected:**
- *Direct `anthropic` SDK* — sirf Claude models deta hai. Week 5 mein jab
  open-weight models (Llama / Mistral / Qwen) compare karne honge, tab dusra
  SDK aur dusra auth add karna padta. Aur har provider ka response shape alag
  hota, to comparison code hi teen jagah branch karta.
- *Har provider ka apna SDK + khud ka abstraction layer likhna* — wahi kaam
  hai jo OpenRouter already kar raha hai. Week 1 ka time usme nahi jaana
  chahiye.

**Tradeoff — kya kho diya:**
- Anthropic ke **native API details** direct nahi dikhte: content blocks ki
  list, `stop_reason` ki values, adaptive thinking config, `cache_control`
  breakpoints. OpenRouter sab kuch OpenAI shape mein normalize kar deta hai.
  *Ye interview mein poochha jaata hai*, isliye theory alag se padhni padegi
  — code se apne aap nahi aayegi.
- Ek **extra hop** beech mein — latency measurement mein OpenRouter ka routing
  overhead bhi shamil hai. Matlab mere numbers "Anthropic API ki latency" nahi,
  "OpenRouter ke through Anthropic ki latency" hain. README mein ye disclose
  karna hai.
- **Routing non-determinism** — OpenRouter ek model ke liye multiple upstream
  providers use kar sakta hai, to latency run-to-run vary kar sakti hai.
- **Vendor dependency** — ek aur service beech mein, jo down ho sakti hai.

**Bonus jo mila:** `usage.cost` response mein aata hai, matlab apna calculated
cost server ke reported cost se verify kar sakta hoon (D-001 ka direct test).

_Pricing note:_ inference pe markup nahi hai (rates Anthropic ke barabar,
`/api/v1/models` se verify kiye), par credits kharidne pe 5.5% Stripe fee hai —
to effective cost thoda zyada hai.

---

_Naye decisions yahan add karte jao._
