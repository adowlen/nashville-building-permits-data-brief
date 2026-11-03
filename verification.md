# Verification - Nashville building permits issued brief (2026-11-03)

This package is the publication build of the verified 2026-10-30
shelf-ready study (hidden_files/nashville-building-permits-study-2026-10-30/),
refreshed with a same-day pull on 2026-11-03. Builder pass, Section 10
pre-flight audit, and independent verifier pass (Section 11 method
diversity) were all re-run on the new snapshot in this build. Refresh
adaptation: the study code's exact-count assertions were replaced with
computed values recorded in stats.json and relationship assertions
(known + unknown = whole, Counter sums, bucket sums), so the gates test
structure on the new data rather than inheriting the 2026-10-30 counts.
Every adaptation is commented in the code files.

## Source verification (before any computation)

- Endpoint (live, queried 2026-11-03):
  `services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Building_Permits_Issued_2/FeatureServer/0`
  ("Building Permits Issued", ArcGIS item 2576bfb2d74f418b8ba8c4538e4f729f,
  owner NashvilleOpenData), confirmed through the Nashville Hub in the
  2026-10-30 study, not a guessed URL.
- Live count at pull: **29,651** (29,661 at the 2026-10-30 study pull;
  drift -10 in four days, consistent with a daily rolling window).
  Pulled in 30 pages of 1,000 (the service's maxRecordCount), ObjectId
  order; pulled count asserted equal to live count; ObjectId unique on
  all rows. Immutable snapshot:
  stack/nashville/snapshots/2026-11-03/building_permits_issued_raw.parquet
  (sha256 782a825f4f1dc1593adf10dbbf56221b988eea49939c525ff31e561f70b8bd0f,
  in data/pull_log.json).
- Fields as served (22): Permit__, Permit_Type_Description,
  Permit_Subtype_Description, Parcel, Date_Entered, Date_Issued,
  Const_Cost, Address, City, State, Subdivision_Lot, Contact, Per_Ty,
  Per_SubTy, IVR_Trk_, Purpose, Council_Dist, Census_Tract, Lon, Lat,
  ObjectId, ZIP.
- Source documentation read: Building Permits Issued Metadata v2.0
  (2024-11-12, archived in this package as data/source-metadata.pdf).
  One record = an ISSUED building permit; Date Entered = date applied
  for; Date Issued = date approved and issued; Construction Cost =
  stated value of construction; the dataset does NOT contain
  applications (including ones never issued) or trade permits; coverage
  is a rolling three years by issue date, updated daily, extracted from
  ePermits/CityWorks.

## Headline figures (all verified below)

- 29,651 issued permits, issued 2023-10-30 to 2026-11-02 (the rolling
  three-year window, keyed on issue date). Entered dates run back to
  2020-06-17: long-pending permits issued inside the window.
- Entry-to-issue wait (29,650 valid rows): median **29 days**, mean
  64.9, p90 166; same-day 2.54% (754 permits); over 90 days 20.44%
  (6,060 permits); over 180 days 8.87%; over 365 days 1.96%. One served
  row has a negative wait (-11 days, a Building Demolition Permit):
  flagged and excluded from timing, counted here.
- Wait by type (median, timed permits): Tree Removal 0 days (325);
  Commercial Tenant Finish Out **119 days** (1,573); Commercial New 93
  (864); Commercial Rehab 50 (3,793); Residential New 35 (10,954);
  Residential Addition 22 (3,167). Commercial Shell records the highest
  median at 150 days but on 149 permits.
- Stated construction value: **$13,227,134,850** total across the
  window; median permit $102,205; mean $446,094; single maximum
  $226,068,759; no zero, null, or negative stated values. Cost is
  applicant-stated (metadata), never audited figures.
- Geography: Council District 19 holds 2,514 permits and $3.15B of
  stated value (23.8% of the citywide stated total) with a median wait
  of 62 days, about double the citywide median of 29 days. The top 5
  districts by stated value hold 48.57% of the known-district stated
  total. District is known on 29,632 rows (unknown: 2 rows with
  district 0, 17 null).
- Composition: largest type is Building Residential - New, 10,954
  permits (36.9%). Permit counts are per-unit: multi-unit developments
  issue one child permit per dwelling unit under a master permit
  (visible in Purpose text, null on 296 rows, 1.0%), so counts are
  permits/units, not projects.

## Methods checklist (brief-writing standards, section 3)

- Base rates and exposure: **no pending-application denominator exists
  in this dataset.** The metadata states the dataset does not contain
  applications, including ones never issued, so there is no base of all
  applications against which an issuance rate or an all-applicant wait
  could be computed. Every figure is a count, a median, or a share
  among permits issued in the window, on a named population, and the
  brief states the missing denominator prominently in its definitions,
  in Finding 1's framing, and in Data notes. No causal pattern is
  implied.
- Direction of causality: the district comparison (Finding 4) is
  printed unadjusted with its composition alternative in the same
  finding and in "What this might mean"; no claim is made that a
  district causes a wait, or that processing pace causes the mix.
- Category and definition changes: full Counter of
  Permit_Type_Description recorded before any computation (29 values,
  summing to 29,651; audit output). No rename or definition change
  inside the window is documented in the metadata (v2.0, 2024-11-12).
  The Per_Ty code field's disagreement with the Description field is
  recorded as a field-quality note, and no figure uses the code field.
- Time windows: exact range stated in the brief: issued 2023-10-30 to
  2026-11-02 (America/Chicago), the layer's rolling three years by
  issue date. No plan or program comparison crosses a period in which
  it was not in effect; the November 4-5, 2026 Council items in the Who
  can act section are forward-looking and no agenda item is asserted.
- Joins: no dataset join is used. Geography is the layer's own
  district and ZIP fields. The one transformation is the census tract
  normalization, a within-layer field repair, with its match rate
  printed: 29,629 of 29,651 rows (99.93%) carry a normalized Davidson
  County GEOID; 22 rows are unknown (17 null, 3 short codes, 2
  anomalies). The unmatched rows are 0.07% of the layer and cannot
  differ systematically at a scale that moves any figure in this brief;
  no tract-level figure is published in this brief in any case.
- Small numbers: percentages carry counts throughout. Classes under
  about 30 timed permits (smallest: Building Moving Permit, 3) sit in
  the data panels with counts and are used in no finding; the smallest
  class cited in a finding is Commercial Shell at 149 permits, printed
  with its count. District 19's within-class Residential New median
  (52 days) rests on 148 permits, printed with its count.
- Official definitions: field meanings are the metadata's own,
  cited in sources.md.
- Layering admission test: no layer was added in this refresh. The
  brief's claims are all makeable from the permits layer alone; the
  tract normalization is a repair of the layer's own field, admitted
  because it makes the tract claim in Finding 3 (tract tabulation is
  reproducible) that could not be made from the raw mixed-format field.

## Pre-flight audit

Script: code/audit_section10.py (run on the final pull, before charts
and prose were finalized). Full output (also in data/audit_output.txt):

```
rows in cleaned layer: 29651
[10.1.1] Council_Dist 0-sentinel rows: 2 mapped unknown; district unknown total 19 (2 zero + 17 null); cost zero/null/negative = 0; coords complete, no 0,0 PASS
[10.1.2] wait_valid polarity: 1 excluded row(s) are the negative served wait(s) [-11]; matched-vs-excluded sample - excluded: [['Building Demolition Permit', -11]]; matched same-day sample: [['Building Residential - Rehab', 0], ['Building Tree Removal Permit', 0], ['Building Tree Removal Permit', 0]]; same-day rows in valid set: 754 PASS
[10.1.3] timing denominator = 29650 valid permits of 29651 rows; same-day share recomputed 0.0254 PASS
[10.1.4] Permit_Type_Description Counter: 29 values, counts sum to 29651, matches stats.json exactly PASS
[10.1.5] district known 29632 + unknown 19 = 29651; tract known 29629 + unknown 22 = 29651; wait buckets sum to 29650 PASS
[10.2] controls: (a) both date fields carry only UTC hours 5/6 = America/Chicago midnights, so local-date reads are correct; (b) no parcel maps to more than one normalized census tract; (c) simple-permit control: Tree Removal median wait 0.0 days on 325 permits (same-day share 0.5631), so long commercial waits are not a uniform queue artifact PASS
[12.3] effective window: issued 2023-10-30 to 2026-11-02; entered dates run back to 2020-06-17 (issued-only dataset: pending/never-issued applications are absent, recent entry cohorts are right-censored) PASS
ALL SECTION 10 GATES PASS
```

## Internal controls (Section 10.2)

1. **Timestamp control.** Both date fields carry only UTC hours 5 and
   6 - America/Chicago midnights in CDT and CST. The served epochs are
   local dates; every date figure in stats.json is read in
   America/Chicago.
2. **Tract consistency control.** The served Census_Tract float mixes
   formats (8-digit on 22,738 rows, full 11-digit GEOID on 6,893,
   short codes on 3, null on 17). After the documented normalization
   (8-digit form is county+tract with the leading zero and state
   prefix dropped), no parcel maps to more than one tract and the two
   forms share 118 tracts. 29,629 rows carry a normalized 47037 GEOID;
   22 rows are unknown (17 null, 3 short codes, 2 anomalies that do
   not resolve to a Davidson County GEOID).
3. **Simple-permit control.** Tree Removal permits (a simple,
   low-review class) issue at a median of 0 days (325 permits, 56.31%
   same-day), so the long waits in commercial classes are not a uniform
   system-wide queue artifact.

## Independent verifier (Section 11)

Script: code/verify_independent.py (carried from the 2026-10-30 study,
where it was written as a separate pass sharing no code with the
builder; in this refresh its snapshot path was pointed at the
2026-11-03 snapshot and its server-side checks were made
drift-tolerant, with expected values read from the new stats.json).
Full output in data/verify_independent_output.txt. **9/9 checks pass.**
Two implementations sharing no code with the builder: (1) server-side
ArcGIS groupBy/statistics - live count 29,651 at verify time (equal to
the snapshot, zero drift), all 29 type counts reproduced exactly,
server maximum stated cost $226,068,759 and server total
$13,227,134,850 match the snapshot exactly; (2) a pyarrow recount of
the raw snapshot - row count, cost total and median, the 29-day wait
median recomputed by raw epoch-day arithmetic (independent of the
builder's timezone path), the single negative wait, ObjectId
uniqueness.

## QA cross-checks run during this build (beyond the trio)

Recomputed from the cleaned layer at QA time, because the brief
carries them in Finding 4 and on the district median-wait chart:
District 19's commercial-class share is 68.7% of its valid-wait
permits (permit type descriptions containing "Commercial") against
25.0% citywide; District 19 within-class medians are Tenant Finish
Out 153 days (572 permits), Commercial Rehab 72 (859), Residential
New 52 (148), against citywide class medians of 119, 50, and 35 days.
Over-threshold counts were also recomputed: over 90 days 6,060
permits, over 180 days 2,629, over 365 days 580, same-day 754, each
equal to the corresponding stats.json share of 29,650. Every number
in brief-draft.md was cross-checked against the final stats.json in
the same pass.

## Adversarial notes (self-check against the standards)

- **A1 Issuance conditioning (the big one).** Every wait in this layer
  is a wait among permits that were issued. Applications still pending
  or never issued are absent by design (the separate Building Permit
  Applications dataset is a different population). The brief says
  "among permits issued in the window" in its title, one-line finding,
  definitions, findings, chart titles, and hero sub-line, and never
  describes these figures as how long applicants in general wait.
- **A2 Right-censoring.** Permits entered in recent quarters and
  already issued are a fast-selected subset; cohort medians for recent
  entry quarters would read artificially short. stats.json records
  this; the brief uses all-window and by-type medians only.
- **A3 Stated cost.** Const_Cost is what the applicant stated. The
  $13.2B total and district shares are stated-value shares, labeled
  "stated value" and "applicant-reported" every time they appear,
  including on the charts; the single $226M maximum is never headlined
  without the $102,205 median beside it.
- **A4 Code-field junk.** Per_Ty disagrees slightly with the
  Description counts and holds a person's name on 1 row; Per_SubTy
  showed 174 values against the Description's 171 in the study.
  Description fields are authoritative in this layer; code fields are
  carried raw and flagged in stats.json. The name itself appears
  only inside that stats.json field warning (inherited verbatim from
  the study, where it serves as the field-quality evidence); it
  appears in no brief prose, chart, or panel in this package.
- **A5 Per-unit counting.** See Finding 5: a 100-unit development can
  be 100 rows. Comparisons are valid as permit activity, not as
  project counts, and the brief says so in its definitions.
- **A6 Contact field.** Carried in the warehouse layer as served
  (public record); contractor/contact names and street addresses are
  never published from this layer under the project's
  no-personal-contact-data rule. This package publishes none.
- **A7 Hero and charts.** All four charts were viewed after the final
  render. The first render clipped the District 19 label on the
  stated-value chart and the subtitle on the district median-wait
  chart; both were fixed in code/charts.py and re-rendered, then
  re-viewed clean. The hero illustration is generated and composited
  by the parent run (code/hero_composite.py + hero-headline.txt ship
  in this package); the hero figure (119 days) is generated from
  stats.json by the composite script, so it cannot drift from the
  stats.

## Sync gate (section 10.3)

- README dependency list matches code imports: pull_data.py
  (requests, pandas, stdlib), build_stats.py (pandas, numpy, stdlib),
  audit_section10.py (pandas, stdlib), charts.py (matplotlib, stdlib),
  verify_independent.py (pyarrow, requests, stdlib),
  hero_composite.py (Pillow, stdlib). README lists exactly: Python
  standard library, matplotlib, numpy, pandas, Pillow, pyarrow,
  requests. No geopandas or shapely anywhere.
- Every number in brief-draft.md cross-checks against the final
  stats.json: figures were taken from stats.json at drafting, the
  District 19 mix claims were recomputed from the cleaned layer in
  the QA pass recorded above, and the hero's text is generated from
  stats.json by code/hero_composite.py. hero-headline.txt carries the
  same text.
- Review adjudication: the only review text inherited into this
  package is the 2026-10-30 study's verification record, which was
  read in full (verification.md and SHELF-READY.md) and whose figures
  were recomputed rather than inherited - the refresh's drift (-10
  rows, median wait 30 to 29 days, stated total +$28,005,267) is
  recorded in sources.md, item 10.

## Section 11.3 exception flags

- Findings touch the Metro Codes Administration lever only in the Who
  can act section - no agency, department, or official is named as a
  finding subject; the findings are about the permit population.
  District 19's longer median wait is a geographic fact about permit
  mix at least as plausibly as about processing, and the brief prints
  that alternative in the finding itself.
- This dataset's first publication use was prepared as a verified
  study on 2026-10-30; this brief is its first publication build:
  flagged as a first-use dataset under standards section 11.3,
  carried from the study.
- Surprising finding (carried from the study, unchanged on the
  refresh): the simple-permit control (Tree Removal, median 0 days)
  sits in the same layer and the same window as a 119-day median for
  tenant finish-out, so the wait structure is class-shaped, not a
  single queue.
- Nothing here touches the portfolio or any standing guardrail.
