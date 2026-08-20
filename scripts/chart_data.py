# this contains additional cleaning code that does not appear in 01_data_cleaning

import pandas as pd

activity_cols = [
    "feeding",
    "sitting_on_water",
    "flying_past",
    "accompanying",
    "following_ship"
    ]

season_order = [
    "spring",
    "summer",
    "autumn",
    "winter"
]

# define function to perform additional cleaning
# takes two dfs (birds and ships) as inputs
# returns four dfs as outputs for charting
def seabird_chart_data(birds_ships):

    # 1) create species_group_activity_proportion

    # start by getting the mean of the activity columns for each species group
    species_group_activity_proportion_wide = (
        birds_ships[["species_group"] + activity_cols]
        .groupby("species_group")
        .mean()
        .reset_index()
    )

    # then get the proportions for all birds
    # this gets a series, then converts it to a dataframe, before transposing it
    all_activity_proportion_wide = birds_ships[activity_cols].mean().to_frame().transpose()
    all_activity_proportion_wide["species_group"] = "all"

    # concatenate them together, ignoring the index
    species_group_activity_proportion_wide = pd.concat(
        [all_activity_proportion_wide, species_group_activity_proportion_wide], 
        ignore_index=True
        )

    # now melt the DataFrame to make it long rather than wide
    # it can now be used for charting!
    species_group_activity_proportion = species_group_activity_proportion_wide.melt(
        id_vars="species_group", 
        value_vars = activity_cols,
        var_name = "activity", 
        value_name = "proportion"
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

    # 3) create species_group_season_proportion

    # get data for species group by season
    species_group_season_proportion = (
        birds_ships
        .groupby("species_group")["season"]
        .value_counts(normalize=True)
        .reset_index(name="proportion")
    )

    # do the same for all
    all_season_proportion = (
        birds_ships["season"]
        .value_counts(normalize=True)
        .reset_index(name="proportion")
    )

    all_season_proportion["species_group"] = "all"

    # concatenate the two datasets together
    species_group_season_proportion = pd.concat(
        [species_group_season_proportion, all_season_proportion], 
        ignore_index=True
    )

    # 4) create species_group_count

    species_group_count = birds_ships["species_group"].value_counts().reset_index(name="sightings")

    return (
        species_group_activity_proportion,
        year_season_count,
        species_group_season_proportion,
        species_group_count
    )