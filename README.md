# Nashville Building Permits Issued - a Machine Readable data brief

Among the 29,651 building permits issued in Nashville from October 30, 2023 to November 2, 2026, the median time from application entry to issuance was 29 days; Commercial Tenant Finish Out permits (1,573 permits) waited a median of 119 days, and Council District 19 holds $3.15 billion of the $13.23 billion in applicant-stated construction value (23.8 percent) with a median wait of 62 days. All waits are among permits issued in the window; the layer contains no pending or never-issued applications, so no all-applicant wait is computed anywhere in this package. All cost figures are stated value, reported by applicants.

Part of Machine Readable: https://adowlen.github.io/machine-readable/

Repository: https://github.com/adowlen/nashville-building-permits-data-brief

## Contents

- brief-draft.md - the brief (publishable text)
- stats.json - every figure used in the brief, produced by code/build_stats.py from the 2026-11-03 snapshot
- verification.md - methods checklist, Section 10 pre-flight audit record (ALL SECTION 10 GATES PASS), internal controls, independent verifier record (9 of 9 checks passed), and Section 11.3 flags
- verification-ledger-independent.md - the independent verifier's recomputation ledger (summary of data/verify_independent_output.txt)
- reviewer-notes.md - claims most likely challenged, checks not completed, flags
- sources.md - dataset citations and the per-figure source audit
- social-drafts.md - LinkedIn draft (held for a future Friday synthesis under the Friday-only rule; Machine Readable never posts to X)
- hero-headline.txt - the headline figure and story description for the hero illustration
- hero.png - hero graphic (generated illustration in hero_source/hero-art.webp, headline figure composited by code/hero_composite.py over a top gradient scrim, with all text generated from stats.json). Viewed during QA in the publication run: a Nashville commercial corridor, one storefront open and lit in amber with its permit posted in the window, the same kind of storefront in teal still papered over with chairs stacked inside, headline and source line fully legible on the scrimmed dark field
- charts/ - chart_wait_by_type.png, chart_district_stated_value.png, chart_wait_distribution.png, chart_district_median_wait.png
- data/ - pull_log.json, audit_output.txt, verify_independent_output.txt, verify_independent_output.json, source-metadata.pdf (Building Permits Issued Metadata v2.0), timing_by_type_panel.csv, district_concentration_panel.csv, zip_top10_panel.csv, issued_by_month_panel.csv, issued_by_year_panel.csv, wait_distribution_panel.csv. The raw snapshot itself is the warehouse file stack/nashville/snapshots/2026-11-03/building_permits_issued_raw.parquet in the project stack (immutable; sha256 in data/pull_log.json), and code/build_stats.py also writes the cleaned layer to stack/nashville/layers/building_permits_issued_clean.parquet
- code/ - pull_data.py, build_stats.py, audit_section10.py, verify_independent.py, charts.py, hero_composite.py

## Dependencies (match code imports)

Python standard library (hashlib, json, pathlib, statistics, sys, time); matplotlib; numpy; pandas; Pillow; pyarrow; requests.

## Reuse and citation

Licensed CC-BY-4.0 (see LICENSE). Cite as: Machine Readable, "Nashville building permits: among permits issued in the last three years, the median entry-to-issue wait was 29 days, and a Commercial Tenant Finish Out permit waited a median of 119 days" (2026), https://github.com/adowlen/nashville-building-permits-data-brief
