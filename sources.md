# Source audit: Nashville building permits issued brief (2026-11-03)

Every figure in brief-draft.md, traced to its derivation. Counts were
produced by code/build_stats.py and are stored in stats.json; the
independent recomputation is in data/verify_independent_output.txt
(9 of 9 checks passed); the pre-flight audit is in
data/audit_output.txt and in verification.md. This package is the
publication build of the verified 2026-10-30 shelf-ready study
(hidden_files/nashville-building-permits-study-2026-10-30/),
refreshed with a same-day pull on 2026-11-03.

## The datasets

1. Building permits issued (primary, only dataset used for figures)
- Name: Building Permits Issued (Building_Permits_Issued_2, layer 0), Metro Nashville open data, owner NashvilleOpenData
- ArcGIS item: 2576bfb2d74f418b8ba8c4538e4f729f, endpoint confirmed through the Nashville Hub search API in the 2026-10-30 study, not a guessed URL
- Endpoint used: https://services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Building_Permits_Issued_2/FeatureServer/0
- Pull: 2026-11-03, paginated query ordered by ObjectId at the service maxRecordCount (1,000), 29,651 records in 30 pages; server count confirmed with returnCountOnly before download and equal to the local count. Immutable snapshot: stack/nashville/snapshots/2026-11-03/building_permits_issued_raw.parquet (sha256 782a825f4f1dc1593adf10dbbf56221b988eea49939c525ff31e561f70b8bd0f, in data/pull_log.json).
- Saved copy: the warehouse snapshot above; derived panels in data/ (timing_by_type_panel.csv, district_concentration_panel.csv, zip_top10_panel.csv, issued_by_month_panel.csv, issued_by_year_panel.csv, wait_distribution_panel.csv)
- Fields relied on: Permit__, Permit_Type_Description, Date_Entered, Date_Issued, Const_Cost, Parcel, Council_Dist, Census_Tract, ZIP, Lat, Lon, Purpose (null count and master/child note only), ObjectId. Contact and Address values are carried in the warehouse layer only and are never published.
- Source documentation: Building Permits Issued Metadata v2.0 (2024-11-12), archived as data/source-metadata.pdf. One record = an ISSUED building permit; Date Entered = date applied for; Date Issued = date approved and issued; Construction Cost = stated value of construction; the dataset does NOT contain applications (including ones never issued) or trade permits; coverage is a rolling three years by issue date, updated daily, extracted from ePermits/CityWorks.

2. Decision hooks (verified from records already in this project, 2026-11-03)
- Metro Council special meeting, Thursday, November 5, 2026, 6:30 PM, and associated committee meetings November 4-5, 2026: Nashville.gov news release dated October 2, 2026, "Metro Council to Meet Thursday, November 5 Due to November 3 Election", as cited in the 2026-11-02 Nashville traffic accidents package (sources.md, item 2): Vice Mayor Angie E. Henderson called the special meeting because the November 3, 2026 general election falls on the regular meeting date. The brief asserts no permits item on that meeting's agenda.
- Metro Council Planning and Zoning Committee meeting Wednesday, November 4, 2026: recorded in this project's leads_log.md, in the CHOSEN BY ALEX pick line for this brief (2026-11-02: "Metro Council Planning and Zoning committee Wed Nov 4; special Council meeting Thu Nov 5"). The brief asserts no permits item on that committee's agenda.

3. Official definitions
- Field meanings: Building Permits Issued Metadata v2.0 (item 1 above).
- Permit type names: the layer's own Permit_Type_Description values (29 values, full Counter in data/audit_output.txt). The Description field is authoritative; the Per_Ty code field disagrees on small counts and holds a person's name on 1 row (stats.json: type_code_field_warning).

## Figure-by-figure audit

1. **29,651 issued permits; issued window October 30, 2023 to November 2, 2026; entered June 17, 2020 to October 30, 2026 (America/Chicago)**
   Server count = downloaded rows = 29,651. Date fields read in America/Chicago per the timestamp control (audit). stats.json: rows, coverage.

2. **Timing, all valid: 29,650 timed permits; median 29 days, mean 64.9, p90 166; same-day 754 (2.54 percent); over 90 days 6,060 (20.44 percent); over 180 days 2,629 (8.87 percent); over 365 days 580 (1.96 percent); 1 negative-wait row (-11 days) excluded**
   wait_days = Date_Issued minus Date_Entered in local days, computed by code/build_stats.py; over-threshold counts recomputed from the cleaned layer in the QA pass and equal to the stats shares times 29,650. stats.json: timing_all_valid, timing_negative_rows_excluded, timing_negative_wait_values, wait_distribution (buckets 754 / 14,342 / 8,494 / 3,431 / 2,049 / 580, summing to 29,650); panel: data/wait_distribution_panel.csv.

