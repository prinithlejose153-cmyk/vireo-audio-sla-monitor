# Vireo Audio — Submission Form Draft

## 1. What did you build, and what business outcome does it move?

I built a first-response SLA monitoring tool that turns Vireo's raw support export into a weekly operating view by **agent, shift, channel and week**.

Across **11,200 unique tickets, 2,440 breached SLA (21.79%)**, creating **₹854,000 of direct SLA-credit exposure** at ₹350 per breach.

Q2 2026 is worse: **563 of 2,230 tickets breached (25.25%)**, representing **₹197,050** of direct exposure. My target is to bring Q2 back to the **21.79% observed baseline or better**. At the same Q2 volume, that is approximately **77 fewer breaches and ₹26,950 less direct SLA-credit exposure per quarter**.

I deliberately call this direct credit exposure, not total business savings — the data does not justify claiming more than that.

## 2. What does one run cost, and what would a month cost at Vireo's volume?

**₹0.**

The production-critical path does not require a paid LLM/API call. SLA calculation, timezone conversion, roster matching, deduplication and reporting are handled locally with Python/pandas.

Vireo's stated volume is approximately **650 tickets/week**:

`650 × 4.33 weeks/month ≈ 2,815 tickets/month`

`2,815 tickets × ₹0 paid API cost = ₹0/month`

The optional Gemini manager-summary layer is outside the critical path. The tool still produces the SLA report without it.

## 3. How do you know it works?

The export contained **11,816 rows**. I identified **616 migration re-import rows**, leaving **11,200 unique tickets** for analysis.

- 11,200/11,200 tickets had a valid channel SLA target.
- 11,200/11,200 matched exactly one applicable roster assignment.
- 0 negative response times.
- 0 missing first-response timestamps.
- 0 resolution-before-response cases.
- 0 duplicate IDs after cleanup.
- 100-ticket stratified spot check.
- 0 spot-check mismatches → **0% observed error in that sample**.

The pipeline explicitly guards against malformed timestamps, missing/ambiguous roster assignments and migration duplicates. The LLM is never used to decide whether a ticket breached SLA.

## 4. Did you change, narrow, or push back on the client's ask?

**Yes — in three places.**

First, I pushed back on using an LLM for the actual SLA decision. The policy gives explicit numerical thresholds, so I made that logic deterministic and auditable.

Second, I did not turn the Morning-shift finding into a hiring recommendation. The client email explicitly says headcount is frozen until Q4. I reported Morning concentration as an operational signal to investigate.

Third, I resolved the migration ambiguity instead of counting every exported row. Where the same ticket appeared in both legacy and current helpdesk data, I retained the current helpdesk copy and converted timestamps to IST before roster/shift attribution.

## 5. What is wrong with what you are handing us?

This is a strong analytical prototype, not a production deployment.

Known limitations:
- it identifies where breaches are concentrated, but does not establish causal root causes;
- the optional Gemini summary can be imperfect and is not authoritative;
- there is no production authentication, authorization or monitoring layer;
- validation is dataset-level validation plus a 100-row spot check, not a full regression suite for every future export shape.

For the supplied dataset, the SLA calculation produced **0 mismatches in the 100-row validation sample**.

## 6. What did you deliberately leave out, and why?

I left out causal root-cause classification, hiring recommendations, agent performance scoring and broad CSAT optimization.

These were either unsupported by the supplied evidence, explicitly constrained by the client, or outside the first-response SLA problem. I prioritized a trustworthy operational measurement layer over a broader but less defensible analytics product.

## 7. Anything you built or found that nobody asked for?

I added migration-deduplication, automated validation, channel-level reporting and a 100-ticket stratified accuracy check.

I also added an optional AI manager-summary layer based only on already-computed metrics.

A useful additional finding was the Q2 shift concentration: **Morning breached 37.36% versus 8.62% for Day**. I present this as an investigation signal, not a causal conclusion.

## 8. What did you use AI for?

I used **ChatGPT and Gemini** during development for implementation assistance, debugging, analysis review, prompt iteration and the optional manager-summary layer.

The most important AI decision was what I threw away: I rejected LLM-based SLA breach classification because the policy gives explicit numerical thresholds. I also discarded prompts that asked the model to calculate metrics Python could calculate exactly.

AI remains only where language generation adds value; the business-critical numbers come from deterministic code.

**Screen recording:** https://drive.google.com/file/d/1DzhA-IK4kCz9-iOsZCMnREmL5M3FQTTN/view?usp=drive_link

## 9. Public Google Drive link

https://drive.google.com/file/d/1DzhA-IK4kCz9-iOsZCMnREmL5M3FQTTN/view?usp=drive_link

## 10. Someone picks this up on Monday and you are unreachable. Three things they need to know.

1. Do not replace the deterministic SLA calculation with an LLM.
2. Do not count the 616 migration re-import rows twice; current helpdesk is retained when both copies exist.
3. Treat the Morning concentration as an investigation signal, not proof that shift assignment causes the gap.

## 11. Honest hours spent

**Fill with actual elapsed working time.**

## 12. GitHub repo

**Fill with the public repository URL after pushing this project.**
