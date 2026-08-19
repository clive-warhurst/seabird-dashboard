# import package
import pandas as pd
import streamlit as st

# get a list of boolen columns in birds
birds_bool_cols = [
    "feeding",
    "sitting_on_water",
    "sitting_on_ice",
    "sitting_on_ship",
    "in_hand",
    "flying_past",
    "accompanying",
    "following_ship",
    "moulting",
    "naturally_feeding"
                  ]

def seabird_setup(setup = "raw"):
    
    # pandas reads from folder where script is
    
    beaufort_scale = pd.read_csv('data/beaufort_scale.csv')
    sea_states = pd.read_csv('data/sea_states.csv')
    time_series_ships = pd.read_csv('data/ships.csv', parse_dates=['date'], index_col='date')

    # if "raw" is specified then function returns the uncleaned data
    if setup == "raw":

        ships = pd.read_csv('data/ships.csv')

        birds = pd.read_csv(
            'data/birds.csv', 
            dtype = {
                'sex' : str,
                'feeding' : str,
                'sitting_on_water' : str,
                'sitting_on_ice' : str,
                'sitting_on_ship' : str,
                'in_hand' : str,
                'flying_past' : str,
                'accompanying' : str,
                'following_ship' : str,
                'moulting' : str,
                'naturally_feeding' : str
                    }
        )
        
        # for each element of the list, cast string to lower case and map to boolean values
        # then fill any NA values with False
        # then cast to a boolean
        for col in birds_bool_cols:
            birds[col] = (
                birds[col]
                .str.strip()
                .str.lower()
                .map({"true" : True, "false" : False})
                .fillna(False)
                .astype("boolean")
            )
        
        return beaufort_scale, birds, sea_states, ships, time_series_ships

    # but if "cleaned" is used then function imports the cleaned data
    elif setup == "cleaned":
        birds_cleaned = pd.read_parquet("data/birds_cleaned.parquet")
        ships_cleaned = pd.read_parquet("data/ships_cleaned.parquet")
        return beaufort_scale, birds_cleaned, sea_states, ships_cleaned, time_series_ships
    
    else:
        raise ValueError("seabird_setup failed - setup argument must be 'raw' or 'cleaned'.")

# function to merge birds and ships dataframes
def birds_ships_join(birds, ships):

    # join birds and ships dataframes on record_id
    birds_ships = pd.merge(birds, ships, how="left", on="record_id")

    # convert date variable to datetime
    birds_ships["date"] = pd.to_datetime(birds_ships["date"])
    # create a column that just shows the years
    birds_ships["year"] = birds_ships["date"].dt.year
    
    return birds_ships

# function to import data for the streamlit app
@st.cache_data
def seabird_streamlit_setup():

    birds_ships_joined = pd.read_parquet("data/birds_ships_joined.parquet")
    return birds_ships_joined