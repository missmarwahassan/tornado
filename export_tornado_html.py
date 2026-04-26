import json
from pathlib import Path


WORKDIR = Path("/Users/marwahas/Documents/Codex/2026-04-21-files-mentioned-by-the-user-narrative")
NOTEBOOK_PATH = WORKDIR / "tornado_story_dashboard.ipynb"
HTML_PATH = WORKDIR / "tornado_story_dashboard.html"
INDEX_PATH = WORKDIR / "index.html"

PROJECT_TITLE = "The Changing Geography of Tornado Risk"
COURSE_LABEL = "SI 649: Information Visualization"
TEAM_LABEL = "Marwa Hassan, Hassan Beydoun, Maryam Romio"


def load_notebook_namespace() -> dict:
    nb = json.loads(NOTEBOOK_PATH.read_text())
    ns: dict = {}
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        exec(compile(src, f"<cell {i}>", "exec"), ns)
    return ns


def paragraph_block(paragraphs: list[str]) -> str:
    return "\n".join(f"<p>{p}</p>" for p in paragraphs)


def main() -> None:
    ns = load_notebook_namespace()
    alt = ns["alt"]
    state_metrics = ns["state_metrics"]
    region_palette = ns["region_palette"]
    timeline = ns["timeline"]
    heatmap = ns["heatmap"]
    state_line = ns["state_line"]
    state_decades = ns["state_decades"]
    map_spec = ns["state_map"].to_dict()

    um_blue = "#00274C"
    um_maize = "#FFCB05"
    um_slate = "#4A5A70"
    um_line = "#D9E1EA"
    panel_bg = "#FFFFFF"

    public_config = {
        "background": panel_bg,
        "title": {"color": um_blue, "fontSize": 22, "font": "Merriweather"},
        "axis": {
            "labelColor": um_blue,
            "titleColor": um_blue,
            "gridColor": um_line,
            "labelFont": "IBM Plex Sans",
            "titleFont": "IBM Plex Sans",
        },
        "legend": {
            "labelColor": um_blue,
            "titleColor": um_blue,
            "labelFont": "IBM Plex Sans",
            "titleFont": "IBM Plex Sans",
        },
        "view": {"stroke": None},
    }

    public_hero = (
        (
            timeline.properties(width=1100, height=120)
            & heatmap.properties(width=1060, height=660)
            & (
                state_line.properties(width=540, height=175)
                | state_decades.properties(width=540, height=175)
            )
        )
        .resolve_scale(color="independent", size="independent")
        .configure(**public_config)
        .configure_legend(
            orient="bottom",
            direction="horizontal",
            gradientLength=360,
            gradientThickness=16,
            titleAnchor="start",
            labelLimit=130,
        )
    )
    hero_spec = public_hero.to_dict()

    static_labels = (
        alt.Chart(state_metrics)
        .transform_filter("datum.label != ''")
        .mark_text(align="left", dx=8, dy=-6, fontSize=11, color=um_blue)
        .encode(
            x="avg_annual:Q",
            y="growth_delta:Q",
            text="label:N",
        )
    )

    community_scatter = (
        (
            alt.Chart(state_metrics)
            .mark_circle(opacity=0.9, stroke=panel_bg, strokeWidth=1.4)
            .encode(
                x=alt.X(
                    "avg_annual:Q",
                    title="Average annual tornadoes (1951-2019)",
                    scale=alt.Scale(domain=[-2, 142], nice=False, zero=False),
                ),
                y=alt.Y(
                    "growth_delta:Q",
                    title="Increase from 1950s average to 2010s average",
                    scale=alt.Scale(domain=[-8, 64], nice=False, zero=False),
                ),
                size=alt.Size("total_count:Q", title="Total tornadoes"),
                color=alt.Color(
                    "region:N",
                    scale=alt.Scale(range=region_palette),
                    title="Region",
                ),
                tooltip=[
                    alt.Tooltip("States:N", title="State"),
                    alt.Tooltip("region:N", title="Region"),
                    alt.Tooltip("avg_annual:Q", title="Average annual tornadoes", format=".1f"),
                    alt.Tooltip("growth_delta:Q", title="Growth since 1950s", format=".1f"),
                    alt.Tooltip("volatility:Q", title="Volatility", format=".1f"),
                    alt.Tooltip("total_count:Q", title="Total tornadoes", format=".0f"),
                ],
            )
            + static_labels
        )
        .properties(
            width=920,
            height=560,
            title=alt.TitleParams(
                text="Exposure vs. Acceleration",
                subtitle="Drag to pan, use your trackpad or mouse wheel to zoom, and double-click to reset.",
                anchor="start",
            ),
        )
        .interactive()
        .configure(**public_config)
    )
    scatter_spec = community_scatter.to_dict()

    map_spec["config"] = public_config
    map_spec["params"] = [
        {**param, "value": 1951} if param.get("name") == "map_year" else param
        for param in map_spec.get("params", [])
    ]

    intro_copy = [
        "For decades, tornado risk in the United States has been associated with a narrow corridor across the Great Plains, commonly known as “Tornado Alley.” But when we step back and examine long-term data, a more complex story emerges.",
        "Tornado activity is not only persistent, but it is shifting, expanding, and redistributing across regions over time. This explorable analysis lets you trace those changes across decades, states, and geographic patterns.",
    ]

    first_section_copy = [
        "The timeline below shows the national “pulse” of tornado activity since the 1950s. While year-to-year variation is expected, the broader pattern reveals that tornado activity remains consistently present over time.",
        "But the bigger story emerges when we look beyond the national average. The heatmap below shows how tornado activity accumulates across individual states over time. As you scan across decades, notice how activity becomes more widespread—especially outside the traditional Great Plains core.",
    ]

    heatmap_copy = [
        "Each row represents a state, and each column represents a year. Brighter colors indicate higher tornado counts. Instead of focusing on a single location, this view reveals how activity spreads and shifts across the entire country."
    ]

    state_detail_copy = [
        "Try selecting a state to follow its long-term trajectory. Some states, particularly in the Southeast, show increasing activity over time, suggesting that tornado risk is expanding beyond its historical core."
    ]

    scatter_intro_copy = [
        "Not all states are changing in the same way. Some have long experienced frequent tornado activity, while others are seeing faster growth in recent decades.",
        "This chart compares long-term exposure (average annual tornadoes) with recent acceleration (how much activity has increased over time). Together, these dimensions reveal which states are not just active—but becoming more at risk.",
    ]

    scatter_side_copy = [
        "States farther to the right have historically higher tornado activity. States higher up have experienced the greatest increases in recent decades.",
        "Notice how several Southeastern states appear high on the chart despite not being part of the traditional Tornado Alley. This highlights a key shift: tornado risk is growing fastest outside its historical core.",
    ]

    map_intro_copy = [
        "To fully understand how tornado geography is changing, it helps to watch it unfold over time.",
        "Use the slider below to move through the years and observe how the center of activity evolves. Earlier decades show a strong concentration in the Great Plains, but over time, activity spreads eastward and becomes more diffuse.",
        "This shift is gradual rather than abrupt—what was once a concentrated corridor is becoming a broader national pattern.",
    ]

    meaning_copy = [
        "Taken together, these patterns challenge the long-standing idea of a fixed Tornado Alley. Instead, tornado activity in the United States appears to be evolving, both in where it occurs and how it changes over time.",
        "While the Great Plains remain a central region of activity, increasing frequency and growth in the Southeast and other regions suggest a broader redistribution of risk. In many ways, our understanding of tornado geography has not kept pace with the data.",
        "This gap is especially important when considering infrastructure and preparedness. Storm shelters, tornado siren systems, building codes, and public awareness efforts have historically been concentrated in the Great Plains, where tornado risk was assumed to be highest. As activity expands into regions like the Southeast, where population density is higher and protective infrastructure is often less widespread, communities may be more vulnerable to severe weather impacts.",
        "Understanding these changes is critical, not just for interpreting past trends, but for preparing for future exposure. Expanding access to storm shelters, improving tornado siren coverage, and strengthening building standards outside the traditional Tornado Alley will be essential as the geography of risk continues to shift.",
    ]

    project_notes = [
        (
            "What is Tornado Alley and How Is it Shifting?",
            "For a long time, people have had a pretty clear idea of where tornadoes happen in the United States. When you hear the term Tornado Alley, you probably think of the Great Plains, especially states like Texas, Oklahoma, and Kansas. It has been treated as a fixed region where tornado risk is concentrated and expected.",
        ),
        (
            "Why simple counts are not enough",
            "Most analyses focus on how many tornadoes happen each year. That is a useful starting point, but it misses some important context. Total counts do not show where tornadoes are happening or how consistent that activity is over time.",
        ),
        (
            "Project approach",
            "In this project, we focused on three things: where tornadoes are happening, how often they occur, and how much that changes from year to year. Looking at all three together gives a better sense of how tornado activity is actually evolving across the country.",
        ),
        (
            "Final takeaway",
            "Overall, while Tornado Alley is still a useful concept, it no longer tells the full story. Tornado activity in the United States is not just concentrated in one region. Understanding that shift matters for how we think about preparedness, infrastructure, and long-term risk.",
        ),
    ]

    overview_cards = [
        (
            "Project Goal",
            "Through interactive maps and timelines, users can explore changes in location, frequency, and seasonality, revealing the eastward shift of Tornado Alley and growing unpredictability of severe weather.",
        ),
        ("Project Type", "Explorable explainers"),
        (
            "Reading Strategy",
            "Start with the national pulse and pressure wall, then compare exposure and acceleration across states, and finally use the map to watch the geography shift over time.",
        ),
    ]

    notes_html = "\n".join(
        f"""
        <div class="note-card">
          <h3>{title}</h3>
          <p>{body}</p>
        </div>
        """
        for title, body in project_notes
    )

    overview_html = "\n".join(
        f"""
        <div class="overview-card">
          <h3>{title}</h3>
          <p>{body}</p>
        </div>
        """
        for title, body in overview_cards
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{PROJECT_TITLE}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Merriweather:wght@400;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    :root {{
      --um-blue: #00274C;
      --um-maize: #FFCB05;
      --um-slate: #4A5A70;
      --um-line: #D9E1EA;
      --um-panel: #FFFFFF;
      --um-bg: #F7F9FC;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", Arial, Helvetica, sans-serif;
      color: var(--um-blue);
      background: #ffffff;
      line-height: 1.6;
    }}
    .brandbar {{
      background: var(--um-blue);
      color: #ffffff;
      border-bottom: 6px solid var(--um-maize);
    }}
    .brandbar-inner {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 16px 24px 14px;
      font-size: 0.95rem;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    main {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 0 24px 72px;
    }}
    .hero {{
      padding: 38px 0 26px;
      border-bottom: 1px solid var(--um-line);
    }}
    .kicker {{
      margin: 0 0 10px;
      color: var(--um-slate);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0 0 12px;
      font-family: "Merriweather", Georgia, "Times New Roman", serif;
      font-size: clamp(2.4rem, 4.8vw, 4.5rem);
      line-height: 1.02;
      letter-spacing: -0.03em;
      max-width: 980px;
    }}
    h2 {{
      margin: 0 0 10px;
      font-family: "Merriweather", Georgia, "Times New Roman", serif;
      font-size: clamp(1.55rem, 2.2vw, 2.2rem);
      line-height: 1.15;
      letter-spacing: -0.02em;
    }}
    h3 {{
      margin: 0 0 8px;
      font-family: "Merriweather", Georgia, "Times New Roman", serif;
      font-size: 1.02rem;
      line-height: 1.2;
    }}
    p {{
      margin: 0 0 14px;
    }}
    .lede {{
      max-width: 920px;
      font-size: 1.08rem;
      color: var(--um-slate);
    }}
    .meta-grid,
    .overview,
    .notes-grid {{
      display: grid;
      gap: 16px;
    }}
    .meta-grid {{
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin-top: 22px;
    }}
    .overview {{
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      margin-top: 24px;
    }}
    .notes-grid {{
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}
    .meta-card,
    .overview-card,
    .note-card,
    .callout,
    .panel,
    .text-panel {{
      background: var(--um-panel);
      border: 1px solid var(--um-line);
      border-radius: 8px;
      box-shadow: none;
    }}
    .meta-card,
    .overview-card,
    .note-card,
    .callout,
    .text-panel {{
      padding: 18px 18px 16px;
    }}
    .meta-card,
    .overview-card,
    .note-card {{
      border-top: 4px solid var(--um-maize);
    }}
    .meta-card strong {{
      display: block;
      margin-bottom: 4px;
      font-size: 0.8rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--um-slate);
    }}
    .section {{
      margin-top: 42px;
    }}
    .section-copy {{
      max-width: 860px;
      color: var(--um-slate);
      margin-bottom: 10px;
    }}
    .panel {{
      padding: 22px 20px;
      margin-top: 18px;
      overflow: hidden;
    }}
    .text-panel {{
      margin-top: 14px;
    }}
    .story-divider {{
      width: 72px;
      height: 6px;
      margin: 10px 0 20px;
      background: var(--um-maize);
      border-radius: 0;
    }}
    .split {{
      display: grid;
      grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.55fr);
      gap: 18px;
      align-items: start;
    }}
    .vega-embed summary {{
      display: none;
    }}
    .vega-embed,
    .vega-embed > div {{
      width: 100%;
    }}
    .lede,
    .section-copy,
    .text-panel p,
    .callout p,
    .overview-card p,
    .note-card p,
    .meta-card span,
    footer {{
      max-width: 75ch;
    }}
    footer {{
      margin-top: 30px;
      padding-top: 18px;
      border-top: 1px solid var(--um-line);
      color: var(--um-slate);
      font-size: 0.93rem;
    }}
    @media (max-width: 980px) {{
      .split {{
        grid-template-columns: 1fr;
      }}
      .panel {{
        padding: 18px 14px;
      }}
      main {{
        padding: 0 14px 56px;
      }}
      .brandbar-inner {{
        padding: 14px 14px 12px;
      }}
    }}
  </style>
