# AI Usage / Prompt Log

## Discarded approach — LLM decides SLA breach

> Read the ticket text and decide whether each ticket breached SLA.

**Why it was discarded:** the SLA breach is a deterministic timestamp calculation governed by explicit policy thresholds. Using an LLM here would add unnecessary ambiguity and make the critical business number harder to audit.

## Discarded approach — LLM performs the arithmetic

Early prompt iterations asked the model to calculate or reconstruct metrics from raw/partial tables.

**Why it was discarded:** Python/pandas can calculate timestamp differences, joins, rates and money exactly. The model should not be the source of truth for those numbers.

## Final optional manager-summary prompt

```text
You are writing a concise support-operations summary for Vireo Audio's Support Operations Manager.

Use only the supplied computed facts and tables. Do not invent causes. Separate observations from hypotheses. Do not rank individual employees beyond reporting the supplied metrics.

Return:
1. Three bullets: what changed / where concentration exists.
2. Three bullets: agents or shifts that should be reviewed, using supplied breach counts/rates.
3. Two concrete questions the manager should ask in the weekly review.

The deterministic pipeline supplies:
- ticket counts;
- channel SLA targets;
- breach counts and rates;
- weekly trends;
- agent/shift attribution;
- direct ₹350 breach-credit exposure.

Never recompute timestamps yourself. Never infer causality from free-text ticket messages unless explicitly labeled as a hypothesis.
```

## Tools used

- ChatGPT: analysis design, implementation assistance, debugging, review, memo/submission drafting and edge-case review.
- Gemini (`gemini-2.5-flash` via `google-genai`): optional narrative summary only.

The production-critical calculation path does not require an API key or paid model call.
