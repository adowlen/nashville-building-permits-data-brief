#!/usr/bin/env python3
"""Section 10 pre-flight audit for the Nashville building permits layer.
Reads the cleaned layer + stats.json; asserts every gate; prints evidence.
"""
import json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve()
PKG = HERE.parents[1]
STACK = HERE.parents[2] / "stack" / "nashville"
clean = pd.read_parquet(STACK / "layers" / "building_permits_issued_clean.parquet")
stats = json.loads((PKG / "stats.json").read_text())
N = len(clean)
print(f"rows in cleaned layer: {N}")
assert N == stats["rows"]

# 10.1.1 zero/null sentinel traps
z = int((clean["Council_Dist"] == 0).sum())
unk = int(clean["council_dist_unknown_flag"].sum())
exp_zero = stats["geography"]["council_district"]["unknown_zero_sentinel_rows"]
exp_unk = stats["geography"]["council_district"]["unknown_rows"]
assert z == exp_zero and unk == exp_unk and int(clean["council_dist_known"].between(1, 35).sum()) == N - unk
assert int((clean["Const_Cost"] <= 0).sum()) + int(clean["Const_Cost"].isna().sum()) == stats["cost"]["zero_or_null_or_negative"]
assert int(clean["coords_unknown_flag"].sum()) == 0
print(f"[10.1.1] Council_Dist 0-sentinel rows: {z} mapped unknown; district unknown total {unk} ({z} zero + {unk - z} null); cost zero/null/negative = {stats['cost']['zero_or_null_or_negative']}; coords complete, no 0,0 PASS")

# 10.1.2 boolean polarity: wait_valid_flag sample check
neg = clean[~clean["wait_valid_flag"]]
assert len(neg) == stats["timing_negative_rows_excluded"]
assert sorted(int(v) for v in neg["wait_days"]) == stats["timing_negative_wait_values"]
same_day = clean[clean["wait_valid_flag"] & (clean["wait_days"] == 0)]
print(f"[10.1.2] wait_valid polarity: {len(neg)} excluded row(s) are the negative served wait(s) {stats['timing_negative_wait_values']}; matched-vs-excluded sample - excluded: {neg[['Permit_Type_Description', 'wait_days']].head(3).values.tolist()}; matched same-day sample: {same_day[['Permit_Type_Description', 'wait_days']].head(3).values.tolist()}; same-day rows in valid set: {len(same_day)} PASS")

# 10.1.3 numerator/denominator unit agreement: timing shares are permits/permits
t = stats["timing_all_valid"]
assert t["n_timed"] == N - stats["timing_negative_rows_excluded"]
recomputed_same_day = float((clean.loc[clean["wait_valid_flag"], "wait_days"] == 0).mean())
assert abs(recomputed_same_day - t["same_day_share"]) < 0.0001
print(f"[10.1.3] timing denominator = {t['n_timed']} valid permits of {N} rows; same-day share recomputed {recomputed_same_day:.4f} PASS")

# 10.1.4 categorical exhaustiveness: full Counter of type field sums to N
cnt = clean["Permit_Type_Description"].value_counts(dropna=False)
assert int(cnt.sum()) == N and len(cnt) == len(stats["type_counts_all_rows"])
assert {str(k): int(v) for k, v in cnt.items()} == stats["type_counts_all_rows"]
print(f"[10.1.4] Permit_Type_Description Counter: {len(cnt)} values, counts sum to {N}, matches stats.json exactly PASS")

# 10.1.5 nullable denominator: district known + unknown = whole
known = int((~clean["council_dist_unknown_flag"]).sum())
assert known + unk == N
tk = int(clean["census_tract_geoid"].notna().sum())
assert tk == stats["geography"]["census_tract_normalized"]["known_rows"] and N - tk == stats["geography"]["census_tract_normalized"]["unknown_rows"]
wd = stats["wait_distribution"]
assert sum(b["permits"] for b in wd) == t["n_timed"]
print(f"[10.1.5] district known {known} + unknown {unk} = {N}; tract known {tk} + unknown {N-tk} = {N}; wait buckets sum to {t['n_timed']} PASS")

# 10.2 controls
hrs_ok = True
for c in ["Date_Entered", "Date_Issued"]:
    hrs = set(pd.to_datetime(clean[c], unit="ms", utc=True).dt.hour.unique())
    hrs_ok &= hrs <= {5, 6}
assert hrs_ok
pt = clean.dropna(subset=["census_tract_geoid"]).groupby("Parcel")["census_tract_geoid"].nunique()
assert int((pt > 1).sum()) == 0
tree = stats["timing_by_type"]["Building Tree Removal Permit"]
assert tree["median_days"] == 0.0
print(f"[10.2] controls: (a) both date fields carry only UTC hours 5/6 = America/Chicago midnights, so local-date reads are correct; (b) no parcel maps to more than one normalized census tract; (c) simple-permit control: Tree Removal median wait {tree['median_days']} days on {tree['n_permits']} permits (same-day share {tree['same_day_share']}), so long commercial waits are not a uniform queue artifact PASS")

# 12.3 censoring print
print(f"[12.3] effective window: issued {stats['coverage']['date_issued_min']} to {stats['coverage']['date_issued_max']}; entered dates run back to {stats['coverage']['date_entered_min']} (issued-only dataset: pending/never-issued applications are absent, recent entry cohorts are right-censored) PASS")
print("ALL SECTION 10 GATES PASS")
