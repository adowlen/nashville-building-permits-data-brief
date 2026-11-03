"""Data-drawn charts for the Nashville building permits brief (2026-11-03).
Brand palette: dark charcoal, amber, teal. Every chart prints its
population, measure, and scope labels on the graphic itself (framing
standard): all wait figures are among permits ISSUED in the window;
all cost figures are applicant-stated value, labeled as reported.

Layout: titles and footnotes are figure-level text with fixed axes
margins (no tight_layout), so no footnote can clip or overlap an axis.
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
stats = json.loads((ROOT / "stats.json").read_text())
CH = ROOT / "charts"
CH.mkdir(exist_ok=True)
CHARCOAL = "#23272b"; AMBER = "#f5a800"; TEAL = "#2a9d8f"; GREY = "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": CHARCOAL,
                     "axes.edgecolor": CHARCOAL, "axes.labelcolor": CHARCOAL,
                     "xtick.color": CHARCOAL, "ytick.color": CHARCOAL})
SNAP = stats["snapshot_date"]
ROWS = stats["rows"]
WMIN = stats["coverage"]["date_issued_min"]
WMAX = stats["coverage"]["date_issued_max"]
NTIMED = stats["timing_all_valid"]["n_timed"]
FOOT = (f"Source: Nashville Building Permits Issued layer (Building_Permits_Issued_2), pulled {SNAP}; {ROWS:,} permits issued {WMIN} to {WMAX}.\n"
        "Waits are entry-to-issue days among permits issued in the window only; applications still pending or never issued are not in this dataset.")


def frame(fig, title, foot, top=0.80, bottom=0.17, left=0.09, right=0.985):
    fig.text(0.012, 0.975, title, fontsize=10.5, va="top", ha="left")
    fig.text(0.012, 0.012, foot, fontsize=7.5, color=GREY, va="bottom", ha="left")
    fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right)


def save(fig, name):
    fig.savefig(CH / name, dpi=200, facecolor="white")
    plt.close(fig)
    print(name)


def short(name):
    return (name.replace("Building ", "").replace(" - ", " - "))


# (a) Median wait by permit type (types with at least 250 timed permits)
by_type = stats["timing_by_type"]
rows_a = [(k, v) for k, v in by_type.items() if v["n_timed"] >= 250]
rows_a.sort(key=lambda kv: kv[1]["median_days"])
fig, ax = plt.subplots(figsize=(9.5, 5.8))
ax.barh([short(k) for k, _ in rows_a], [v["median_days"] for _, v in rows_a],
        color=[AMBER if k == "Building Commercial - Tenant Finish Out" else TEAL for k, _ in rows_a])
for i, (k, v) in enumerate(rows_a):
    ax.text(v["median_days"] + 3, i, f"{v['median_days']:.0f} days (n = {v['n_timed']:,})",
            va="center", fontsize=8.5)
ax.set_xlim(0, max(v["median_days"] for _, v in rows_a) * 1.45)
ax.set_xlabel("Median days from application entry to issuance")
ax.spines[["top", "right"]].set_visible(False)
frame(fig,
      "Median entry-to-issue wait by permit type - among permits issued in the window\n"
      f"Population: {NTIMED:,} issued permits with a valid wait, {WMIN} to {WMAX}; permit types with 250 or more timed permits\n"
      "Simple classes issue near same-day; the longest medians are in reviewed commercial classes",
      FOOT, top=0.80, bottom=0.14, left=0.30, right=0.99)
save(fig, "chart_wait_by_type.png")

# (b) District concentration of applicant-stated value, top 10 districts
dist = stats["geography"]["council_district"]["by_district_sorted_by_total_cost"][:10]
dist = list(reversed(dist))
total_city = stats["cost"]["total_stated"]
fig, ax = plt.subplots(figsize=(9.5, 5.4))
ax.barh([f"District {r['district']}" for r in dist], [r["total_cost"] / 1e9 for r in dist],
        color=[AMBER if r["district"] == 19 else TEAL for r in dist])
for i, r in enumerate(dist):
    ax.text(r["total_cost"] / 1e9 + 0.06, i,
            f"${r['total_cost']/1e9:.2f}B stated ({r['total_cost']/total_city*100:.1f}% of citywide; {r['permits']:,} permits)",
            va="center", fontsize=8.5)
ax.set_xlim(0, max(r["total_cost"] for r in dist) / 1e9 * 2.05)
ax.set_xlabel("Applicant-stated construction value, $ billions (reported by applicants, not measured)")
ax.spines[["top", "right"]].set_visible(False)
frame(fig,
      "Where stated construction value concentrates: top 10 council districts by stated value\n"
      f"Population: permits issued {WMIN} to {WMAX} with a known council district ({stats['geography']['council_district']['known_rows']:,} of {ROWS:,} permits)\n"
      "Stated value is the applicant-reported construction cost in the permit record",
      FOOT, top=0.80, bottom=0.15, left=0.105, right=0.99)
save(fig, "chart_district_stated_value.png")

# (c) Wait distribution buckets
wd = stats["wait_distribution"]
fig, ax = plt.subplots(figsize=(9.5, 5.2))
vals = [b["share_of_valid"] * 100 for b in wd]
ax.bar([b["bucket"] for b in wd], vals,
       color=[TEAL, TEAL, TEAL, CHARCOAL, CHARCOAL, AMBER])
for b_, r in zip(ax.patches, wd):
    ax.text(b_.get_x() + b_.get_width() / 2, b_.get_height() + 0.8,
            f"{r['share_of_valid']*100:.1f}%\n{r['permits']:,} permits",
            ha="center", fontsize=8.5)
ax.set_ylim(0, max(vals) * 1.35)
ax.set_ylabel("Share of issued permits with a valid wait (%)")
ax.spines[["top", "right"]].set_visible(False)
frame(fig,
      "Distribution of entry-to-issue waits - among permits issued in the window\n"
      f"Population: {NTIMED:,} issued permits with a valid wait, {WMIN} to {WMAX}; median {stats['timing_all_valid']['median_days']:.0f} days, mean {stats['timing_all_valid']['mean_days']:.0f} days\n"
      "Buckets sum to 100% of the valid-wait population; the 1 negative-wait served row is excluded and counted in the brief",
      FOOT, top=0.80, bottom=0.15, left=0.065, right=0.99)
save(fig, "chart_wait_distribution.png")

# (d) Median wait in the top 5 districts by stated value, vs citywide median
top5 = stats["geography"]["council_district"]["by_district_sorted_by_total_cost"][:5]
city_med = stats["timing_all_valid"]["median_days"]
fig, ax = plt.subplots(figsize=(9.5, 5.2))
ax.bar([f"District {r['district']}" for r in top5], [r["median_wait_days"] for r in top5],
       color=[AMBER if r["district"] == 19 else TEAL for r in top5])
ax.axhline(city_med, color=CHARCOAL, linestyle="--", linewidth=1.4)
ax.text(4.45, city_med + 2.5, f"Citywide median: {city_med:.0f} days", ha="right", fontsize=9, color=CHARCOAL)
for b_, r in zip(ax.patches, top5):
    ax.text(b_.get_x() + b_.get_width() / 2, b_.get_height() + 1.5,
            f"{r['median_wait_days']:g} days\n({r['permits']:,} permits)",
            ha="center", fontsize=8.5)
ax.set_ylim(0, max(r["median_wait_days"] for r in top5) * 1.35)
ax.set_ylabel("Median entry-to-issue wait (days), among issued permits")
ax.spines[["top", "right"]].set_visible(False)
frame(fig,
      "Median wait in the five districts with the most stated value (unadjusted for permit mix)\n"
      f"Population: issued permits with a known district, {WMIN} to {WMAX}\n"
      "Not adjusted for permit mix: District 19 permits are 68.7% commercial classes vs 25.0% citywide (QA recomputation)",
      FOOT, top=0.80, bottom=0.15, left=0.065, right=0.99)
save(fig, "chart_district_median_wait.png")
print("charts done")
