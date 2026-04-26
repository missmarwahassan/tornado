# The Changing Geography of Tornado Risk

An interactive narrative visualization project exploring how tornado activity is distributed across the United States from 1951 to 2019. The project combines a linked Altair dashboard, a zoomable comparison view, and a year-by-year state map to show that the tornado story is not only about a fixed Great Plains corridor, but also about regional change over time.

## Live Site

- GitHub Pages: [https://missmarwahassan.github.io/tornado/](https://missmarwahassan.github.io/tornado/)
- Repository: [https://github.com/missmarwahassan/tornado](https://github.com/missmarwahassan/tornado)

## Course And Team

- Course: `SI 649: Information Visualization`
- Team: `Marwa Hassan`, `Hassan Beydoun`, `Maryam Romio`

## Project Overview

This project was built as a final narrative visualization project focused on how tornado geography is changing in the United States.

The main argument of the site is that tornado activity is not only persistent, but also shifting, spreading, and becoming less confined to the traditional Great Plains core often associated with Tornado Alley.

The site is structured as a guided story:

1. `National Pattern and State Detail`
   A linked dashboard showing the national pulse, the tornado pressure wall, and selected-state detail views.
2. `Exposure and Acceleration`
   A zoomable scatterplot comparing long-run exposure with recent growth across states.
3. `State-by-State Geographic Shift`
   A choropleth map with a year slider to show how tornado activity changes geographically over time.
4. `What This Means`
   A concluding interpretation of how these shifts matter for preparedness, infrastructure, and risk.
5. `Project Notes`
   Supporting narrative context drawn from team project materials.

## Data

- Primary dataset: `Tornado_Data_Count.csv`
- Coverage: annual tornado counts by U.S. state, `1951-2019`

The visualizations focus on state-level counts over time, making the project well suited for narrative questions about concentration, growth, and geographic change.

## Repository Structure

- `index.html`
  GitHub Pages entry point for the published site.
- `tornado_story_dashboard.html`
  Standalone HTML export of the project site.
- `tornado_story_dashboard.ipynb`
  Main working notebook for analysis and visualization.
- `present_tornado_story_dashboard.ipynb`
  Presentation-oriented notebook version.
- `build_tornado_notebook.py`
  Script that generates the notebook programmatically.
- `export_tornado_html.py`
  Script that exports the notebook visuals into the final HTML site.
- `Tornado_Data_Count.csv`
  State-by-year tornado count dataset used by the project.

## How To View The Project

### Option 1: View the published site

Open the GitHub Pages site:

[https://missmarwahassan.github.io/tornado/](https://missmarwahassan.github.io/tornado/)

### Option 2: Open the local HTML file

Open `index.html` in a browser.

Note: the HTML loads Vega libraries from a CDN, so an internet connection is recommended for full interactivity.

### Option 3: Work in the notebook

Open `tornado_story_dashboard.ipynb` in Jupyter or VS Code to inspect and modify the analysis directly.

## Regenerating The Project Files

If you edit the notebook-generation logic:

```bash
python3 build_tornado_notebook.py
```

If you want to regenerate the final HTML site:

```bash
python3 export_tornado_html.py
```

## Features

- Linked dashboard interactions
- Timeline brushing
- State selection across coordinated views
- Zoomable exposure vs. acceleration chart
- Year-slider U.S. tornado activity map
- GitHub Pages-ready HTML export

## Project Framing

This project challenges the long-standing idea of a fixed Tornado Alley. While the Great Plains remain a central region of activity, the data suggests a broader redistribution of tornado risk, especially toward the Southeast and other regions outside the traditional historical core.

The project emphasizes not just total tornado counts, but also:

- where tornadoes are happening
- how consistently they occur
- how much activity has changed over time

## Future Improvements

- Add additional contextual annotations for notable years or regional shifts
- Incorporate severity or impact variables such as fatalities or outbreak magnitude
- Extend the project with preparedness or infrastructure data, such as storm shelter access or warning system coverage

## Credits

Built using:

- Python
- Pandas
- Altair / Vega-Lite
- GitHub Pages
