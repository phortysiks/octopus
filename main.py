'''Get the current Octopus Agile electricity prices for Area J'''
from datetime import datetime, timedelta
import requests

API_ENDPOINT = 'https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-J/standard-unit-rates/' #pylint: disable=line-too-long
current_price_lookup = requests.get(API_ENDPOINT, timeout=4).json()
current_datetime = datetime.now()
IS_SUMMERTIME = True
# print(current_datetime)
prices_list = current_price_lookup['results']

def normalise_datetime(date):
    '''Format the datetime string returned by Octopus to just a time string'''
    just_time = date[11:]
    no_z_or_secs = just_time[:-4]
    return no_z_or_secs


def convert_dt_string_to_dt_obj(datetime_string):
    '''Converts the datetime string recieved from the API to a datetime object'''
    if IS_SUMMERTIME:
        converted_string = (datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=1))
    else :
        converted_string = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ')
    return converted_string


def get_current_price():
    '''Get the current Octopus Agile electricity prices for Area J'''
    for window in prices_list:
        if (convert_dt_string_to_dt_obj(window['valid_from']) < current_datetime) and convert_dt_string_to_dt_obj(window['valid_to']) > current_datetime:
            current_price = window['value_inc_vat']
            rounded_price = round(current_price, 1)
            print(f"The current price is {rounded_price}p")


def get_cheapest_price():
    '''Get the cheapest price in the current day and show when it is'''
    cheapest_price = 40
    for window in prices_list:
        if window['value_inc_vat'] < cheapest_price and convert_dt_string_to_dt_obj(window['valid_to']) > current_datetime:
            cheapest_price = window['value_inc_vat']
            half_hour_window_start_time = convert_dt_string_to_dt_obj(window['valid_from'])

    print(f"The cheapest window starts at {datetime.strftime(half_hour_window_start_time, '%H:%M')}")
    print(f"The price is {round(cheapest_price, 1)}p")

get_cheapest_price()
