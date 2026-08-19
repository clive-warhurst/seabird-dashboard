# Seabird Dashboard

An interactive Streamlit dashboard exploring seabird sighting records,
showing distribution by species group, seasonal patterns, and observation
locations.

This dashboard uses data sourced from Te Papa. More information is available here: https://www.tepapa.govt.nz/learn/research/datasets/sea-observations-seabirds-dataset. 

More information about the data is available at this tidytuesday repo: https://github.com/rfordatascience/tidytuesday/tree/main/data/2026/2026-04-14.

The dashboard is currently hosted on Streamlit Community Cloud here: https://seabird-dashboard.streamlit.app/. 

## Data

The original data comes from the tidytuesday repository.

I have cleaned this data to create `data/birds_ships_joined.parquet` — see `01_data_cleaning.ipynb` for the cleaning steps.

## Code

`bird_sightings_explorer.py` will import `data/ships_cleaned.parquet` and launch the Streamlit dashboard.

`scripts/seabird_setup.py` and `scripts/chart_data.py` prepare the imported data for use in the dashboard.

## Requirements

Python 3.14
