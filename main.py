# -*- coding: utf-8 -*-
"""
Created on Tue May 25 10:11:00 2021

@author: Lukas
"""

import pandas as pd

from utilities import get_tmy_data
from physics import heatflow_transmission, heatflow_ventilation_infiltration

#%% COMFORT LEVELS 

temp_in_low = 20 # [°C] lowest allowed temperature, if temperature drops below this level, heating is required
temp_in_high = 26 # [°C] highest allowed temperature, if temperature goes above this level, cooling is required
n_ventilation = 0.25 # [1/h] ventilation rate, _ air exchanges per hour
n_infiltration = 0.25 # [1/h] infiltration rate, _ air exchanges per hour

#%% BUILDING INFORMATION, GEOMETRY AND MATERIAL PROPERTIES

# Location of the building
latitude = 48
longitude = 8

# Volume of the building
volume = 100 # m^3 

# Opaque building envelope areas 
walls = {
    'wall' : {'area' : 30, 'u_value' : 2},
    'roof' : {'area' : 20, 'u_value' : 2},
    'basement' :{'area' : 10, 'u_value' : 2},
}

# dictionary of window areas facing in the same direction 
# {area [m^2], u_value [W/mK], g_value [-], tilt and azimuth [deg]}
windows = {
    'north' : {'area' : 0, 'u_value' : 2, 'g_value' : 0.6, 'tilt' : 90, 'azimuth' : 0},
    'east' : {'area' : 2, 'u_value' : 2, 'g_value' : 0.6, 'tilt' : 90, 'azimuth' : 90},
    'south': {'area' : 3, 'u_value' : 2, 'g_value' : 0.6, 'tilt' : 90, 'azimuth' : 180},
    'west' : {'area' : 2, 'u_value' : 2, 'g_value' : 0.6, 'tilt' : 90, 'azimuth' : 270},
}

# %% LOAD WEATHER DATA - tmy for now

# timezone information is needed for the calculation of sun angles by pvlib
tz = 'Europe/Berlin' # maybe the timezone can be set according to lat, long

#df = get_tmy_data(latitude=latitude, longitude=longitude)
df = get_tmy_data(latitude=latitude, longitude=longitude)[['T2m','G(h)','Gb(n)','Gd(h)']]
#print(df.head())

# temp_out = 10 # °C
temp_ground = 8 # °C # some formula needed to calc ground temp, from ambient temp


#%% TRANSMISSION LOSSES
df_trans = pd.DataFrame() # create df for all the transmission heatflows
df['Qdot_trans_opaque [W]'] = 0 # create empty column in main df for sum of opaque trans heatflows 
# Opaque building elements (basement, outside walls, roof)
for wall, property in walls.items():
    if wall == 'basement':
        # The basement walls outside temperature is the ground temperature
        df_trans['Qdot_trans_basement [W]'] =  heatflow_transmission(
            area = property['area'], 
            u_value = property['u_value'],
            temp_in = temp_in_low, 
            temp_out = temp_ground,
        )
    else:
        # All other walls have the ambient air temperature as outside temperature
        df_trans['Qdot_trans_' + wall + ' [W]'] = heatflow_transmission(
            u_value = property['u_value'],
            area = property['area'],
            temp_in = temp_in_low,
            temp_out = df['T2m'],
        )
    df['Qdot_trans_opaque [W]'] += df_trans['Qdot_trans_' + wall + ' [W]']
# Transparent building elements (windows)
df['Qdot_trans_windows [W]'] = 0 # create empty column in main df for sum of window trans heatflows
for window, properties in windows.items():
    df_trans['Qdot_trans_win_' + window + ' [W]'] = heatflow_transmission(
        u_value=properties['u_value'],
        area=properties['area'],
        temp_in=temp_in_low,
        temp_out=df['T2m'],
    )
    df['Qdot_trans_windows [W]'] += df_trans['Qdot_trans_win_' + window + ' [W]']
print(df_trans.head())


#%% calculate heatflow due to infiltration and ventilation

df['Qdot_vent [W]'] = heatflow_ventilation_infiltration(
    volume = volume,
    n_vent = n_ventilation,
    n_inf = n_infiltration,
    temp_in = temp_in_low,
    temp_out = df['T2m']
)


print(df.head())
'''
# %% SOLAR GAINS

# calculate solar angles
from pvlib.solarposition import get_solarposition
tz = 'Europe/Berlin'
lat, lon = 48, 8 # latitude and longitude of the buildings location

# this needs to be replaced by the index of the timeseries of our weather data
# the index has to be in python datetime format
times = pd.date_range('2019-01-01 00:00:00', '2020-01-01', closed='left',
                      freq='H', tz=tz)

solpos = get_solarposition(times, lat, lon)

print(solpos.head())

# calculate total (beam + diffuse_sky + diffuse_ground) irradiation on windows
from pvlib.irradiance import get_total_irradiance


# calculate solar gains
def heatflow_solar_gains(area, irradiation, g_value):
    Qdot = area * irradiation * g_value
    return Qdot

Qdot_sol = 0 # initialize heatflow due to solar gains [W]
for window, property in windows.items():
    Qdot_win = heatflow_solar_gains(property['area'], irradiation['window'], property['g_value'])
    print(f'{window=}: {Qdot_win=}')


'''