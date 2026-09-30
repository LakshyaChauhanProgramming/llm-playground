# days/ — har complete din ka frozen snapshot

Root ka `play.py` "current working file" hai — usme abhi jis din pe kaam chal
raha hai wahi hota hai (aksar aadha-bhara, TODOs ke saath).

Jab koi din **complete** ho jaata hai, us din ka finished `play.py` yahan
`days/dayN/play.py` mein copy ho jaata hai — frozen. Baad mein aa ke dekh sakte
ho ki us din exactly kya banaya tha, bina git history khodne ke.

> Rule: din khatam -> `cp play.py days/dayN/play.py` -> is index mein ek line.

---

## Day 1 — single call: tokens + cost + finish_reason
**Snapshot:** [`day1/play.py`](./day1/play.py) · **Status:** ✅ complete

- `call_model()` — OpenRouter ko ek call, defensive parsing (choices/usage/
  content missing ho to safely handle), `time.perf_counter()` se latency.
- `estimate_cost()` — local `PRICES` table se input/output rates, unknown model
  par `KeyError` (fail-fast).
- OpenRouter ka reported `usage.cost` bhi dikhata hai + apne calc se difference.

## Day 2 — streaming + TTFT vs total latency
**Snapshot:** [`day2/play.py`](./day2/play.py) · **Status:** ✅ complete

- `call_model_streaming()` — `stream=True`, chunks aate hi read.
- **TTFT** (pehla token kab aaya = perceived speed) aur **total latency** (pura
  jawab kab bana) alag measure. `render` dono + generation time dikhata hai.
- Streaming mein usage `stream_options={"include_usage": True}` se maangna padta
  hai (aakhri chunk mein aata hai).
- CLI: `python play.py "..." [model] --stream`
