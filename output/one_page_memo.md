# Vireo Audio — Weekly First-Response SLA Memo

**To:** Neha Kulkarni, Support Operations Manager  
**Subject:** First-response SLA breach concentration — Q2 2026

## Executive takeaway

The cleaned export contains **11,200 unique tickets** after removing **616 migration duplicates**. Across the full period, **2,440 tickets breached first-response SLA (21.79%)**, representing **₹854,000** of direct SLA-credit exposure at the policy's ₹350 automatic-credit amount.

For **Q2 2026**, the breach rate was **25.25% (563/2,230)**, with **₹197,050** of direct SLA-credit exposure.

The clearest concentration is the **Morning shift**: **482 of 1,290 Q2 tickets breached (37.36%)**. Day shift was **8.62%** in the same quarter. The gap is especially visible in chat and email. This report is intended to focus the weekly conversation on where the SLA problem is concentrated; it does not claim that shift assignment itself is the cause.

## Recommended operating goal

A conservative, data-derived goal is to return the Q2 breach rate to the **21.79% full-period baseline** or lower. At the Q2 volume of 2,230 tickets, that means roughly **77 fewer breaches**, equivalent to about **₹26,950 per quarter** in direct SLA-credit exposure.

This is a direct credit-line opportunity only; it excludes any broader retention or satisfaction effects.

## What the weekly review should show

1. Weekly breach rate by shift, with Morning highlighted for review.
2. Agent-level breach counts and rates, with minimum-volume filtering to avoid overreacting to tiny samples.
3. Channel mix, because chat has the tightest SLA target (15 minutes) and is a major contributor to breach volume.
4. The raw ticket examples behind any unusually high agent/shift result before taking action.

## Scope and data handling

The export timestamps are UTC, while roster shifts are IST. The pipeline converts ticket creation time to IST before joining the active roster assignment. The policy defines first response as the first human agent reply and sets targets of 15 minutes for chat, 2 hours for voice, 4 hours for social and 8 hours for email.

The export contains 616 duplicated ticket IDs caused by legacy/current-system migration. Paired copies are identical except for legacy CSAT representation, so the helpdesk copy is retained.

The report does **not** infer causality from ticket text, use CSAT as a zero for non-response, recommend hiring, or optimize refunds/replacements. Headcount is explicitly frozen until Q4 in the supplied email thread.

## Reliability checks

All **11,200** deduplicated tickets have a valid channel target and exactly one roster assignment. There are no negative response times, no resolution-before-response records, and no duplicate IDs after deduplication. A **100-row stratified independent spot-check produced zero SLA target/breach mismatches**.

## Handoff

The Streamlit dashboard is the review surface. `weekly_sla_report.csv` is the weekly export, and `agent_sla_report.csv` is the agent/shift view. The core calculation is deterministic; an optional Gemini step can turn the computed tables into a short manager narrative without changing the underlying metrics.
