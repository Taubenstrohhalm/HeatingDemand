# -*- coding: utf-8 -*-
"""
Created on Tue May 25 10:11:00 2021

@author: Lukas
"""

import pandas as pd
from pvlib.solarposition import get_solarposition
from pvlib.irradiance import get_total_irradiance

import utilities
#from utilities import get_tmy_data
from physics import heatflow_transmission, heatflow_ventilation_infiltration, heatflow_solar_gains

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

#data = utilities.get_tmy_data(latitude=latitude, longitude=longitude)
#utilities.save_tmy_data(data, f"TMY_lat{latitude}_lon{longitude}")
df = utilities.read_tmy_data(filename=f"TMY_lat{latitude}_lon{longitude}")[['T2m','G(h)','Gb(n)','Gd(h)']]
print(df.head())

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
    # Sum all transparent heatflows and save to main df
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
    # Sum all transmission heatflows through the windows and store in main df 
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
# %% SOLAR GAINS
df['Qdot_sol [W]'] = 0 # create empty column in main df for sum of solar gains

# create df for solargains and init with solarpositions 
times = df.index
df_sol = get_solarposition(df.index, latitude, longitude)

# calculate total (beam + diffuse_sky + diffuse_ground) irradiation on windows
for window, properties in windows.items():
    irradiation = get_total_irradiance(
        surface_tilt = properties['tilt'],
        surface_azimuth = properties['azimuth'],
        solar_zenith = df_sol['zenith'],
        solar_azimuth = df_sol['azimuth'],
        dni = df['Gb(n)'],
        ghi = df['G(h)'],
        dhi = df['Gd(h)']
    )
    df_sol['Qdot_sol_gain_' + window + ' [W]'] = heatflow_solar_gains(
        area = properties['area'],
        irradiation = irradiation['poa_global'],
        g_value = properties['g_value']
    )

    df['Qdot_sol [W]'] += df_sol['Qdot_sol_gain_' + window + ' [W]']

print(df_sol.head())
print(df.head())