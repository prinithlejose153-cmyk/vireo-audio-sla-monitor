from pathlib import Path
import argparse
import json

import numpy as np
import pandas as pd

TARGETS_MIN = {"chat": 15, "voice": 120, "social": 240, "email": 480}
IST = "Asia/Kolkata"
BREACH_CREDIT_INR = 350


def load_data(data_dir):
    data_dir = Path(data_dir)
    required = ["tickets.csv", "agents.csv"]
    missing = [name for name in required if not (data_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required input files: " + ", ".join(missing) +
            ". The public repository intentionally excludes the supplied customer-level dataset; "
            "see data/README.md for the expected input pack."
        )

    tickets = pd.read_csv(data_dir / "tickets.csv")
    agents = pd.read_csv(data_dir / "agents.csv")

    for c in ["created_at", "first_response_at", "resolved_at"]:
        tickets[c] = pd.to_datetime(tickets[c], errors="coerce", utc=True)
    agents["from_date"] = pd.to_datetime(agents["from_date"], errors="coerce")
    agents["to_date"] = pd.to_datetime(agents["to_date"], errors="coerce")
    agents["to_date_f"] = agents["to_date"].fillna(pd.Timestamp("2099-12-31"))
    return tickets, agents


def attach_roster(tickets, agents):
    t = tickets.copy()

    # Migration duplicates: same ticket can appear once in legacy_fd and once in helpdesk.
    # Keep the current helpdesk copy when both exist.
    t["_source_rank"] = t["source_system"].map({"legacy_fd": 0, "helpdesk": 1}).fillna(0)
    t = t.sort_values(["ticket_id", "_source_rank"]).drop_duplicates("ticket_id", keep="last")
    t = t.drop(columns="_source_rank")

    t["created_ist"] = t["created_at"].dt.tz_convert(IST)
    t["channel"] = t["channel"].str.lower()
    t["target_min"] = t["channel"].map(TARGETS_MIN)
    t["response_min"] = (t["first_response_at"] - t["created_at"]).dt.total_seconds() / 60
    t["breach"] = t["response_min"] > t["target_min"]

    roster_cols = []
    roster_match_counts = []
    for _, row in t.iterrows():
        date = row["created_ist"].date()
        g = agents[
            (agents["agent_id"] == row["agent_id"])
            & (agents["from_date"].dt.date <= date)
            & (agents["to_date_f"].dt.date >= date)
        ]
        roster_match_counts.append(len(g))
        if len(g):
            r = g.iloc[0]
            roster_cols.append((r["name"], r["site"], r["team"], r["shift"]))
        else:
            roster_cols.append((np.nan, np.nan, np.nan, np.nan))

    t["_roster_match_count"] = roster_match_counts
    t[["agent_name", "site", "roster_team", "roster_shift"]] = pd.DataFrame(
        roster_cols, index=t.index
    )
    t["week_start_ist"] = (
        t["created_ist"].dt.normalize()
        - pd.to_timedelta(t["created_ist"].dt.weekday, unit="D")
    )
    t["month"] = t["created_ist"].dt.strftime("%Y-%m")
    # Drop timezone before Period conversion to avoid pandas' timezone warning.
    t["quarter"] = t["created_ist"].dt.tz_localize(None).dt.to_period("Q").astype(str)
    return t


def make_reports(t):
    weekly = (
        t.groupby(["week_start_ist", "roster_shift"])
        .agg(tickets=("ticket_id", "size"), breaches=("breach", "sum"))
        .reset_index()
    )
    weekly["breach_rate"] = weekly["breaches"] / weekly["tickets"]
    weekly["sla_credit_exposure_inr"] = weekly["breaches"] * BREACH_CREDIT_INR

    agent = (
        t.groupby(["agent_id", "agent_name", "site", "roster_team", "roster_shift"])
        .agg(
            tickets=("ticket_id", "size"),
            breaches=("breach", "sum"),
            breach_rate=("breach", "mean"),
            median_response_min=("response_min", "median"),
        )
        .reset_index()
    )
    agent["sla_credit_exposure_inr"] = agent["breaches"] * BREACH_CREDIT_INR
    agent = agent.sort_values(["breaches", "tickets"], ascending=[False, False])

    shift = (
        t.groupby("roster_shift")
        .agg(tickets=("ticket_id", "size"), breaches=("breach", "sum"))
        .reset_index()
    )
    shift["breach_rate"] = shift["breaches"] / shift["tickets"]
    shift["sla_credit_exposure_inr"] = shift["breaches"] * BREACH_CREDIT_INR

    channel = (
        t.groupby("channel")
        .agg(tickets=("ticket_id", "size"), breaches=("breach", "sum"))
        .reset_index()
    )
    channel["breach_rate"] = channel["breaches"] / channel["tickets"]
    channel["sla_credit_exposure_inr"] = channel["breaches"] * BREACH_CREDIT_INR

    return weekly, agent, shift, channel


def build_summary(t):
    q2 = t[t["quarter"] == "2026Q2"]
    day = t[t["roster_shift"] == "Day"]
    morning = t[t["roster_shift"] == "Morning"]

    day_rates = day.groupby("channel")["breach"].mean()
    morning_vol = morning.groupby("channel").size()
    expected_morning_at_day_rate = float((morning_vol * day_rates).sum())
    actual_morning = int(morning["breach"].sum())

    q2_morning = q2[q2["roster_shift"] == "Morning"]
    q2_day = q2[q2["roster_shift"] == "Day"]

    q2_expected_morning_at_day_rate = float(
        (
            q2_morning.groupby("channel").size()
            * q2_day.groupby("channel")["breach"].mean()
        ).sum()
    )

    result = {
        "deduped_tickets": int(len(t)),
        "overall_breaches": int(t["breach"].sum()),
        "overall_breach_rate": float(t["breach"].mean()),
        "overall_sla_credit_exposure_inr": int(t["breach"].sum() * BREACH_CREDIT_INR),
        "q2_2026_tickets": int(len(q2)),
        "q2_2026_breaches": int(q2["breach"].sum()),
        "q2_2026_breach_rate": float(q2["breach"].mean()),
        "q2_2026_sla_credit_exposure_inr": int(q2["breach"].sum() * BREACH_CREDIT_INR),
        "q2_morning_tickets": int(len(q2_morning)),
        "q2_morning_breaches": int(q2_morning["breach"].sum()),
        "q2_morning_breach_rate": float(q2_morning["breach"].mean()),
        "q2_day_tickets": int(len(q2_day)),
        "q2_day_breaches": int(q2_day["breach"].sum()),
        "q2_day_breach_rate": float(q2_day["breach"].mean()),
        "morning_tickets": int(len(morning)),
        "morning_breaches": actual_morning,
        "morning_breach_rate": float(morning["breach"].mean()),
        "day_breach_rate": float(day["breach"].mean()),
        "morning_counterfactual_breaches_at_day_channel_rates": expected_morning_at_day_rate,
        "morning_counterfactual_avoidable_breaches": actual_morning - expected_morning_at_day_rate,
        "q2_morning_benchmark_avoidable_breaches": int(q2_morning["breach"].sum()) - q2_expected_morning_at_day_rate,
        "q2_morning_benchmark_inr": (
            int(q2_morning["breach"].sum()) - q2_expected_morning_at_day_rate
        ) * BREACH_CREDIT_INR,
    }
    return result


def validate(raw, t):
    checks = {
        "raw_rows": int(len(raw)),
        "unique_ticket_ids": int(raw["ticket_id"].nunique()),
        "duplicate_rows_removed": int(len(raw) - len(t)),
        "deduped_ticket_count": int(len(t)),
        "all_channels_have_policy_target": int(t["target_min"].notna().sum()),
        "all_tickets_roster_matched": int((t["_roster_match_count"] == 1).sum()),
        "tickets_with_zero_roster_matches": int((t["_roster_match_count"] == 0).sum()),
        "tickets_with_multiple_roster_matches": int((t["_roster_match_count"] > 1).sum()),
        "negative_response_times": int((t["response_min"] < 0).sum()),
        "missing_first_response": int(t["first_response_at"].isna().sum()),
        "resolution_before_first_response": int(
            (t["resolved_at"].notna() & (t["resolved_at"] < t["first_response_at"])).sum()
        ),
        "duplicate_ids_after_dedupe": int(t["ticket_id"].duplicated().sum()),
    }

    # Independent 100-row stratified spot check across channel and shift.
    parts = []
    for ch in TARGETS_MIN:
        for sh in ["Morning", "Day", "Night"]:
            sub = t[(t["channel"] == ch) & (t["roster_shift"] == sh)]
            if len(sub):
                parts.append(sub.sample(n=min(9, len(sub)), random_state=42))
    sample = pd.concat(parts).drop_duplicates().head(100)
    expected_target = sample["channel"].map(TARGETS_MIN)
    expected_response = (sample["first_response_at"] - sample["created_at"]).dt.total_seconds() / 60
    expected_breach = expected_response > expected_target
    row_mismatch = (expected_target != sample["target_min"]) | (expected_breach != sample["breach"])
    checks["spot_check_rows"] = int(len(sample))
    checks["spot_check_mismatches"] = int(row_mismatch.sum())
    checks["spot_check_error_rate"] = float(row_mismatch.mean()) if len(sample) else 0.0
    return checks


def run(data_dir, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw, agents = load_data(data_dir)
    t = attach_roster(raw, agents)
    weekly, agent, shift, channel = make_reports(t)

    weekly.to_csv(output_dir / "weekly_sla_report.csv", index=False)
    agent.to_csv(output_dir / "agent_sla_report.csv", index=False)
    shift.to_csv(output_dir / "shift_sla_report.csv", index=False)
    channel.to_csv(output_dir / "channel_sla_report.csv", index=False)

    summary = build_summary(t)
    summary["raw_rows"] = int(len(raw))
    summary["duplicate_rows_removed"] = int(len(raw) - len(t))
    summary["unique_ticket_ids"] = int(raw["ticket_id"].nunique())
    summary["channels"] = t["channel"].value_counts().to_dict()
    summary["sources_after_dedupe"] = t["source_system"].value_counts().to_dict()
    summary["validation"] = validate(raw, t)
    (output_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run Vireo Audio first-response SLA analysis.")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--output-dir", default="output")
    args = p.parse_args()
    s = run(args.data_dir, args.output_dir)
    print(json.dumps(s, indent=2, default=str))
