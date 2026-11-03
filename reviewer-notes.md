# Reviewer notes - Nashville building permits issued brief (2026-11-03)

## Claims most likely to be challenged

- Headline 119 days (median entry-to-issue wait for Commercial Tenant
  Finish Out among issued permits, 1,573 permits). Pressure point,
  printed in the brief: this is a median over permits that were
  issued. Applications still pending or never issued are not in the
  dataset, so the figure is not "how long a tenant finish-out
  application takes" in general; it is the median completed wait for
  the issued population. The framing phrase "among permits issued in
  the window" appears in the title, the one-line finding, the
  definitions, the findings, the chart titles, and the hero sub-line.
- District 19 (62-day median wait; $3.15B stated, 23.8 percent of the
  citywide stated total). The mix alternative is printed in Finding 4
  itself: 68.7 percent of District 19's permits are commercial classes
  against 25.0 percent citywide, and commercial classes wait longer
  everywhere. The within-class medians (Tenant Finish Out 153 vs 119;
  Commercial Rehab 72 vs 50; Residential New 52 vs 35) are printed
  alongside, labeled unadjusted for stated value, size, and subtype.
  A reader who quotes the 62 days as a processing finding for the
  district is going past the package; the package does not make that
  claim.
- The $13.23 billion stated total. It is applicant-reported
  construction value from the permit records, labeled "stated value"
  every time it appears, including on the charts ("reported by
  applicants, not measured"). The single $226,068,759 maximum permit
  is printed only next to the $102,205 median.
- The 29-day citywide median (study: 30 days). The refresh moved it
  by one day as the rolling window shifted four days; the drift is
  recorded in sources.md (item 10) so a reader comparing the two
  packages sees the same method on two snapshots, not a changed
  method.

## Checks that could not be completed

- Mix-adjusted district waits (adjusting District 19's median for
  permit class, stated value, and subtype together): not computed.
  The brief prints the unadjusted medians, the mix shares, and the
  within-class medians, and states what a fuller adjustment would
  need. The shelf-ready study flagged a mix adjustment as a pick-time
  option; the within-class table in Finding 4 is the partial version
  this build ships.
- Pending-application waits: not computable from this dataset by
  design (applications are a different dataset, out of scope per the
  shelf-ready framing rules). No figure in the brief needs it, and the
  missing denominator is stated prominently.
- Project-level counts: not computed. Master/child structure is
  visible in Purpose text but project counts would need free-text
  master-permit parsing (Purpose is null on 296 rows and
  boilerplate-heavy); the brief counts permits/units and says so.
- Tract-level findings: the normalization is verified (29,629 of
  29,651 rows on a Davidson County GEOID) and the cleaned layer ships
  in the warehouse, but this brief publishes no tract-level figure;
  a tract map is a follow-on the data now supports.

## Findings that surprised us

- The wait structure is class-shaped to an unusual degree inside one
  layer and one window: Tree Removal issues at a median of 0 days
  (56.3 percent same-day) while Commercial Shell sits at a median of
  150 days and Tenant Finish Out at 119 - the simple-permit control
  rules out a single uniform queue as the explanation.
- District 19's within-class medians are above the citywide class
  medians in all three classes checked at QA, even though its mix
  (68.7 percent commercial) explains much of the raw 62-vs-29 gap.
  Both facts are printed; the package does not adjudicate between
  size/subtype composition inside classes and processing differences.
- The refresh drift was small but not one-directional: 10 fewer
  permits than the study snapshot, a 1-day lower median wait, and
  $28.0 million more stated value, because the rolling window dropped
  late-October 2023 days and added late-October/early-November 2026
  days at once.

## Flags

- This brief's findings concern a permit population and a public
  dataset's fields. No agency, department, or official is named as a
  finding subject; Metro Codes Administration and the Metropolitan
  Council appear only in the Who can act section as lever owners
  (standards section 11.3 flag, carried from the study).
- First publication build of the Building Permits Issued layer
  (verified as a study layer on 2026-10-30): flagged as a first-use
  dataset under standards section 11.3.
- The November 4 Planning and Zoning Committee date rests on this
  project's own leads_log.md pick line (2026-11-02); the November 5
  special meeting rests on the Nashville.gov October 2, 2026 news
  release as cited in the 2026-11-02 package. No agenda item is
  asserted for either.
- Hero: COMPLETED and VIEWED in the publication run (2026-11-03).
  Generated illustration in the brand palette (a Nashville commercial
  corridor: one storefront open and lit in amber with its permit
  posted in the window, the same kind of storefront in teal still
  papered over with chairs stacked inside and a blank coming-soon
  sign), composited by code/hero_composite.py over a top gradient
  scrim with all hero text generated from stats.json. Viewed during
  QA: headline (119 days), sub-line, and source line fully legible on
  the scrimmed dark field; narrative scene unobscured.
- Charts: all four were viewed after the final render. The first
  render clipped the District 19 label on the stated-value chart and
  a subtitle on the district median-wait chart; both were fixed in
  code/charts.py, re-rendered, and re-viewed clean (verification.md,
  adversarial note A7).
