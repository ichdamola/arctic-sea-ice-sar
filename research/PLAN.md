# Phase 2 research plan: do simple SAR rules hold up across many scenes?

*Written before running any multi-scene analysis. Hypotheses and exclusion rules below are fixed in advance;
any later change will be recorded in the "Changes to this plan" section with the reason.*

## Motivation

In Phase 1 (one scene, 2 May 2024, Beaufort Sea) a simple rule "HH < −19 dB = open water" labelled 7.5 % of the
area as water, while AMSR2 passive microwave said ~100 % ice. I proposed that most of the "dark" pixels were thin new
ice, not water. One scene can't test that. Phase 2 tests it, and the other weakness Phase 1 could not test
(wind-roughened water), on many scenes with expert ice charts as reference.

## Data

**AI4Arctic Sea Ice Challenge Dataset, ready-to-train version** (DTU, doi:10.11583/DTU.21316608, v3).
Per scene: Sentinel-1 EW HH + HV σ⁰ (NERSC noise correction, 80 m), incidence angle, an ice chart rasterised to the same
grid (total concentration SIC; dominant stage of development SOD where one type is ≥ 65 % of the ice), AMSR2 brightness
temperatures and ERA5 weather (2 km).

**Selection (fixed in advance):**
1. Canadian Ice Service charts only (Canadian Arctic, closest to the Phase 1 region).
2. November-May acquisitions (76 scenes).
3. **Dry-snow rule:** keep a scene only if its mean ERA5 2 m air temperature over valid pixels is **below −5 °C**.
   Wet snow changes backscatter completely; this keeps the physics comparable.
4. Valid pixels: chart value ≠ 255 (excludes land, areas outside the chart, and ambiguous SOD where applicable).

**Important caveat about the reference.** Ice charts are expert interpretations, not ground truth (dataset manual §2.4):
concentrations are polygon averages, and CIS analysts drew these charts *from the same SAR image* plus other data. So
agreement between SAR rules and charts is partly built in, and disagreement is not automatically a SAR error.

## Unit of analysis: chart regions, not pixels

A chart polygon says "this area is 90 % ice", not which pixels are ice. Comparing pixel by pixel would be wrong. Instead:

- **Chart region** = a connected area with identical (SIC, SOD) labels, at least **25 km²** (≈ 3 900 pixels at 80 m).
- For each region: **D** = fraction of pixels a SAR rule calls "dark / water"; **W** = chart open-water fraction = 1 − SIC.
- A perfect rule would give D ≈ W on average.

## SAR rules being tested

| Rule | Description | Tuned on Phase 2 data? |
|---|---|---|
| **T19** | HH < −19 dB (the Phase 1 threshold, unchanged) | No: tests whether it transfers |
| **T19-IA** | same, after normalising HH to 35° incidence with a slope estimated from charted 100 % first-year ice regions | slope only |
| **KM4** | k-means (k=4) on (HH, HV) per scene; darkest cluster = water | No |

## Research questions and predictions

**RQ1: Is "dark" thin ice?** In regions charted as **≥ 90 % ice**, does the SAR dark fraction D depend on the dominant
stage of development?
- **H1:** D is higher where the dominant type is **new or young ice** (SOD 1-2) than where it is **thick first-year or
  old ice** (SOD 4-5).
- What would count against H1: D similar across SOD classes, or too few new/young-ice regions to tell (will report counts).

**RQ2: Does wind make open water look like ice?** In regions charted as **open water (SIC = 0)**, does D fall as ERA5 10 m
wind speed rises?
- **H2:** D decreases with wind speed (rougher water → brighter HH → fewer pixels below the threshold).
- Reported as D per wind-speed bin (0-3, 3-6, 6-9, > 9 m/s) with region counts.

**RQ3: Does the Phase 1 threshold transfer, and does incidence correction help?**
- **H3a:** T19's region-level error |D − W| varies strongly between scenes (it was tuned on one scene).
- **H3b:** T19-IA has lower mean |D − W| than T19.
- Reported: mean and median |D − W| per rule, per-scene spread, and bias (D − W) by SIC class.

## What I will report regardless of outcome

Number of scenes kept/excluded and why; region counts behind every number; all three rules; results that contradict
the hypotheses. No scene is removed after looking at results.

## Later (Phase 2b, not part of this plan)

A small learned model (gradient boosting on pixel features, then possibly a U-Net) with a **scene-level** train/test
split, compared against these rules on the same regions.

## Changes to this plan

*(none yet)*
