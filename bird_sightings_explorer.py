# import packages and functions
import streamlit as st
import plotly.express as px

from scripts.chart_data import seabird_chart_data
from scripts.seabird_setup import seabird_streamlit_setup
from scripts.chart_functions import format_percent

# import data 
birds_ships_joined = seabird_streamlit_setup()

# run the additional cleaning function to create datasets needed for charting
(species_group_activity_proportion,
    year_season_count,
    species_group_season_proportion,
    species_group_count
) = seabird_chart_data(birds_ships_joined)

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
with col1:
    st.subheader("Species Groups")
    st.bar_chart(
        species_group_count, 
        x="species_group", 
        y="sightings",
        horizontal=True,
        x_label = "Species Group",
        y_label = "Number of Sightings",
        height= 450,
        width = "stretch",
        sort = "-sightings"
    )

# create a bar chart of the sightings by year by season
with col2:
    st.subheader("Sightings over Time")
    st.bar_chart(
        year_season_count,
        x="year",
        y="sightings",
        color="season",
        stack=False,
        x_label = "Year",
        y_label = "Number of Sightings",
        height = 450,
        width = "stretch",
    )

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
    mean_species_group_filter = species_group_activity_proportion[species_group_activity_proportion["species_group"] == "All"]
    species_group_seasonal_sightings_filter = species_group_season_proportion[species_group_season_proportion["species_group"] == "All"]
else:
    species_group_select_filter = birds_ships_joined[birds_ships_joined["species_group"] == selected_species_group]
    mean_species_group_filter = species_group_activity_proportion[(species_group_activity_proportion["species_group"] == selected_species_group) | (species_group_activity_proportion["species_group"] == "All")]
    species_group_seasonal_sightings_filter = species_group_season_proportion[(species_group_season_proportion["species_group"] == selected_species_group) | (species_group_season_proportion["species_group"] == "All")]

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
    st.caption("Proportion of sightings with observed bird behaviour")
    st.bar_chart(
        mean_species_group_filter,
        x="activity",
        y="proportion",
        color="species_group",
        stack=False,
        horizontal=True,
        x_label = "Bird Behaviour",
        y_label = "Proportion of Sightings",
        height = 450,
        width = 450
    )

    # and now add in the chart of species group by season
    st.subheader("Sightings by Season")
    st.bar_chart(
        species_group_seasonal_sightings_filter,
        x="season",
        y="proportion",
        color="species_group",
        stack=False,
        x_label = "Season",
        y_label = "Proportion of Sightings",
        height = 450,
        width = 450
    )

with col2:
    # finally, plot the chart
    st.subheader("Sightings Map")
    st.plotly_chart(fig, height = "stretch", width="stretch", config={"displayModeBar": False})  