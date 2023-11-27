'''Module providing functionality to store Octopus Agile prices'''
import datetime as dt
import os
from dotenv import load_dotenv
import psycopg2
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()
auth = HTTPBasicAuth(os.getenv('API_KEY'), '')

BASE_URL = 'https://api.octopus.energy/v1/'
ELEC_METER_ID = os.getenv("ELEC_METER_ID")
ELEC_SERIAL_NUM = os.getenv("ELEC_SERIAL_NUM")
GAS_METER_ID = os.getenv("GAS_METER_ID")
GAS_SERIAL_NUM = os.getenv("GAS_SERIAL_NUM")
AGILE_AREA = os.getenv("AGILE_AREA")

AGILE_PRICE_REQUEST_URL = (
    BASE_URL + 'products/AGILE-FLEX-22-11-25/electricity-tariffs/' +
    AGILE_AREA + '/standard-unit-rates/'
)

ELEC_CONSUMPTION_REQUEST_URL = (
    BASE_URL + 'electricity-meter-points/' + ELEC_METER_ID +
    '/meters/' + ELEC_SERIAL_NUM + '/consumption/'
)

GAS_CONSUMPTION_REQUEST_URL = (
    BASE_URL + 'gas-meter-points/' + GAS_METER_ID +
    '/meters/' + GAS_SERIAL_NUM + '/consumption/'
)

def convert_datetime(datetime_string):
    '''Convert a datetime string to a datetime object'''
    datetime_obj = dt.datetime.fromisoformat(datetime_string[:-1])
    utc_obj = datetime_obj.replace(tzinfo=dt.timezone.utc)
    return utc_obj

agile_rates_res = requests.get(AGILE_PRICE_REQUEST_URL, auth=auth, timeout=4).json()
agile_rates_data = agile_rates_res['results']

elec_res = requests.get(ELEC_CONSUMPTION_REQUEST_URL, auth=auth, timeout=10).json()
elec_consumption_data = elec_res['results']

gas_res = requests.get(GAS_CONSUMPTION_REQUEST_URL, auth=auth, timeout=10).json()
gas_consumption_data = gas_res['results']

connection = psycopg2.connect(
    user = os.getenv("user"),
    password = os.getenv("password"),
    host = os.getenv("host"),
    port = os.getenv("port"),
    database = os.getenv("database")
)

cursor = connection.cursor()

for entry in agile_rates_data:
    cursor.execute("""
        INSERT INTO rates_and_consumption (time_interval_start, time_interval_end, agile_elec_price)
        VALUES (%s, %s, %s)
        ON CONFLICT (time_interval_start)
        DO UPDATE
        SET agile_elec_price = %s;
    """, (convert_datetime(entry['valid_from']),
            convert_datetime(entry['valid_to']),
            entry['value_inc_vat'],
            entry['value_inc_vat'])
            )
 
for entry in elec_consumption_data:
    cursor.execute("""
        INSERT INTO rates_and_consumption (time_interval_start, time_interval_end, elec_consumption)
        VALUES (%s, %s, %s)
        ON CONFLICT (time_interval_start)
        DO UPDATE
        SET elec_consumption = %s;
    """, (convert_datetime(entry['interval_start']),
          convert_datetime(entry['interval_end']),
          entry['consumption'], entry['consumption'])
    )

for entry in gas_consumption_data:
    cursor.execute("""
        INSERT INTO rates_and_consumption (time_interval_start, time_interval_end, gas_consumption)
        VALUES (%s, %s, %s)
        ON CONFLICT (time_interval_start)
        DO UPDATE
        SET gas_consumption = %s;
    """, (convert_datetime(entry['interval_start']),
          convert_datetime(entry['interval_end']),
          entry['consumption'], entry['consumption'])
    )

connection.commit()
cursor.close()
connection.close()