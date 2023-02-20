'''Get the current Octopus Agile electricity prices for Area J'''
import datetime
import requests

API_ENDPOINT = 'https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-J/standard-unit-rates/' #pylint: disable=line-too-long
current_price_lookup = requests.get(API_ENDPOINT, timeout=4).json()
current_datetime = datetime.datetime.now().isoformat()
prices_list = current_price_lookup['results']

def normalise_datetime(date):
    '''Format the datetime string returned by Octopus to just a time string'''
    just_time = date[11:]
    no_z_or_secs = just_time[:-4]
    return no_z_or_secs

def get_current_price():
    '''Get the current Octopus Agile electricity prices for Area J'''
    for window in prices_list:
        if (window['valid_from'] < current_datetime) and window['valid_to'] > current_datetime:
            current_price = window['value_inc_vat']
            rounded_price = round(current_price, 1)
            print(f"The current price is {rounded_price}p")

def get_cheapest_price():
    '''Get the cheapest price in the current day and show when it is'''
    cheapest_price = 40
    for window in prices_list:
        if window['value_inc_vat'] < cheapest_price and window['valid_to'] > current_datetime:
            cheapest_price = window['value_inc_vat']
            half_hour_window_start_time = window['valid_from']

    print(f"The cheapest window starts at {normalise_datetime(half_hour_window_start_time)}")
    print(f"The price is {round(cheapest_price, 1)}p")

get_cheapest_price()
