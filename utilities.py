import requests
import json
import pandas as pd

def get_tmy_data(latitude, longitude):
    '''
    this function returns a pandas dataframe with the env data from the pvgis database
    '''
    url = 'https://re.jrc.ec.europa.eu/api/tmy?lat='+str(latitude)+'&lon='+str(longitude)+'&outputformat=json'
    
    response = requests.get(url)
    data = json.loads(response.text)
    data_outputs_hourly = data['outputs']['tmy_hourly']
    df = pd.DataFrame.from_dict(data_outputs_hourly)
    df.set_index('time(UTC)', inplace = True)
    df.index = pd.to_datetime(df.index, format = '%Y%m%d:%H%M')
    return df