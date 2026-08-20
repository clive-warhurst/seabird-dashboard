# this script contains other functions in use by bird_sightings_explorer.py, mostly for charting

# this function will format a percentage, to either 1dp or if it returns 0.0% then the nearest decimal place
def format_percent(value, decimal_places):

    # if value = 0 then return 0%
    if value == 0:
        return "0%"

    # else if the value would round to 0 then return as <0.1%
    elif round(value *100, decimal_places) < 0.1:
        return "<0.1%"

    # else if rounded percentage to number of decimal places = 100 then return 100%
    elif round(value * 100, decimal_places) == 100:
        return "100%"

    # else return rounded percentage
    else:
        return f"{round(value * 100, decimal_places)}%"