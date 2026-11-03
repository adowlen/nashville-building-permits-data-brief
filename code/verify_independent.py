#!/usr/bin/env python3
"""Independent verifier (Section 11 method diversity).
Two implementations sharing no code with the builder:
 (1) server-side ArcGIS groupBy/statistics queries against the live service;
 (2) a pyarrow recount of the raw snapshot (no pandas).
Compares both against stats.json. Prints PASS/FAIL per check.
"""
import json
from pathlib import Path
import pyarrow.parquet as pq
import pyarrow.compute as pc
import requests

HERE = Path(__file__).resolve()
PKG = HERE.parents[1]
STACK = HERE.parents[2] / "stack" / "nashville"
BASE = "https://services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Building_Permits_Issued_2/FeatureServer/0"
stats = json.loads((PKG / "stats.json").read_text())
checks = []

def check(name, ok, detail=""):
    checks.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")

# --- (1) server-side ---
def q(params):
    params = dict(params)
    if "outStatistics" in params:
        params["outStatistics"] = json.dumps(params["outStatistics"])
    r = requests.get(BASE + "/query", params=params, timeout=120)
    r.raise_for_status()
    d = r.json()
    if "error" in d:
        raise RuntimeError(d["error"])
    return d

live = q({"where": "1=1", "returnCountOnly": "true", "f": "json"})["count"]
check("server count (note: live service rolls daily; drift-tolerant)",
      abs(live - stats["rows"]) <= 1000, f"live now {live} vs snapshot {stats['rows']}")

d = q({"where": "1=1", "groupByFieldsForStatistics": "Permit_Type_Description",
       "outStatistics": [{"statisticType": "count", "onStatisticField": "ObjectId", "outStatisticFieldName": "n"}],
       "orderByFields": "n DESC", "f": "json"})
server_types = {f["attributes"]["Permit_Type_Description"]: f["attributes"]["n"] for f in d["features"]}
same = {k: v for k, v in server_types.items() if stats["type_counts_all_rows"].get(k) == v}
check("server groupBy type counts reproduce snapshot counts for unchanged types",
      len(same) >= 25, f"{len(same)}/{len(server_types)} types match the snapshot exactly (rolling window shifts the rest)")

d = q({"where": "1=1", "outStatistics": [
    {"statisticType": "sum", "onStatisticField": "Const_Cost", "outStatisticFieldName": "tot"},
    {"statisticType": "max", "onStatisticField": "Const_Cost", "outStatisticFieldName": "mx"}], "f": "json"})
a = d["features"][0]["attributes"]
check("server max stated cost is at least the snapshot max (window rolls)",
      float(a["mx"]) >= stats["cost"]["max"], f"server max {a['mx']:,.0f} vs stats {stats['cost']['max']:,.0f} (total legitimately shifts as the window rolls: server now {a['tot']:,.0f})")

# --- (2) pyarrow recount of the raw snapshot ---
t = pq.read_table(STACK / "snapshots" / "2026-11-03" / "building_permits_issued_raw.parquet")
check("pyarrow row count", t.num_rows == stats["rows"], f"{t.num_rows}")
cost = t.column("Const_Cost").to_pylist()
check("pyarrow cost total",
      sum(cost) == int(stats["cost"]["total_stated"]),
      f"sum {sum(cost):,} (stats {int(stats['cost']['total_stated']):,})")
import statistics as st
med = st.median(cost)
check("pyarrow cost median exact", med == stats["cost"]["median"], f"{med:,.0f}")
ent = t.column("Date_Entered").to_pylist(); iss = t.column("Date_Issued").to_pylist()
waits = sorted((i - e) // 86400000 for e, i in zip(ent, iss) if i >= e)
check("pyarrow wait median (epoch-day arithmetic, independent of builder tz path)",
      st.median(waits) == stats["timing_all_valid"]["median_days"], f"median {st.median(waits)} days over {len(waits)} valid rows")
neg = sum(1 for e, i in zip(ent, iss) if i < e)
check("pyarrow negative waits", neg == stats["timing_negative_rows_excluded"], f"{neg}")
obj = t.column("ObjectId").to_pylist()
check("pyarrow ObjectId unique", len(set(obj)) == len(obj), f"{len(set(obj))} unique")

fails = [c for c in checks if not c[1]]
print(f"\n{len(checks) - len(fails)}/{len(checks)} checks pass")
if fails:
    raise SystemExit(1)
