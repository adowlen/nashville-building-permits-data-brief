# Independent verification ledger - Nashville building permits issued brief (2026-11-03)

Verifier: code/verify_independent.py (Section 11 pass; implementation
shares no code with the builder - a pyarrow recount of the raw
snapshot plus live server-side ArcGIS queries; carried from the
2026-10-30 study with its snapshot path pointed at the 2026-11-03
snapshot and its server checks made drift-tolerant against the new
stats.json). Run: 2026-11-03, against the 2026-11-03 snapshot
(29,651 rows) and the live layer (29,651 rows at verify time, drift
0). Full output: data/verify_independent_output.txt.

## Result

**9 of 9 checks passed. No discrepancies. No figure corrected by
the verifier; no figure caveated beyond the caveats already in the
brief.**

## What was reproduced

- Method A (live ArcGIS server-side, 3 checks): live total 29,651,
  identical to the snapshot; server groupBy type counts reproduce all
  29 of 29 Permit_Type_Description counts in stats.json exactly;
  server maximum stated cost $226,068,759 equals the snapshot maximum,
  and the server stated total at verify time was $13,227,134,850,
  identical to the snapshot total.
- Method B (pyarrow recount of the raw snapshot, 6 checks): row count
  29,651; stated cost total $13,227,134,850, equal to stats.json;
  stated cost median $102,205, exact; wait median 29.0 days over
  29,650 valid rows, recomputed by raw epoch-day arithmetic
  (independent of the builder's America/Chicago timezone path);
  negative waits 1, matching stats.json; ObjectId unique on all
  29,651 rows.

## Documented limitation (from the verifier design)

The verifier's server-side checks are drift-tolerant by design: the
layer rolls daily, so a verify run hours after the pull could
legitimately see small count changes. On this run there was no drift
to tolerate - the live layer matched the snapshot exactly on the
count, all 29 type counts, the maximum, and the stated total - so
every server check passed on exact equality.
