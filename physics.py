

def heatflow_transmission(u_value = 1, area = 0, temp_in = 22, temp_out = 0):
    Qdot_trans = u_value * area * (temp_in - temp_out)
    return Qdot_trans