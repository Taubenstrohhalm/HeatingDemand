

def heatflow_transmission(u_value, area, temp_in, temp_out):
    Qdot_trans = u_value * area * (temp_in - temp_out)
    return Qdot_trans

def heatflow_ventilation_infiltration(volume, n_vent, temp_in, temp_out, n_inf = 0):
    HEATCAPAIR = 1100 # [J/kg] heat capacity of air
    DENSITYAIR = 1.25 # [kg/m^3] density of air
    Qdot_vent = HEATCAPAIR * DENSITYAIR * volume * (n_inf + n_vent) * (temp_in - temp_out)
    return Qdot_vent

def heatflow_solar_gains(area, irradiation, g_value):
    Qdot_sol = area * irradiation * g_value
    return Qdot_sol