from pathlib import Path
import json
import os

import pandas as pd
import streamlit as st

from analyze import run

st.set_page_config(page_title="Vireo Audio SLA Monitor", layout="wide")
st.title("Vireo Audio — First-Response SLA Monitor")
st.caption("Deterministic SLA calculation + optional AI-assisted manager summary. Core arithmetic never depends on an LLM.")

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
SUMMARY_FILE = OUT_DIR / "analysis_summary.json"

if not SUMMARY_FILE.exists():
    if (DATA_DIR / "tickets.csv").exists() and (DATA_DIR / "agents.csv").exists():
        with st.spinner("Running deterministic SLA analysis..."):
            run(DATA_DIR, OUT_DIR)
    else:
        st.error(
            "The public repository does not include the supplied customer-level input dataset. "
            "The checked-in output reports are the submission snapshot. To regenerate them, "
            "place the supplied tickets.csv and agents.csv in data/; see data/README.md."
        )
        st.stop()

summary = json.loads(SUMMARY_FILE.read_text())
agent = pd.read_csv(OUT_DIR / "agent_sla_report.csv")
shift = pd.read_csv(OUT_DIR / "shift_sla_report.csv")
channel = pd.read_csv(OUT_DIR / "channel_sla_report.csv")
weekly = pd.read_csv(OUT_DIR / "weekly_sla_report.csv", parse_dates=["week_start_ist"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tickets", f"{summary['deduped_tickets']:,}")
c2.metric("SLA breaches", f"{summary['overall_breaches']:,}")
c3.metric("Breach rate", f"{summary['overall_breach_rate']:.1%}")
c4.metric("Credit exposure", f"₹{summary['overall_sla_credit_exposure_inr']:,.0f}")

st.subheader("Q2 2026 operating view")
q1, q2, q3, q4 = st.columns(4)
q1.metric("Q2 tickets", f"{summary['q2_2026_tickets']:,}")
q2.metric("Q2 breaches", f"{summary['q2_2026_breaches']:,}")
q3.metric("Q2 breach rate", f"{summary['q2_2026_breach_rate']:.1%}")
q4.metric("Q2 credit exposure", f"₹{summary['q2_2026_sla_credit_exposure_inr']:,.0f}")

st.subheader("Weekly breaches by shift")
pivot = weekly.pivot(index="week_start_ist", columns="roster_shift", values="breach_rate").fillna(0)
st.line_chart(pivot)

left, right = st.columns(2)
with left:
    st.subheader("Shift")
    st.dataframe(shift.sort_values("breach_rate", ascending=False), width="stretch")
with right:
    st.subheader("Channel")
    st.dataframe(channel.sort_values("breach_rate", ascending=False), width="stretch")

st.subheader("Agent report")
min_tickets = st.slider("Minimum tickets per agent", 1, 200, 30)
view = agent[agent.tickets >= min_tickets].copy()
st.dataframe(view, width="stretch", hide_index=True)

st.subheader("Manager takeaway")
st.write(
    f"In Q2 2026, Morning breached {summary['q2_morning_breach_rate']:.1%} of tickets "
    f"versus {summary['q2_day_breach_rate']:.1%} on Day. "
    "This is an operational concentration signal, not proof that shift assignment causes the gap. "
    f"A channel-matched Day-rate benchmark implies about {summary['q2_morning_benchmark_avoidable_breaches']:.0f} "
    "fewer Q2 Morning breaches, or approximately "
    f"₹{summary['q2_morning_benchmark_inr']:,.0f} of direct SLA-credit exposure. "
    "This is a benchmark opportunity, not a forecast."
)

st.subheader("Validation snapshot")
v = summary["validation"]
st.write(
    f"{v['raw_rows']:,} raw rows → {v['deduped_ticket_count']:,} unique tickets; "
    f"{v['duplicate_rows_removed']:,} migration duplicates removed. "
    f"Spot check: {v['spot_check_rows']} rows, {v['spot_check_mismatches']} mismatches."
)

# Optional AI layer: only runs if a key is supplied by the user.
if st.button("Generate AI manager summary"):
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        st.info("No GOOGLE_API_KEY set. Core report is complete without paid AI calls.")
    else:
        try:
            from google import genai

            client = genai.Client(api_key=key)
            prompt = f"""
You are writing a concise support-operations summary for Vireo Audio's Support Operations Manager.
Use only the supplied facts below. Do not invent causes. Separate observations from hypotheses.
Facts:
{json.dumps(summary, indent=2)}
Shift table:
{shift.to_dict(orient='records')}
Channel table:
{channel.to_dict(orient='records')}
Agent table (top 12 by breaches):
{agent.head(12).to_dict(orient='records')}
Write: 3 bullets of what changed, 3 bullets of who/where needs attention, and 2 concrete questions for the operations manager.
"""
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            st.markdown(resp.text)
        except Exception as e:
            st.error(f"AI summary failed safely; deterministic report remains available. {e}")

st.caption("SLA policy: chat 15m, voice 2h, social 4h, email 8h. Breach credit exposure uses ₹350 per breached ticket.")