</head>
<body>
  <div class="brandbar">
    <div class="brandbar-inner">University of Michigan | School of Information</div>
  </div>
  <main>
    <section class="hero">
      <p class="kicker">Final Narrative Visualization Project</p>
      <h1>{PROJECT_TITLE}</h1>
      <div class="story-divider"></div>
      <p class="lede">
        This site presents our team’s final narrative visualization project on tornado activity across the United States from 1951 to 2019.
      </p>
      {paragraph_block(intro_copy)}
      <div class="meta-grid">
        <div class="meta-card">
          <strong>Course</strong>
          <span>{COURSE_LABEL}</span>
        </div>
        <div class="meta-card">
          <strong>Team</strong>
          <span>{TEAM_LABEL}</span>
        </div>
      </div>
      <div class="overview">
        {overview_html}
      </div>
    </section>

    <section class="section">
      <h2>1. National Pattern and State Detail</h2>
      <div class="story-divider"></div>
      <p class="section-copy">
        This opening dashboard is the main entry point for the project. It is designed to give a broad overview of tornado activity across the country.
      </p>
      {paragraph_block(first_section_copy)}
      <div class="text-panel">
        {paragraph_block(heatmap_copy)}
      </div>
      <div class="panel">
        <div id="hero-dashboard"></div>
      </div>
      <div class="text-panel">
        {paragraph_block(state_detail_copy)}
      </div>
    </section>

    <section class="section">
      <h2>2. Exposure and Acceleration</h2>
      <div class="story-divider"></div>
      {paragraph_block(scatter_intro_copy)}
      <div class="split">
        <div class="panel">
          <div id="zoom-scatter"></div>
        </div>
        <aside class="callout">
          {paragraph_block(scatter_side_copy)}
        </aside>
      </div>
    </section>

    <section class="section">
      <h2>3. State-by-State Geographic Shift</h2>
      <div class="story-divider"></div>
      {paragraph_block(map_intro_copy)}
      <div class="panel">
        <div id="state-map"></div>
      </div>
    </section>

    <section class="section">
      <h2>4. What This Means</h2>
      <div class="story-divider"></div>
      {paragraph_block(meaning_copy)}
    </section>

    <section class="section">
      <h2>5. Project Notes</h2>
      <div class="story-divider"></div>
      <div class="notes-grid">
        {notes_html}
      </div>
    </section>

    <footer>
      Built for {COURSE_LABEL}. Published as an interactive GitHub Pages site using Altair and Vega-Lite.
    </footer>
  </main>

  <script>
    const heroSpec = {json.dumps(hero_spec)};
    const scatterSpec = {json.dumps(scatter_spec)};
    const mapSpec = {json.dumps(map_spec)};

    vegaEmbed("#hero-dashboard", heroSpec, {{ actions: false }});
    vegaEmbed("#zoom-scatter", scatterSpec, {{ actions: false }});
    vegaEmbed("#state-map", mapSpec, {{ actions: false }});
  </script>
</body>
</html>
"""

    HTML_PATH.write_text(html)
    INDEX_PATH.write_text(html)
    print(f"Wrote {HTML_PATH}")
    print(f"Wrote {INDEX_PATH}")


if __name__ == "__main__":
    main()
