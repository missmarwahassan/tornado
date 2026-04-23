import json
from pathlib import Path


WORKDIR = Path("/Users/marwahas/Documents/Codex/2026-04-21-files-mentioned-by-the-user-narrative")
NOTEBOOK_PATH = WORKDIR / "tornado_story_dashboard.ipynb"
HTML_PATH = WORKDIR / "tornado_story_dashboard.html"
INDEX_PATH = WORKDIR / "index.html"


def load_notebook_namespace() -> dict:
    nb = json.loads(NOTEBOOK_PATH.read_text())
    ns: dict = {}
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        exec(compile(src, f"<cell {i}>", "exec"), ns)
    return ns


def main() -> None:
    ns = load_notebook_namespace()
    alt = ns["alt"]
    map_spec = ns["state_map"].to_dict()
    state_metrics = ns["state_metrics"]
    region_palette = ns["region_palette"]
    paper = ns["paper"]
    ink = ns["ink"]
    base_config = ns["base_config"]
    timeline = ns["timeline"]
    heatmap = ns["heatmap"]
    state_line = ns["state_line"]
    state_decades = ns["state_decades"]

    public_hero = (
        (
            timeline.properties(width=1120, height=110)
            & heatmap.properties(width=1080, height=650)
            & (
                state_line.properties(width=540, height=170)
                | state_decades.properties(width=540, height=170)
            )
        )
        .resolve_scale(color="independent", size="independent")
        .configure(**base_config)
        .configure_legend(
            orient="bottom",
            direction="horizontal",
            gradientLength=320,
            gradientThickness=14,
            titleAnchor="start",
            labelLimit=120,
        )
    )
    hero_spec = public_hero.to_dict()

    community_scatter_base = (
        alt.Chart(state_metrics)
        .mark_circle(opacity=0.88, stroke=paper, strokeWidth=1.3)
        .encode(
            x=alt.X("avg_annual:Q", title="Average annual tornadoes (1951-2019)"),
            y=alt.Y("growth_delta:Q", title="Increase from 1950s average to 2010s average"),
            size=alt.Size("total_count:Q", title="Total tornadoes"),
            color=alt.Color("region:N", scale=alt.Scale(range=region_palette), title="Region"),
            tooltip=[
                alt.Tooltip("States:N", title="State"),
                alt.Tooltip("region:N", title="Region"),
                alt.Tooltip("avg_annual:Q", title="Avg annual", format=".1f"),
                alt.Tooltip("growth_delta:Q", title="Growth", format=".1f"),
                alt.Tooltip("volatility:Q", title="Volatility", format=".1f"),
                alt.Tooltip("total_count:Q", title="Total tornadoes", format=".0f"),
            ],
        )
    )

    hover_state = alt.selection_point(
        name="hover_state",
        fields=["States"],
        on="pointerover",
        nearest=True,
        empty=False,
    )

    community_scatter_labels = (
        alt.Chart(state_metrics)
        .add_params(hover_state)
        .mark_text(align="left", dx=8, dy=-5, fontSize=11, color=ink)
        .encode(
            x="avg_annual:Q",
            y="growth_delta:Q",
            text="States:N",
            opacity=alt.condition(hover_state, alt.value(1), alt.value(0)),
        )
    )

    community_scatter = (
        (community_scatter_base + community_scatter_labels)
        .properties(
            width=980,
            height=580,
            title=alt.TitleParams(
                text="Exposure vs. Acceleration",
                subtitle="This view is zoomable and pannable. Drag to pan, use your trackpad or mouse wheel to zoom, and double-click to reset.",
                anchor="start",
            ),
        )
        .interactive()
        .configure(**base_config)
    )

    scatter_spec = community_scatter.to_dict()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tornado Geography Project</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    :root {{
      --paper: #f6f1e7;
      --ink: #1f1d1a;
      --accent: #e4572e;
      --grid: #d8ccb8;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "Georgia", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(228,87,46,0.14), transparent 24%),
        radial-gradient(circle at 15% 10%, rgba(243,167,18,0.11), transparent 18%),
        linear-gradient(180deg, #fbf8f1 0%, var(--paper) 100%);
      line-height: 1.5;
    }}
    a {{
      color: var(--accent);
    }}
    main {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 0 24px 80px;
    }}
    h1 {{
      margin: 0 0 10px;
      max-width: 1100px;
      font-size: clamp(2.6rem, 5vw, 5.2rem);
      line-height: 0.95;
      letter-spacing: -0.03em;
    }}
    .hero {{
      padding-top: 42px;
    }}
    .kicker {{
      margin: 0 0 12px;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: rgba(31,29,26,0.7);
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: clamp(1.6rem, 2.4vw, 2.4rem);
      letter-spacing: -0.02em;
    }}
    .lede {{
      max-width: 930px;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 1.08rem;
      color: rgba(31,29,26,0.84);
      margin-bottom: 30px;
    }}
    .panel {{
      background: rgba(255,255,255,0.54);
      border: 1px solid rgba(216,204,184,0.8);
      border-radius: 22px;
      padding: 24px 22px;
      box-shadow: 0 20px 56px rgba(76, 61, 46, 0.08);
      margin-top: 22px;
      overflow: hidden;
    }}
    .section-copy {{
      max-width: 760px;
      margin: 4px 0 14px;
      font-family: Helvetica, Arial, sans-serif;
      color: rgba(31,29,26,0.82);
    }}
    .split {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
      gap: 18px;
      align-items: start;
    }}
    .callout {{
      background: rgba(255,255,255,0.58);
      border: 1px solid rgba(216,204,184,0.8);
      border-radius: 18px;
      padding: 18px 18px 16px;
      font-family: Helvetica, Arial, sans-serif;
    }}
    .callout p {{
      margin: 0 0 10px;
      color: rgba(31,29,26,0.82);
    }}
    .callout p:last-child {{
      margin-bottom: 0;
    }}
    .vega-embed summary {{
      display: none;
    }}
    .vega-embed {{
      width: 100%;
    }}
    .vega-embed > div {{
      width: 100%;
    }}
    .section {{
      margin-top: 28px;
    }}
    .overview {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 20px;
    }}
    .overview-card {{
      background: rgba(255,255,255,0.58);
      border: 1px solid rgba(216,204,184,0.8);
      border-radius: 18px;
      padding: 18px 18px 16px;
      font-family: Helvetica, Arial, sans-serif;
    }}
    .overview-card h3 {{
      margin: 0 0 8px;
      font-size: 1rem;
      color: var(--ink);
    }}
    .overview-card p {{
      margin: 0;
      color: rgba(31,29,26,0.82);
      font-size: 0.95rem;
    }}
    footer {{
      margin-top: 30px;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 0.92rem;
      color: rgba(31,29,26,0.7);
    }}
    @media (max-width: 980px) {{
      .split {{
        grid-template-columns: 1fr;
      }}
      .overview {{
        grid-template-columns: 1fr;
      }}
      .panel {{
        padding: 18px 14px;
      }}
      main {{
        padding: 0 14px 64px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <p class="kicker">Final Narrative Visualization Project</p>
      <h1>Tornado Geography Beyond Classic Tornado Alley</h1>
      <p class="lede">
        This site presents our team’s final narrative visualization project on tornado activity across the United States from 1951 to 2019.
        Our goal is to show that the national tornado story is not only about a fixed Plains corridor, but also about regional change, concentration, and expansion over time.
      </p>
      <div class="overview">
        <div class="overview-card">
          <h3>Project Goal</h3>
          <p>Show how tornado activity accumulates, shifts, and intensifies across states over time through an interactive narrative rather than a single static map.</p>
        </div>
        <div class="overview-card">
          <h3>What To Look For</h3>
          <p>Compare the long-run dominance of the Great Plains with the growing prominence of the Southeast and the changing rank order of states across decades.</p>
        </div>
        <div class="overview-card">
          <h3>How To Read</h3>
          <p>Start with the main dashboard, then zoom into the exposure chart for smaller states, and finally use the map slider to inspect year-by-year geographic change.</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>1. National Pattern and State Detail</h2>
      <p class="section-copy">
        This opening dashboard is the main entry point for the project. Use the national pulse to focus an era, read the pressure wall as a state-by-year texture of activity, and compare the selected state’s long-run trend with its decade totals.
      </p>
      <div class="panel">
        <div id="hero-dashboard"></div>
      </div>
    </section>

    <section class="section">
      <h2>2. Exposure and Acceleration</h2>
      <p class="section-copy">
        This dedicated view isolates the relationship between long-run exposure and recent growth. It gives the smaller-state cluster enough space to inspect closely, which is difficult to do in a compressed multi-panel dashboard.
      </p>
      <div class="split">
        <div class="panel">
          <div id="zoom-scatter"></div>
        </div>
        <aside class="callout">
          <p><strong>Reading tip</strong></p>
          <p>States far to the right have high long-run exposure. States higher up have increased more sharply from the 1950s to the 2010s.</p>
          <p>The quiet cluster in the lower-left matters too: these are states with comparatively low annual averages and limited long-run growth, and they become much easier to examine once you zoom in.</p>
          <p>Double-click inside the chart to reset the zoom.</p>
        </aside>
      </div>
    </section>

    <section class="section">
      <h2>3. State-by-State Geographic Shift</h2>
      <p class="section-copy">
        The slider map works as a companion view to the analytical panels above. Move through the years to watch how the center of tornado activity broadens, spikes, and migrates across the country.
      </p>
      <div class="panel">
        <div id="state-map"></div>
      </div>
    </section>

    <section class="section">
      <h2>4. Project Notes</h2>
      <div class="overview">
        <div class="overview-card">
          <h3>Dataset</h3>
          <p>The visualizations are built from annual state-level tornado counts spanning 1951 to 2019, allowing both long-run comparisons and decade-level narrative framing.</p>
        </div>
        <div class="overview-card">
          <h3>Narrative Choice</h3>
          <p>We structured the project as a sequence: first establish the national pattern, then isolate a key analytical relationship, and finally provide a geographic playback view.</p>
        </div>
        <div class="overview-card">
          <h3>Team Presentation Use</h3>
          <p>This format is designed to support a final class presentation as well as a browsable standalone web page that preserves Altair interactivity.</p>
        </div>
      </div>
    </section>

    <footer>
      Export generated from the notebook and dataset in this project folder. For GitHub Pages, publish this file as <code>index.html</code>.
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
