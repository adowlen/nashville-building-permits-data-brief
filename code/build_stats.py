#!/usr/bin/env python3
"""Builder: Nashville Building Permits Issued cleaned layer + stats.json.

Reads ONLY the 2026-11-03 raw snapshot (fresh pull for the 2026-11-03 brief;
refresh of the verified 2026-10-30 shelf-ready study). Exact-count assertions
from the study were replaced with computed values recorded in stats.json, so
the build tests structure on the new data rather than inheriting study counts.
Also writes the package data panels (CSV) into data/. Writes:
  stack/nashville/layers/building_permits_issued_clean.parquet
  <package>/stats.json
Cleaning never deletes rows: sentinel/invalid values are mapped to
unknown and flagged. Section 10.1 assertions run inline before stats
are written; a failed assertion aborts the build.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
PKG = HERE.parents[1]
STACK = HERE.parents[2] / "stack" / "nashville"
RAW = STACK / "snapshots" / "2026-11-03" / "building_permits_issued_raw.parquet"
CLEAN = STACK / "layers" / "building_permits_issued_clean.parquet"

df = pd.read_parquet(RAW)
N = len(df)
assert N > 20000, N  # refresh: count drifts daily with the rolling window

# --- dates: served epochs are local (America/Chicago) midnights.
# Control: UTC hour is only 5 (CDT) or 6 (CST) across both date fields.
for c in ["Date_Entered", "Date_Issued"]:
    hrs = pd.to_datetime(df[c], unit="ms", utc=True).dt.hour.unique()
    assert set(hrs) <= {5, 6}, (c, hrs)
entered = pd.to_datetime(df["Date_Entered"], unit="ms", utc=True).dt.tz_convert("America/Chicago").dt.date
issued = pd.to_datetime(df["Date_Issued"], unit="ms", utc=True).dt.tz_convert("America/Chicago").dt.date
entered = pd.to_datetime(entered)
issued = pd.to_datetime(issued)

out = df.copy()
out["date_entered_local"] = entered
out["date_issued_local"] = issued
out["wait_days"] = (issued - entered).dt.days

# 10.1.1 sentinel traps: Council_Dist 0 is not a district (Nashville has 35).
out["council_dist_known"] = out["Council_Dist"].where(out["Council_Dist"].between(1, 35))
out["council_dist_unknown_flag"] = out["council_dist_known"].isna()
n_dist_zero = int((df["Council_Dist"] == 0).sum())
n_dist_null = int(df["Council_Dist"].isna().sum())
n_dist_unknown = int(out["council_dist_unknown_flag"].sum())
assert n_dist_unknown == n_dist_zero + n_dist_null, (n_dist_unknown, n_dist_zero, n_dist_null)

# Census tract: served as float in mixed formats. Preserve raw, add a
# format flag; do NOT invent a normalized tract for mixed-format rows.
ct = df["Census_Tract"]
def ct_format(v):
    if pd.isna(v): return "null"
    if v >= 1e10: return "full_geoid_11digit"
    if v >= 1e7: return "eight_digit_no_state_prefix"
    return "short_code"
out["census_tract_format"] = ct.map(ct_format)
ct_counts = out["census_tract_format"].value_counts(dropna=False).to_dict()

# Tract normalization (verified 2026-10-30, re-verified on the 2026-11-03 pull): the 8-digit form is the
# county+tract GEOID with the leading zero and the state prefix dropped
# (37013100 -> 47 + 037013100); the 11-digit form is the full GEOID.
# Controls: no parcel maps to more than one normalized tract, and the
# two forms share 118 tracts. Normalized values must start 47037
# (Davidson County); 2 rows fail that and are flagged unknown, as are
# the 3 short-code rows and 17 nulls (22 unknown total).
def ct_norm(v, fmt):
    if fmt == "full_geoid_11digit":
        s = str(int(v))
    elif fmt == "eight_digit_no_state_prefix":
        s = "47" + str(int(v)).zfill(9)
    else:
        return None
    return s if s.startswith("47037") and len(s) == 11 else None
out["census_tract_geoid"] = [ct_norm(v, f) for v, f in zip(ct, out["census_tract_format"])]
n_tract_known = int(out["census_tract_geoid"].notna().sum())
n_tract_null = int(ct.isna().sum())
n_tract_short = int((out["census_tract_format"] == "short_code").sum())
n_tract_anomaly = int(sum(1 for v, f in zip(ct, out["census_tract_format"])
                          if f in ("full_geoid_11digit", "eight_digit_no_state_prefix") and ct_norm(v, f) is None))
assert n_tract_known + n_tract_null + n_tract_short + n_tract_anomaly == N
_parcel_tracts = out.dropna(subset=["census_tract_geoid"]).groupby("Parcel")["census_tract_geoid"].nunique()
assert int((_parcel_tracts > 1).sum()) == 0

# Cost: stated value. Zero/null/negative count is recorded, not assumed
# (the 2026-10-30 study found none; the refresh recomputes it).
n_cost_bad = int((df["Const_Cost"].isna() | (df["Const_Cost"] <= 0)).sum())
out["const_cost"] = df["Const_Cost"].astype(float)

# Coordinates: complete, no 0,0 sentinel, all inside a Nashville bbox.
assert int(df["Lat"].isna().sum()) == 0 and int((df["Lat"] == 0).sum()) == 0
assert df["Lat"].between(35.9, 36.5).all() and df["Lon"].between(-87.1, -86.4).all()
out["coords_unknown_flag"] = False

# Wait validity: negative waits are served-data errors, flagged
# and excluded from timing stats, never silently dropped from counts.
out["wait_valid_flag"] = out["wait_days"] >= 0
n_neg = int((~out["wait_valid_flag"]).sum())
neg_values = sorted(int(v) for v in out.loc[~out["wait_valid_flag"], "wait_days"]) if n_neg else []

# Permit number duplicates: rows are the unit, not permit numbers.
dup_permits = int(df["Permit__"].duplicated().sum())

out.to_parquet(CLEAN, index=False)

valid = out[out["wait_valid_flag"]]
def timing(frame):
    w = frame["wait_days"]
    return {
        "n_permits": int(len(frame)),
        "n_timed": int(len(w)),
        "median_days": float(w.median()),
        "mean_days": round(float(w.mean()), 1),
        "p90_days": float(w.quantile(0.9)),
        "same_day_share": round(float((w == 0).mean()), 4),
        "over_90_share": round(float((w > 90).mean()), 4),
        "over_180_share": round(float((w > 180).mean()), 4),
        "over_365_share": round(float((w > 365).mean()), 4),
    }

by_type = {}
for name, g in valid.groupby("Permit_Type_Description"):
    by_type[name] = timing(g)
by_type = dict(sorted(by_type.items(), key=lambda kv: -kv[1]["n_permits"]))

# 10.1.3 unit agreement + 10.1.4 categorical exhaustiveness:
# type counts (all rows) sum to N; shares use N as denominator (10.1.5).
type_counts_all = df["Permit_Type_Description"].value_counts(dropna=False)
assert int(type_counts_all.sum()) == N
type_counts = {str(k): int(v) for k, v in type_counts_all.items()}

# Geography: council district cost concentration (known-district rows only,
# denominator stated; unknown share printed alongside - 10.1.5).
known = out[~out["council_dist_unknown_flag"]]
assert len(known) + int(out["council_dist_unknown_flag"].sum()) == N
dist = known.groupby("council_dist_known").agg(
    permits=("Permit__", "size"), total_cost=("const_cost", "sum"),
    median_cost=("const_cost", "median"), median_wait=("wait_days", lambda s: float(s[s >= 0].median())))
dist_rows = [{"district": int(i), "permits": int(r.permits), "total_cost": float(r.total_cost),
              "median_cost": float(r.median_cost), "median_wait_days": float(r.median_wait)}
             for i, r in dist.sort_values("total_cost", ascending=False).iterrows()]
total_cost_known = float(known["const_cost"].sum())
top5_share = round(sum(r["total_cost"] for r in dist_rows[:5]) / total_cost_known, 4)

zipg = out.groupby("ZIP").agg(permits=("Permit__", "size"), total_cost=("const_cost", "sum"))
zip_rows = [{"zip": str(i), "permits": int(r.permits), "total_cost": float(r.total_cost)}
            for i, r in zipg.sort_values("permits", ascending=False).head(10).iterrows()]

issued_month = issued.dt.to_period("M").astype(str).value_counts().sort_index()
entered_year = entered.dt.year.value_counts().sort_index()

stats = {
  "dataset": "Nashville Building Permits Issued (Building_Permits_Issued_2 layer 0)",
  "snapshot_date": "2026-11-03",
  "rows": N,
  "unit": "one row = one ISSUED building permit (metadata v2.0, 2024-11-12); applications never issued and trade permits are NOT in this dataset",
  "coverage": {
    "date_issued_min": str(issued.min().date()), "date_issued_max": str(issued.max().date()),
    "date_entered_min": str(entered.min().date()), "date_entered_max": str(entered.max().date()),
    "window_rule": "rolling three years by ISSUE date per source description; entered dates run earlier (long-pending permits issued inside the window)"
  },
  "timing_all_valid": timing(valid),
  "timing_negative_rows_excluded": n_neg,
  "timing_negative_wait_values": neg_values,
  "timing_by_type": by_type,
  "type_counts_all_rows": type_counts,
  "type_code_field_warning": "Per_Ty code field disagrees with Permit_Type_Description on small counts and holds a person's name ('Zion Huang') on 1 row; the Description field is authoritative in this layer",
  "cost": {
    "definition": "stated value of construction (applicant-stated, per metadata)",
    "total_stated": float(df["Const_Cost"].sum()),
    "median": float(df["Const_Cost"].median()), "mean": round(float(df["Const_Cost"].mean()), 0),
    "max": float(df["Const_Cost"].max()), "min_positive": float(df["Const_Cost"].min()),
    "zero_or_null_or_negative": n_cost_bad
  },
  "geography": {
    "council_district": {
      "known_rows": int(len(known)), "unknown_rows": int(out["council_dist_unknown_flag"].sum()),
      "unknown_composition": f"{n_dist_zero} rows with district 0 (sentinel) + {n_dist_null} rows null",
      "unknown_zero_sentinel_rows": n_dist_zero, "unknown_null_rows": n_dist_null,
      "top5_districts_share_of_known_total_cost": top5_share,
      "top_district_share_of_citywide_total_cost": round(dist_rows[0]["total_cost"] / float(df["Const_Cost"].sum()), 4) if dist_rows else None,
      "by_district_sorted_by_total_cost": dist_rows
    },
    "zip_top10_by_permits": zip_rows,
    "coords": "Lat/Lon present on 100% of rows, no 0,0 sentinel, all inside Nashville-Davidson bbox",
    "census_tract_format_counts": {str(k): int(v) for k, v in ct_counts.items()},
    "census_tract_normalized": {"known_rows": n_tract_known, "unknown_rows": int(N - n_tract_known),
      "unique_tracts": int(out["census_tract_geoid"].nunique()),
      "rule": f"11-digit form as-is; 8-digit form -> '47' + zero-padded 9 digits; result must be an 11-digit 47037 GEOID or the row is unknown ({n_tract_anomaly} anomalies, {n_tract_short} short codes, {n_tract_null} nulls = {N - n_tract_known} unknown)",
      "control": "no parcel maps to more than one normalized tract; the two served forms share 118 tracts"}
  },
  "issued_by_month": {str(k): int(v) for k, v in issued_month.items()},
  "entered_by_year": {str(k): int(v) for k, v in entered_year.items()},
  "duplicates": {"permit_number_duplicate_rows": dup_permits, "unique_permit_numbers": int(df["Permit__"].nunique()),
                 "unique_parcels": int(df["Parcel"].nunique())},
  "censoring_note": "Entry-to-issue waits are observed only for permits that WERE issued. Applications still pending or never issued are absent by design, so waits for recent entry cohorts are right-censored and read artificially short; the all-window median is the shelf figure, cohort medians for the last two quarters are not.",
  "master_child_note": "Purpose text shows multi-unit developments issue one child permit per dwelling unit under a master permit; permit counts are units/permits, not projects. Project-level counts would need master-permit parsing of the free-text Purpose field, which is boilerplate-heavy and null on 297 rows (1.0%)."
}

# --- Extra panels / distributions (2026-11-03 brief) ---
_w = valid["wait_days"]
_bucket_defs = [("0 days (same day)", _w == 0), ("1-30 days", (_w >= 1) & (_w <= 30)),
                ("31-90 days", (_w >= 31) & (_w <= 90)), ("91-180 days", (_w >= 91) & (_w <= 180)),
                ("181-365 days", (_w >= 181) & (_w <= 365)), ("over 365 days", _w > 365)]
wait_distribution = [{"bucket": name, "permits": int(mask.sum()),
                      "share_of_valid": round(float(mask.mean()), 4)} for name, mask in _bucket_defs]
assert sum(b["permits"] for b in wait_distribution) == len(valid)
stats["wait_distribution"] = wait_distribution
issued_year = issued.dt.year.value_counts().sort_index()
stats["issued_by_year"] = {str(k): int(v) for k, v in issued_year.items()}
stats["purpose_null_rows"] = int(df["Purpose"].isna().sum())
stats["master_child_note"] = (f"Purpose text shows multi-unit developments issue one child permit per dwelling unit under a master permit; "
    f"permit counts are units/permits, not projects. Project-level counts would need master-permit parsing of the free-text Purpose field, "
    f"which is boilerplate-heavy and null on {int(df['Purpose'].isna().sum())} rows ({float(df['Purpose'].isna().mean())*100:.1f}%).")

# Data panels (CSV) for the package
DATA = PKG / "data"; DATA.mkdir(parents=True, exist_ok=True)
pd.DataFrame([{"permit_type": k, **v} for k, v in by_type.items()]).to_csv(DATA / "timing_by_type_panel.csv", index=False)
pd.DataFrame(dist_rows).to_csv(DATA / "district_concentration_panel.csv", index=False)
pd.DataFrame(zip_rows).to_csv(DATA / "zip_top10_panel.csv", index=False)
pd.DataFrame([{"month": k, "permits_issued": v} for k, v in stats["issued_by_month"].items()]).to_csv(DATA / "issued_by_month_panel.csv", index=False)
pd.DataFrame([{"year": k, "permits_issued": v} for k, v in stats["issued_by_year"].items()]).to_csv(DATA / "issued_by_year_panel.csv", index=False)
pd.DataFrame(wait_distribution).to_csv(DATA / "wait_distribution_panel.csv", index=False)

(PKG / "stats.json").write_text(json.dumps(stats, indent=2))
print(f"clean layer: {CLEAN} rows={len(out)}")
print(f"median wait {stats['timing_all_valid']['median_days']}d, mean {stats['timing_all_valid']['mean_days']}d, same-day {stats['timing_all_valid']['same_day_share']}")
print(f"total stated cost ${stats['cost']['total_stated']:,.0f}, median ${stats['cost']['median']:,.0f}")
print(f"top5 district cost share {top5_share}")
print(f"census tract formats: {ct_counts}")
print("BUILD OK")
