# import packages and functions
import streamlit as st
import plotly.express as px
import altair as alt

from scripts.chart_data import seabird_chart_data
from scripts.seabird_setup import seabird_streamlit_setup
from scripts.chart_functions import format_percent

# import data 
birds_ships_joined = seabird_streamlit_setup()

# run the additional cleaning function to create datasets needed for charting
(
    #h3_birds_ships,
    species_group_activity_percent,
    year_season_count_filled,
    species_group_season_percent,
    species_group_count
) = seabird_chart_data(birds_ships_joined)

# setup season_order
season_order = [
    "Spring",
    "Summer",
    "Autumn",
    "Winter"
]

# set the page config - adds a page title, cute page icon and a page title
st.set_page_config(
    page_title="Bird Sightings at Sea Explorer",
    page_icon=":penguin:",
    layout="wide",
)

# app features
st.title("Bird Sightings at Sea Explorer")
st.write("This dashboard uses data from Te Papa Tongarewa, the Museum of New Zealand.")

# let's make a bar of metrics
# this creates a horizontal container with a controlled width and gap
st.subheader("Overview")
st.write("")
with st.container(horizontal=True, width="content", gap="large"):
    st.metric(label="Seabird Sightings", value=len(birds_ships_joined.index))
    st.metric(label="Number of Species", value=len(birds_ships_joined["species_common_name"].unique()))
    st.metric(label="Most Common Species Group", value=birds_ships_joined["species_group"].mode()[0])
    st.metric(label="Most Common Season for Sightings", value=birds_ships_joined["season"].mode()[0])

# create a bit of vertical space
st.write("")

# create some columns for the 1st row of charts
col1, col2 = st.columns([2,5], gap="large", border=True)

# create the bar chart for overall Species Group sightings
# create an altair chart for this using the method-based syntax

chart_1 = (
    alt.Chart(species_group_count)
    .mark_bar()
    .encode(
        alt.X("sightings:Q").title("Number of Sightings"),
        alt.Y("species_group:N").sort("-x").title("Species Group"),
        tooltip=[
            alt.Tooltip("species_group:N").title("Species Group"),
            alt.Tooltip("sightings:Q").title("Number of Sightings").format(",")
        ]
    )
    .properties(height=450)
)

with col1:
    st.subheader("Sightings by Species Groups")
    st.altair_chart(chart_1, use_container_width=True)

# create a bar chart of the sightings by year by season
chart_2 = (
    alt.Chart(year_season_count_filled)
    .mark_bar()
    .encode(
        alt.X("year:O").title("Year").axis(labelAngle=0),
        alt.Y("sightings:Q").title("Number of Sightings"),
        alt.XOffset("season:O").sort(season_order),
        alt.Color("season:O").sort(season_order).legend(orient="bottom").title("Season"),
        tooltip=[
            alt.Tooltip("year:O").title("Year"),
            alt.Tooltip("season:O").title("Season"),
            alt.Tooltip("sightings:Q").title("Number of Sightings").format(",")
        ]
    )
    .properties(height=450)
)


with col2:
    st.subheader("Sightings over Time")
    st.altair_chart(chart_2)

# create the selectbox and plot the map
st.subheader("Species Group Summary")
st.write("")
st.write("Select a species group below to see data relating to that species group.")
st.write("")

species_group_sorted_list = sorted(birds_ships_joined["species_group"].unique())
species_group_options = ["All"] + species_group_sorted_list
selected_species_group = st.selectbox("Species Group Selector", species_group_options, width=250)
st.write("")

# create filters depending on what was selected!
if selected_species_group == "All":
    species_group_select_filter = birds_ships_joined
    mean_species_group_filter = species_group_activity_percent[species_group_activity_percent["species_group"] == "All"]
    species_group_seasonal_sightings_filter = species_group_season_percent[species_group_season_percent["species_group"] == "All"]
else:
    species_group_select_filter = birds_ships_joined[birds_ships_joined["species_group"] == selected_species_group]
    mean_species_group_filter = species_group_activity_percent[(species_group_activity_percent["species_group"] == selected_species_group) | (species_group_activity_percent["species_group"] == "All")]
    species_group_seasonal_sightings_filter = species_group_season_percent[(species_group_season_percent["species_group"] == selected_species_group) | (species_group_season_percent["species_group"] == "All")]

with st.container(horizontal=True, width="content", gap="large"):
    st.metric(
        label=f"{selected_species_group} Sightings", 
        value=len(species_group_select_filter.index),
        delta=f"{format_percent(len(species_group_select_filter) / len(birds_ships_joined), 1)} of total",
        delta_arrow="off",
        delta_color ="blue"
        )
    st.metric(label=f"Number of {selected_species_group} Species", value=len(species_group_select_filter["species_common_name"].unique()))
    st.metric(label=f"Most Common {selected_species_group} Species", value=species_group_select_filter["species_common_name"].mode()[0])

st.write("")

# set up a colour palette
palette = px.colors.qualitative.Plotly

# create a dictionary mapping species groups up to colours in the palette
color_map = {species_group: palette[i % len(palette)] for i, species_group in enumerate(species_group_options)}

# use plotly to create a scatter map of the filtered dataset
fig = px.scatter_map(
    species_group_select_filter,
    lat="latitude",
    lon="longitude",
    color = "species_group",
    color_discrete_map=color_map,
    category_orders ={"species_group": species_group_sorted_list},
    hover_data=["date", "species_common_name", "count"],
    zoom=3,
    height=450, 
    width=450
)

# update the map style
fig.update_layout(map_style="basic")

# create some columns for the 2nd row
col1, col2 = st.columns([2,5], gap="large", border = True)

with col1:
    # now create the bar chart for the selected species group
    st.subheader("Bird Behaviours")

    chart_3 = (
        alt.Chart(mean_species_group_filter)
        .mark_bar()
        .encode(
            alt.X("percentage:Q").title("Percentage"),
            alt.Y("activity:N").title("Bird Behaviour"),
            alt.YOffset("species_group:N").sort(species_group_options),
            alt.Color("species_group:N").sort(species_group_options).title("Species Group").legend(orient="bottom"),
            tooltip=[
                alt.Tooltip("species_group:N").title("Species Group"),
                alt.Tooltip("activity:N").title("Bird Behaviour"),
                alt.Tooltip("percentage:Q").title("Percentage")
            ]
        )
        .properties(height=450)
    )
    st.caption("Proportion of sightings with observed bird behaviour")
    st.altair_chart(chart_3)

    # and now add in the chart of species group by season
    st.subheader("Sightings by Season")

    chart_4 = (
        alt.Chart(species_group_seasonal_sightings_filter)
        .mark_bar()
        .encode(
            alt.X("season:O").sort(season_order).title("Season").axis(labelAngle=0),
            alt.Y("percentage:Q").title("Percentage"),
            alt.XOffset("species_group:N").sort(species_group_options),
            alt.Color("species_group:N").sort(species_group_options).title("Species Group").legend(orient="bottom"),
            tooltip=[
                alt.Tooltip("species_group:N").title("Species Group"),
                alt.Tooltip("season:O").title("Season"),
                alt.Tooltip("percentage:Q").title("Percentage")
            ]
        )
        .properties(height=450)
    )

    st.altair_chart(chart_4)

with col2:
    # finally, plot the chart
    st.subheader("Sightings Map")
    st.plotly_chart(fig, height = "stretch", width="stretch", config={"displayModeBar": False})  