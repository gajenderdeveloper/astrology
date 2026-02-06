def CE_color(row,last_price):
    if row['strike'] < last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'

def PE_color(row,last_price):
    if row['strike'] > last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'

def CE_color_volume(row, max_volume_CE, second_largest_volume_CE,last_price):
    if row['call_volume'] == max_volume_CE and row['call_volume'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['call_volume'] == second_largest_volume_CE and row['call_volume'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['strike'] < last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'


def PE_color_volume(row, max_volume_PE, second_largest_volume_PE,last_price):
    if row['put_volume'] == max_volume_PE and row['put_volume'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['put_volume'] == second_largest_volume_PE and row['put_volume'] > 0:  
        return 'background-color: #a5d6a7;'
    elif row['strike'] > last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'
    
# for change in oi
def CE_color_change_in_oi(row, max_coi_CE,second_largest_coi_CE, min_coi_CE,last_price):
    if row['call_coi'] == max_coi_CE and row['call_coi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['call_coi'] == second_largest_coi_CE and row['call_coi'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['call_coi'] == min_coi_CE and row['call_coi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] < last_price:
        return 'background-color: #f2eed9;'
    
    else:
            return 'background-color: #ffffff;'
        


def PE_color_change_in_oi(row, max_coi_PE, second_largest_coi_PE, min_coi_PE,last_price):
    if row['put_coi'] == max_coi_PE and row['put_coi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['put_coi'] == second_largest_coi_PE and row['put_coi'] > 0:  
        return 'background-color: #a5d6a7;'
    elif row['put_coi'] == min_coi_PE and row['put_coi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] > last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'
    


def CE_color_total_oi(row, max_CE_oi, second_largest_CE_oi, min_CE_oi, last_price):
    if row['call_oi'] == max_CE_oi and row['call_oi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['call_oi'] == second_largest_CE_oi and row['call_oi'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['call_oi'] == min_CE_oi and row['call_oi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] < last_price:
        return 'background-color: #f2eed9;'

    else:
        return 'background-color: #ffffff;'


def PE_color_total_oi(row, max_PE_oi, second_largest_PE_oi, min_PE_oi, last_price):
    if row['put_oi'] == max_PE_oi and row['put_oi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['put_oi'] == second_largest_PE_oi and row['put_oi'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['put_oi'] == min_PE_oi and row['put_oi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] > last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'