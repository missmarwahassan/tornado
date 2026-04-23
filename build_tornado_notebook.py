import json
from pathlib import Path


NOTEBOOK_PATH = Path("/Users/marwahas/Documents/Codex/2026-04-21-files-mentioned-by-the-user-narrative/tornado_story_dashboard.ipynb")


def md_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    md_cell(
        """# Tornado Geography Beyond Classic Tornado Alley

This notebook is designed as a presentation-ready narrative visualization for the team project. It uses a linked Altair dashboard to show that while Texas and the Great Plains still dominate total tornado counts, the Southeast has become increasingly central to the modern story.

**Working assumption:** because the project proposal PDF was not extractable in this environment, this notebook is framed around a likely team goal: showing how tornado activity is distributed across the United States over time, and how that story has shifted in ways a simple "Tornado Alley" framing misses.

**What makes this notebook different**
- It uses a linked editorial dashboard instead of a single standard line chart.
- It combines long-run intensity, state-level volatility, and decade rank movement in one coordinated interaction.
- It is presentation-friendly: the markdown is already structured so your team can talk through goal, findings, progress, and next steps.
"""
    ),
    code_cell(
        """import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path

alt.data_transformers.disable_max_rows()
alt.renderers.set_embed_options(actions=False)
"""
    ),
    code_cell(
        """DATA_PATH = Path("Tornado_Data_Count.csv")

wide = pd.read_csv(DATA_PATH)
wide.head()
"""
    ),
    code_cell(
        """regions = {
    "Great Plains": ["TEXAS", "OKLAHOMA", "KANSAS", "NEBRASKA", "NORTH DAKOTA", "SOUTH DAKOTA"],
    "Southeast": ["ALABAMA", "ARKANSAS", "FLORIDA", "GEORGIA", "KENTUCKY", "LOUISIANA", "MISSISSIPPI", "NORTH CAROLINA", "SOUTH CAROLINA", "TENNESSEE"],
    "Midwest": ["ILLINOIS", "INDIANA", "IOWA", "MICHIGAN", "MINNESOTA", "MISSOURI", "OHIO", "WISCONSIN"],
    "Northeast": ["CONNECTICUT", "DELAWARE", "MAINE", "MARYLAND", "MASSACHUSETTS", "NEW HAMPSHIRE", "NEW JERSEY", "NEW YORK", "PENNSYLVANIA", "RHODE ISLAND", "VERMONT"],
    "West": ["ARIZONA", "CALIFORNIA", "COLORADO", "IDAHO", "MONTANA", "NEVADA", "NEW MEXICO", "OREGON", "UTAH", "WASHINGTON", "WYOMING"],
}

state_to_region = {state: region for region, states in regions.items() for state in states}
state_fips = {
    "ALABAMA": 1,
    "ALASKA": 2,
    "ARIZONA": 4,
    "ARKANSAS": 5,
    "CALIFORNIA": 6,
    "COLORADO": 8,
    "CONNECTICUT": 9,
    "DELAWARE": 10,
    "FLORIDA": 12,
    "GEORGIA": 13,
    "HAWAII": 15,
    "IDAHO": 16,
    "ILLINOIS": 17,
    "INDIANA": 18,
    "IOWA": 19,
    "KANSAS": 20,
    "KENTUCKY": 21,
    "LOUISIANA": 22,
    "MAINE": 23,
    "MARYLAND": 24,
    "MASSACHUSETTS": 25,
    "MICHIGAN": 26,
    "MINNESOTA": 27,
    "MISSISSIPPI": 28,
    "MISSOURI": 29,
    "MONTANA": 30,
    "NEBRASKA": 31,
    "NEVADA": 32,
    "NEW HAMPSHIRE": 33,
    "NEW JERSEY": 34,
    "NEW MEXICO": 35,
    "NEW YORK": 36,
    "NORTH CAROLINA": 37,
    "NORTH DAKOTA": 38,
    "OHIO": 39,
    "OKLAHOMA": 40,
    "OREGON": 41,
    "PENNSYLVANIA": 42,
    "RHODE ISLAND": 44,
    "SOUTH CAROLINA": 45,
    "SOUTH DAKOTA": 46,
    "TENNESSEE": 47,
    "TEXAS": 48,
    "UTAH": 49,
    "VERMONT": 50,
    "VIRGINIA": 51,
    "WASHINGTON": 53,
    "WEST VIRGINIA": 54,
    "WISCONSIN": 55,
    "WYOMING": 56,
}

long = (
    wide.melt(id_vars="States", var_name="year", value_name="count")
    .assign(
        year=lambda d: d["year"].astype(int),
        count=lambda d: pd.to_numeric(d["count"], errors="coerce"),
    )
    .dropna(subset=["count"])
)

long["region"] = long["States"].map(state_to_region).fillna("Other")
long["decade"] = (long["year"] // 10) * 10
long["decade_label"] = long["decade"].astype(str) + "s"
long["year_start"] = long["year"] - 0.5
long["year_end"] = long["year"] + 0.5
long["state_name"] = long["States"].str.title()
long["id"] = long["States"].map(state_fips)
map_data = long.dropna(subset=["id"]).copy()
map_data["id"] = map_data["id"].astype(int)
map_data["lookup_key"] = map_data["id"].astype(str) + "_" + map_data["year"].astype(str)

state_order = (
    long.groupby("States")["count"]
    .sum()
    .sort_values(ascending=False)
    .index
    .tolist()
)

national = long.groupby("year", as_index=False)["count"].sum().rename(columns={"count": "us_total"})
region_year = long.groupby(["region", "year"], as_index=False)["count"].sum()

decade_ranks = (
    long.groupby(["decade", "decade_label", "States", "region"], as_index=False)["count"]
    .sum()
    .sort_values(["decade", "count"], ascending=[True, False])
)
decade_ranks["rank"] = decade_ranks.groupby("decade")["count"].rank(method="dense", ascending=False)
top_decade_ranks = decade_ranks[decade_ranks["rank"] <= 12].copy()

era_summary = (
    long.assign(
        era=np.where(long["year"] < 1960, "1950s", np.where(long["year"] >= 2010, "2010s", "middle"))
    )
    .query("era != 'middle'")
    .groupby(["States", "region", "era"], as_index=False)["count"]
    .mean()
    .pivot(index=["States", "region"], columns="era", values="count")
    .fillna(0)
    .reset_index()
)

state_metrics = (
    long.groupby(["States", "region"], as_index=False)
    .agg(
        total_count=("count", "sum"),
        avg_annual=("count", "mean"),
        volatility=("count", "std"),
        peak_year=("count", "max"),
    )
    .merge(era_summary, on=["States", "region"], how="left")
    .fillna({"1950s": 0, "2010s": 0})
)

state_metrics["growth_delta"] = state_metrics["2010s"] - state_metrics["1950s"]
state_metrics["label"] = np.where(
    state_metrics["total_count"].rank(ascending=False, method="dense") <= 12,
    state_metrics["States"],
    "",
)

top_states = (
    state_metrics.nlargest(8, "total_count")[["States", "region", "total_count", "avg_annual", "growth_delta"]]
    .reset_index(drop=True)
)

top_states
"""
    ),
    md_cell(
        """## Narrative Framing

The dataset tracks annual tornado counts by state from **1951 to 2019**. That makes it strong for a story about **where tornado activity concentrates, which places are becoming more exposed, and how the national picture changes over time**.

The core argument this notebook supports:

1. The Great Plains still carry the highest cumulative burden.
2. The Southeast has become much more prominent in recent decades.
3. A modern tornado story is about **migration and spread**, not just one fixed corridor.
"""
    ),
    code_cell(
        """region_options = ["All", "Great Plains", "Southeast", "Midwest", "Northeast", "West", "Other"]

region_filter = alt.param(
    name="region_filter",
    value="All",
    bind=alt.binding_select(options=region_options, name="Regional focus: "),
)

picked_state = alt.selection_point(
    name="picked_state",
    fields=["States"],
    value=[{"States": "TEXAS"}],
    empty=False,
)

year_window = alt.selection_interval(name="year_window", encodings=["x"])

paper = "#f6f1e7"
ink = "#1f1d1a"
accent = "#e4572e"
accent_soft = "#f3a712"
grid = "#d8ccb8"
region_palette = ["#7f5539", "#bc4749", "#386641", "#577590", "#3d405b", "#6c757d"]

base_config = {
    "background": paper,
    "title": {"color": ink, "fontSize": 20, "font": "Georgia"},
    "axis": {
        "labelColor": ink,
        "titleColor": ink,
        "gridColor": grid,
        "labelFont": "Helvetica",
        "titleFont": "Helvetica",
    },
    "legend": {
        "labelColor": ink,
        "titleColor": ink,
        "labelFont": "Helvetica",
        "titleFont": "Helvetica",
    },
    "view": {"stroke": None},
}
"""
    ),
    code_cell(
        """timeline = (
    alt.layer(
        alt.Chart(national)
        .mark_area(line={"color": accent, "strokeWidth": 2}, color=accent, opacity=0.22)
        .encode(
            x=alt.X(
                "year:Q",
                title=None,
                axis=alt.Axis(format="d", tickCount=8),
                scale=alt.Scale(domain=[1950.5, 2019.5], nice=False, zero=False),
            ),
            y=alt.Y("us_total:Q", title="US total tornadoes"),
            tooltip=[
                alt.Tooltip("year:Q", title="Year", format="d"),
                alt.Tooltip("us_total:Q", title="National total", format=".0f"),
            ],
        ),
        alt.Chart(national)
        .mark_rect(opacity=0, cursor="crosshair")
        .encode(
            x=alt.X(
                "year_start:Q",
                scale=alt.Scale(domain=[1950.5, 2019.5], nice=False, zero=False),
            ),
            x2="year_end:Q",
        )
        .add_params(year_window),
    )
    .properties(
        width=860,
        height=95,
        title=alt.TitleParams(
            text="National Pulse",
            subtitle="Brush across the timeline to focus the rest of the dashboard on a specific era.",
            anchor="start",
        ),
    )
)

heatmap = (
    alt.Chart(long)
    .transform_filter(year_window)
    .transform_filter("region_filter == 'All' || datum.region == region_filter")
    .mark_rect()
    .encode(
        x=alt.X(
            "year_start:Q",
            title="Year",
            axis=alt.Axis(format="d", tickCount=9, values=list(range(1952, 2020, 4))),
            scale=alt.Scale(domain=[1950.5, 2019.5], nice=False, zero=False),
        ),
        x2="year_end:Q",
        y=alt.Y("States:N", title=None, sort=state_order),
        color=alt.Color(
            "count:Q",
            title="Annual tornadoes",
            scale=alt.Scale(scheme="goldred"),
        ),
        stroke=alt.condition(picked_state, alt.value(paper), alt.value(None)),
        strokeWidth=alt.condition(picked_state, alt.value(1.6), alt.value(0)),
        tooltip=[
            alt.Tooltip("States:N", title="State"),
            alt.Tooltip("region:N", title="Region"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip("count:Q", title="Tornadoes", format=".0f"),
        ],
    )
    .add_params(region_filter, picked_state)
    .properties(
        width=860,
        height=620,
        title=alt.TitleParams(
            text="Tornado Pressure Wall",
            subtitle="Each stripe is a state; brighter cells mark heavier annual tornado counts. Click any state to carry it through the linked views.",
            anchor="start",
        ),
    )
)

scatter = (
    alt.Chart(state_metrics)
    .transform_filter("region_filter == 'All' || datum.region == region_filter")
    .mark_circle(opacity=0.9, stroke=paper, strokeWidth=1.2)
    .encode(
        x=alt.X("avg_annual:Q", title="Average annual tornadoes (1951-2019)"),
        y=alt.Y("growth_delta:Q", title="Growth from 1950s average to 2010s average"),
        size=alt.Size("total_count:Q", title="Total tornadoes"),
        color=alt.Color("region:N", scale=alt.Scale(range=region_palette), title="Region"),
        tooltip=[
            alt.Tooltip("States:N", title="State"),
            alt.Tooltip("region:N", title="Region"),
            alt.Tooltip("avg_annual:Q", title="Avg annual", format=".1f"),
            alt.Tooltip("growth_delta:Q", title="1950s to 2010s change", format=".1f"),
            alt.Tooltip("volatility:Q", title="Volatility", format=".1f"),
            alt.Tooltip("total_count:Q", title="Total tornadoes", format=".0f"),
        ],
        opacity=alt.condition(picked_state, alt.value(1), alt.value(0.78)),
    )
    .add_params(picked_state)
    .properties(
        width=360,
        height=300,
        title=alt.TitleParams(
            text="Exposure vs. Acceleration",
            subtitle="States in the upper-right are both consistently active and growing more intense over time.",
            anchor="start",
        ),
    )
)

scatter_labels = (
    alt.Chart(state_metrics)
    .transform_filter("region_filter == 'All' || datum.region == region_filter")
    .transform_filter("datum.label != ''")
    .mark_text(align="left", dx=7, dy=-5, fontSize=11, color=ink)
    .encode(
        x="avg_annual:Q",
        y="growth_delta:Q",
        text="label:N",
    )
)

state_line = (
    alt.Chart(long)
    .transform_filter(picked_state)
    .mark_line(color=accent, strokeWidth=3, point=alt.OverlayMarkDef(size=45, filled=True))
    .encode(
        x=alt.X(
            "year:Q",
            title="Year",
            axis=alt.Axis(format="d", tickCount=8),
            scale=alt.Scale(domain=[1950.5, 2019.5], nice=False, zero=False),
        ),
        y=alt.Y("count:Q", title="Annual tornadoes"),
        tooltip=[
            alt.Tooltip("States:N", title="State"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip("count:Q", title="Tornadoes", format=".0f"),
        ],
    )
    .transform_filter(year_window)
    .properties(
        width=360,
        height=170,
        title=alt.TitleParams(
            text="Selected State Trend",
            subtitle="Starts on Texas by default; click a different state in any linked view to update it.",
            anchor="start",
        ),
    )
)

state_decades = (
    alt.Chart(decade_ranks)
    .transform_filter(picked_state)
    .mark_bar(color=accent_soft, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X("decade_label:N", title="Decade"),
        y=alt.Y("count:Q", title="Tornadoes per decade"),
        tooltip=[
            alt.Tooltip("States:N", title="State"),
            alt.Tooltip("decade_label:N", title="Decade"),
            alt.Tooltip("count:Q", title="Decade total", format=".0f"),
            alt.Tooltip("rank:Q", title="National rank", format=".0f"),
        ],
    )
    .properties(
        width=360,
        height=170,
        title=alt.TitleParams(
            text="Decade Fingerprint",
            subtitle="This shows how much of the selected state's story comes from each decade.",
            anchor="start",
        ),
    )
)

hero_dashboard = (
    ((timeline & heatmap) | ((scatter + scatter_labels) & state_line & state_decades))
    .resolve_scale(color="independent", size="independent")
    .configure(**base_config)
)

hero_dashboard
"""
    ),
    md_cell(
        """## Why This Dashboard Works for the Story

- The **timeline** shows the national pulse and lets you isolate eras interactively.
- The **pressure wall** turns the full 50-state history into a single texture, which is much more memorable than a default line plot.
- The **scatterplot** reframes the conversation from "who has the most tornadoes?" to "who is both exposed and accelerating?"
- The **selected-state panels** make it easy to talk through individual examples in a live presentation.
"""
    ),
    code_cell(
        """map_year = alt.param(
    name="map_year",
    value=2011,
    bind=alt.binding_range(min=1951, max=2019, step=1, name="Map year: "),
)

us_states = alt.topo_feature(
    "https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json",
    "states",
)

state_map = (
    alt.Chart(us_states)
    .mark_geoshape(stroke=paper, strokeWidth=0.7)
    .transform_calculate(lookup_key="toString(datum.id) + '_' + toString(map_year)")
    .transform_lookup(
        lookup="lookup_key",
        from_=alt.LookupData(
            map_data,
            key="lookup_key",
            fields=["state_name", "year", "count", "region"],
        ),
    )
    .encode(
        color=alt.Color(
            "count:Q",
            title="Tornadoes",
            scale=alt.Scale(scheme="orangered"),
        ),
        tooltip=[
            alt.Tooltip("state_name:N", title="State"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip("count:Q", title="Tornadoes", format=".0f"),
            alt.Tooltip("region:N", title="Region"),
        ],
    )
    .project(type="albersUsa")
    .add_params(map_year)
    .properties(
        width=900,
        height=500,
        title=alt.TitleParams(
            text="Tornado Activity by State",
            subtitle="A standalone choropleth adapted from the separate HTML view. Use the slider to watch the center of activity shift year by year.",
            anchor="start",
        ),
    )
    .configure(**base_config)
)

state_map
"""
    ),
    code_cell(
        """bump_lines = (
    alt.Chart(top_decade_ranks)
    .transform_filter("region_filter == 'All' || datum.region == region_filter")
    .mark_line(strokeWidth=3)
    .encode(
        x=alt.X("decade_label:N", title="Decade"),
        y=alt.Y(
            "rank:Q",
            title="Rank among states",
            scale=alt.Scale(domain=[12.5, 0.5]),
            axis=alt.Axis(values=list(range(1, 13))),
        ),
        color=alt.Color("region:N", scale=alt.Scale(range=region_palette), title="Region"),
        detail="States:N",
        tooltip=[
            alt.Tooltip("States:N", title="State"),
            alt.Tooltip("region:N", title="Region"),
            alt.Tooltip("decade_label:N", title="Decade"),
            alt.Tooltip("rank:Q", title="Rank", format=".0f"),
            alt.Tooltip("count:Q", title="Decade total", format=".0f"),
        ],
        opacity=alt.condition(picked_state, alt.value(1), alt.value(0.45)),
    )
    .add_params(picked_state)
)

bump_points = bump_lines.mark_point(filled=True, size=80)

final_labels = (
    alt.Chart(top_decade_ranks)
    .transform_filter("datum.decade == 2010")
    .transform_filter("region_filter == 'All' || datum.region == region_filter")
    .mark_text(align="left", dx=8, fontSize=11, color=ink)
    .encode(x="decade_label:N", y="rank:Q", text="States:N")
)

bump_chart = (
    (bump_lines + bump_points + final_labels)
    .properties(
        width=960,
        height=420,
        title=alt.TitleParams(
            text="Which States Enter the Top Tier Over Time?",
            subtitle="This bump chart tracks the top-12 states by decade. It helps show that the national hierarchy broadens beyond the classic Plains core.",
            anchor="start",
        ),
    )
    .configure(**base_config)
)

bump_chart
"""
    ),
    code_cell(
        """summary = pd.DataFrame(
    [
        {
            "Finding": "Highest cumulative total",
            "State or region": state_metrics.sort_values("total_count", ascending=False).iloc[0]["States"],
            "Value": f"{state_metrics['total_count'].max():,.0f} tornadoes",
        },
        {
            "Finding": "Largest 1950s to 2010s average increase",
            "State or region": state_metrics.sort_values("growth_delta", ascending=False).iloc[0]["States"],
            "Value": f"{state_metrics['growth_delta'].max():.1f} tornadoes per year",
        },
        {
            "Finding": "Largest regional total",
            "State or region": region_year.groupby('region')['count'].sum().sort_values(ascending=False).index[0],
            "Value": f"{region_year.groupby('region')['count'].sum().max():,.0f} tornadoes",
        },
    ]
)

summary
"""
    ),
    md_cell(
        """## Presentation Talking Points

Use these as speaker notes for the preliminary presentation:

- **Goal of the project:** show that tornado risk is a national story with meaningful regional change over time, not just a static Tornado Alley map.
- **How this differs from similar work:** instead of a single map or line chart, the visualization links macro trends, state-level patterns, and rank shifts in one dashboard.
- **Current progress:** we already have a functioning interactive Altair prototype with coordinated views and a clear argument emerging from the data.
- **Plan for remaining work:** refine the regional framing, add annotations for landmark years or outbreaks, and potentially merge in severity or fatality data for a stronger impact story.
- **Feedback to ask for:** whether the audience finds the regional grouping intuitive, and whether the story is more compelling when framed as geographic migration versus concentration.
"""
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.13",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2))
print(f"Wrote {NOTEBOOK_PATH}")
