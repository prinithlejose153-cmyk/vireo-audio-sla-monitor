# Vireo Audio — First-Response SLA Monitor

A reproducible first-response SLA monitoring tool built for the Vireo Audio support-operations take-home.

## What it does

The tool converts the supplied support export into an operational view by **week, agent, shift and channel**.

The critical SLA path is deliberately deterministic:

- applies the policy SLA targets: chat 15m, voice 2h, social 4h, email 8h;
- converts ticket timestamps from UTC to IST before roster/shift attribution;
- resolves legacy/current helpdesk migration re-imports;
- joins tickets to the active agent roster;
- calculates first-response breach and ₹350 direct SLA-credit exposure;
- produces weekly, shift, channel and agent reports;
- validates data-quality assumptions and runs a 100-row stratified spot check;
- optionally uses Gemini only to turn already-computed results into a manager-facing summary.

**The LLM is never the source of truth for the SLA calculation.**

## Submission snapshot

The supplied export produced:

| Metric | Result |
|---|---:|
| Raw rows | 11,816 |
| Unique tickets after migration cleanup | 11,200 |
| Duplicate rows removed | 616 |
| Overall SLA breaches | 2,440 |
| Overall breach rate | 21.79% |
| Overall direct SLA-credit exposure | ₹854,000 |
| Q2 2026 tickets | 2,230 |
| Q2 2026 breaches | 563 |
| Q2 2026 breach rate | 25.25% |
| Q2 2026 direct SLA-credit exposure | ₹197,050 |
| Q2 Morning breach rate | 37.36% |
| Q2 Day breach rate | 8.62% |
| 100-row spot-check mismatches | 0 |

The conservative business goal used in the memo is to return Q2's 25.25% breach rate to the observed full-period baseline of **21.79% or lower**. At the observed Q2 volume, that is approximately **77 fewer breaches / ₹26,950 per quarter** in direct SLA-credit exposure.

## Quick start

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Run the dashboard

The public repo includes the checked-in `output/` submission snapshot, so the Streamlit dashboard can be opened without exposing the source customer dataset:

```bash
streamlit run app.py
```

### Regenerate the analysis

The public repository intentionally excludes the supplied customer-level input files. To regenerate the exact reports, place the supplied `tickets.csv` and `agents.csv` in `data/` and run:

```bash
python analyze.py
```

See [`data/README.md`](data/README.md) for the privacy/reproducibility note.

## Scope decisions

### 1. Migration duplicates

The raw export contains **616 extra rows from migration re-imports**. When the same ticket appears in both `legacy_fd` and `helpdesk`, the current helpdesk copy is retained.

### 2. SLA calculation

First response is calculated as:

`first_response_at - created_at`

The supplied timestamps are UTC. The ticket is converted to IST before roster/shift attribution. Breach is `response_minutes > channel_target_minutes`.

### 3. Agent and shift attribution

The ticket's `agent_id` is joined to the roster assignment active on the ticket's IST creation date. The resolving agent is used for reporting, consistent with the supplied policy.

### 4. Business outcome

The financial metric is **direct SLA-credit exposure** using the policy's ₹350 automatic store-credit amount per breached ticket. It is not presented as total business cost or customer-retention value.

### 5. No unsupported staffing conclusion

The client email says headcount is frozen until Q4. The Morning-vs-Day gap is therefore reported as an operational concentration signal, not converted into a hiring recommendation or causal claim.

### 6. Deliberate exclusions

This first version does not attempt causal root-cause classification from free text, agent performance scoring, refund/replacement optimization, or broad CSAT optimization. Those require additional evidence and would expand the scope beyond the first-response SLA problem.

## Validation

The pipeline checks:

- channel SLA target exists for every analyzed ticket;
- exactly one roster assignment matches each analyzed ticket;
- no negative response times;
- no missing first-response timestamps;
- no resolution-before-response cases;
- no duplicate IDs after deduplication;
- a 100-row stratified spot check across channel and shift.

The supplied dataset produced **0 spot-check mismatches (0% observed error in that sample)**.

## AI usage

AI was used during development for implementation assistance, debugging, analysis review, prompt iteration and manager-facing narrative design.

The important architectural decision was to **discard LLM-based breach classification**. The policy gives explicit numerical thresholds, so timestamp arithmetic and roster attribution are better handled deterministically and auditable in Python.

The optional Gemini layer (`gemini-2.5-flash`) receives already-computed metrics and generates a concise manager summary. The dashboard and core reports remain fully usable without an API key.

## Repository structure

```text
.
├── analyze.py
├── app.py
├── requirements.txt
├── README.md
├── AI_PROMPTS.md
├── screen-recording-script.md
├── submission-form.md
├── data/
│   └── README.md
└── output/
    ├── analysis_summary.json
    ├── agent_sla_report.csv
    ├── channel_sla_report.csv
    ├── headline_metrics.csv
    ├── one_page_memo.md
    ├── shift_sla_report.csv
    └── weekly_sla_report.csv
```

## Handoff notes

1. Do not replace the deterministic SLA calculation with an LLM.
2. Do not count the 616 migration re-import rows twice.
3. Treat the Morning concentration as an investigation signal, not proof of causality.

## License / data note

This repository contains implementation and derived submission artifacts for a take-home exercise. The supplied customer-level source data is intentionally excluded from the public repository.
