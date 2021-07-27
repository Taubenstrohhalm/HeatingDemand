import requests
import json
import pandas as pd
from pathlib import Path

data_path = Path("input")

def get_tmy_data(latitude, longitude):
    """Load weather - typical meterological year(TMY) data from PVGIS
    Parameters
    ----------
    latitude : float
        Latitude [decimal degrees]
    longitude : float
        Longitude [decimal degrees]
    Returns
    -------
    content of the requests.response object containing weather data
    """
    url = 'https://re.jrc.ec.europa.eu/api/tmy?lat='+str(latitude)+'&lon='+str(longitude)+'&outputformat=json'
    response = requests.get(url)
    return response.content

def save_tmy_data(data, filename, filepath = data_path):
    """Save the weather data in a json file.
    Parameters
    ----------
    data : content of the requests.response object
        content of the requests.response object containing weather data
    filename : str
        filename of the tmy file
    filepath : pathlib Path
        filepath where the json file should be saved
    """
    Path(filepath , filename + ".json").write_bytes(data)


def read_tmy_data(filename, filepath = data_path):
    """Read the weather data from a json file and write to pandas dataframe.
    Parameters
    ----------
    filename : str
        filename of the tmy file
    filepath : pathlib Path
        filepath where the json file is saved
    Returns
    -------
    pandas df containing
    - time (index, datetime): Date & time (UTC)
    - T2m (pandas column, float): Dry bulb (air) temperature [°C]
    - RH (pandas column, float):  Relative Humidity [%]
    - G(h) (pandas column, float): Global horizontal irradiance [W/m2]
    - Gb(n) (pandas column, float): Direct (beam) irradiance [W/m2]
    - Gd(h) (pandas column, float): Diffuse horizontal irradiance [W/m2]
    - IR(h) (pandas column, float): Infrared radiation downwards [W/m2]
    - WS10m (pandas column, float): Windspeed [m/s]
    - WD10m (pandas column, float): Wind direction [°]
    - SP (pandas column, float): Surface (air) pressure [Pa]
    Notes
    -----
    A typical meteorological year (TMY) is a set of meteorological data with data values 
    for every hour in a year for a given geographical location. The data are selected from hourly 
    data in a longer time period (normally 10 years or more). 
    The TMY is generated in PVGIS following the procedure described in ISO 15927-4. [1]_
    References
    ----------
    .. [1] https://ec.europa.eu/jrc/en/PVGIS/tools/tmy
    """

    filename = Path(filepath , filename + ".json")
    with open(filename, 'r') as file:
        data = json.load(file)
    data_outputs_hourly = data['outputs']['tmy_hourly']
    df = pd.DataFrame.from_dict(data_outputs_hourly)
    df.set_index('time(UTC)', inplace = True)
    df.index = pd.to_datetime(df.index, format = '%Y%m%d:%H%M')
    return df