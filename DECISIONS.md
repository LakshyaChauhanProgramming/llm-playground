# Decisions

> Har technical choice, uska reason, aur kaunsa alternative reject kiya aur kyun.
> Interview ke "project deep-dive" round ki cheat-sheet yahi file hai —
> 6 hafte baad khud yaad nahi rahega ki kya kyun kiya tha.

Format: ek entry per decision.

---

## D-001 — Cost calculation client-side, API se nahi

**Date:** _fill karo_
**Context:** _kya problem thi_
**Decision:** _kya choose kiya_
**Alternatives rejected:** _kya nahi choose kiya, aur kyun_
**Tradeoff:** _kya kho diya is choice mein_

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
