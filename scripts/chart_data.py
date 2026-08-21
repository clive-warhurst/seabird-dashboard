# this contains additional cleaning code that does not appear in 01_data_cleaning

import pandas as pd
import h3

activity_cols = [
    "feeding",
    "sitting_on_water",
    "flying_past",
    "accompanying",
    "following_ship"
    ]

season_order = [
    "Spring",
    "Summer",
    "Autumn",
    "Winter"
]

# define function to perform additional cleaning
# takes two dfs (birds and ships) as inputs
# returns four dfs as outputs for charting
def seabird_chart_data(birds_ships):

    # 1) create species_group_activity_percent

    # start by getting the mean of the activity columns for each species group
    species_group_activity_percent_wide = (
        birds_ships[["species_group"] + activity_cols]
        .groupby("species_group")
        .mean()
        .reset_index()
    )

    # then get the proportions for all birds
    # this gets a series, then converts it to a dataframe, before transposing it
    all_activity_percent_wide = birds_ships[activity_cols].mean().to_frame().transpose()
    all_activity_percent_wide["species_group"] = "All"

    # concatenate them together, ignoring the index
    species_group_activity_percent_wide = pd.concat(
        [all_activity_percent_wide, species_group_activity_percent_wide], 
        ignore_index=True
        )

    # now melt the DataFrame to make it long rather than wide
    # it can now be used for charting!
    species_group_activity_percent = species_group_activity_percent_wide.melt(
        id_vars="species_group", 
        value_vars = activity_cols,
        var_name = "activity", 
        value_name = "percentage"
        )

    # convert to percentage and round
    species_group_activity_percent["percentage"] = (species_group_activity_percent["percentage"] * 100).round(1)

    # now capitalise the activity column values and replace "_" with " "
    species_group_activity_percent["activity"] = (
        species_group_activity_percent["activity"]
        .str.replace("_", " ")
        .str.title()
        )

    # 2) create year_season_count

    # firstly, ensure that season is a categorical series and sort
    birds_ships["season"] = pd.Categorical(birds_ships["season"], categories=season_order, ordered=True)

    # now use groupby to get a count of the sightings per group, allowing groups with 0 sightings to be shown as well
    year_season_count = (
        birds_ships
        .groupby(["year", "season"], observed=False)
        .size()
        .reset_index(name="sightings")
    )

    # get all years of data, including the gap into a list
    all_years = range(1969, 1991)

    # create a product of missing years and seasons using pd.MultiIndex.from_product()
    all_years_index = pd.MultiIndex.from_product(
        [all_years, season_order], names=["year", "season"]
        )

    # then add this to the year_season_count dataframe by setting an index,
    # re-indexing on the missing years,
    # and then resetting the index

    year_season_count_filled = (
        year_season_count
        .set_index(["year", "season"])
        .reindex(all_years_index, fill_value = 0)
        .reset_index()
    )

    # 3) create species_group_season_percent

    # get data for species group by season
    species_group_season_percent = (
        birds_ships
        .groupby("species_group")["season"]
        .value_counts(normalize=True)
        .reset_index(name="percentage")
    )

    # do the same for all
    all_season_percent = (
        birds_ships["season"]
        .value_counts(normalize=True)
        .reset_index(name="percentage")
    )

    all_season_percent["species_group"] = "All"

    # concatenate the two datasets together
    species_group_season_percent = pd.concat(
        [species_group_season_percent, all_season_percent], 
        ignore_index=True
    )

    # convert to percentage
    species_group_season_percent["percentage"] = (species_group_season_percent["percentage"] * 100).round(1)

    # 4) create species_group_count

    species_group_count = birds_ships["species_group"].value_counts().reset_index(name="sightings")

    # setup data for the map (chart 5)
    
    # this gets an h3 cell ref for each row in the dataframe
    #h3_data = birds_ships.copy()
    #h3_data["h3_cell"] = h3_data.apply(
    #    lambda row: h3.latlng_to_cell(row["latitude"], row["longitude"], 4),
    #    axis=1
    #)

    #print(h3_data["h3_cell"].nunique())
    #print(h3_data["h3_cell"].value_counts().head())

    return (
        #h3_data,
        species_group_activity_percent,
        year_season_count_filled,
        species_group_season_percent,
        species_group_count
    )