3. **Wait by type: Tenant Finish Out median 119 days (1,573 timed; over-90 share 58.68 percent); Commercial New 93 (864; 51.16 percent); Commercial Rehab 50 (3,793); Residential New 35 (10,954; 36.94 percent of all 29,651 rows, derived); Residential Addition 22 (3,167); Demolition 14 (2,170 timed of 2,171 rows); Sign 14 (1,989); Residential Rehab 8 (2,430); Tree Removal 0 (325; same-day share 56.31 percent); Commercial Shell 150 (149); Use & Occupancy 111 (389)**
   Permit_Type_Description groups over valid-wait rows. stats.json: timing_by_type, type_counts_all_rows; panel: data/timing_by_type_panel.csv.

4. **Stated value: total $13,227,134,850; median $102,205; mean $446,094; maximum $226,068,759; minimum $1; zero/null/negative count 0**
   Const_Cost as served, applicant-stated per the metadata. Server-side sum and maximum reproduced the snapshot exactly in the independent verifier. stats.json: cost.

5. **Districts: known 29,632 rows, unknown 19 (2 with district 0 + 17 null); District 19: 2,514 permits, $3,148,570,433 stated (= 23.8 percent of the citywide stated total, derived: 3,148,570,433 / 13,227,134,850 = 0.2380), median stated $129,473, median wait 62 days; District 2: $892,808,044 (1,482; wait 49); District 18: $884,661,966 (957; wait 33); District 17: $804,497,673 (1,576; wait 37.5); District 20: $676,523,843 (1,255; wait 36); top 5 districts hold 48.57 percent of the known-district stated total**
   Council_Dist groups over known-district rows (district 0 mapped to unknown as a sentinel; audit 10.1.1). stats.json: geography.council_district; panel: data/district_concentration_panel.csv (all 35 districts).

6. **District 19 mix (QA recomputation, not a builder figure): 68.7 percent of District 19's valid-wait permits are in permit classes whose type description contains "Commercial", against 25.0 percent citywide; within-class District 19 medians: Tenant Finish Out 153 days (572 permits), Commercial Rehab 72 (859), Residential New 52 (148), against citywide class medians 119 / 50 / 35**
   Recomputed from the cleaned warehouse layer during this build's QA pass (method: Permit_Type_Description contains "Commercial"; medians on valid-wait rows with council_dist_known = 19). Recorded in verification.md under QA cross-checks. The district chart prints the 68.7 / 25.0 pair on the graphic.

7. **ZIP leaders: 37207 (2,698 permits, $1,118,501,549 stated), 37209 (2,572, $850,292,830), 37203 (2,398, $2,461,416,239 = 18.6 percent of the citywide stated total, derived)**
   ZIP value groups over all rows. stats.json: geography.zip_top10_by_permits; panel: data/zip_top10_panel.csv.

8. **Census tract: served formats 22,738 eight-digit, 6,893 full 11-digit GEOID, 17 null, 3 short codes; normalized known 29,629 rows (99.93 percent) across 182 unique tracts; unknown 22 (17 null + 3 short codes + 2 anomalies); the two served forms share 118 tracts; no parcel maps to more than one normalized tract**
   Normalization rule and controls in verification.md. stats.json: geography.census_tract_format_counts, geography.census_tract_normalized.

9. **Composition: 51 duplicate permit-number rows; 29,600 unique permit numbers; 20,851 unique parcels; Purpose null on 296 rows (1.0 percent); largest class Building Residential - New, 10,954 of 29,651 rows (36.9 percent)**
   stats.json: duplicates, purpose_null_rows, type_counts_all_rows, master_child_note.

10. **Refresh drift against the 2026-10-30 study: rows 29,661 to 29,651 (-10); all-permit median wait 30 to 29 days; total stated value $13,199,129,583 to $13,227,134,850 (+$28,005,267); issued window rolled from 2023-10-26/2026-10-29 to 2023-10-30/2026-11-02**
    Study figures from hidden_files/nashville-building-permits-study-2026-10-30/stats.json; fresh figures from this package's stats.json.

11. **Hero figure: 119 days**
    Item 3's Tenant Finish Out median (stats.json: timing_by_type), composited from stats.json by code/hero_composite.py; hero-headline.txt carries the same text.
