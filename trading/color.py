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
    if row['CE_volume'] == max_volume_CE and row['CE_volume'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['CE_volume'] == second_largest_volume_CE and row['CE_volume'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['strike'] < last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'


def PE_color_volume(row, max_volume_PE, second_largest_volume_PE,last_price):
    if row['PE_volume'] == max_volume_PE and row['PE_volume'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['PE_volume'] == second_largest_volume_PE and row['PE_volume'] > 0:  
        return 'background-color: #a5d6a7;'
    elif row['strike'] > last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'
    
# for change in oi
def CE_color_change_in_oi(row, max_coi_CE,second_largest_coi_CE, min_coi_CE,last_price):
    if row['CE_change_in_oi'] == max_coi_CE and row['CE_change_in_oi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['CE_change_in_oi'] == second_largest_coi_CE and row['CE_change_in_oi'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['CE_change_in_oi'] == min_coi_CE and row['CE_change_in_oi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] < last_price:
        return 'background-color: #f2eed9;'
    
    else:
            return 'background-color: #ffffff;'
        


def PE_color_change_in_oi(row, max_coi_PE, second_largest_coi_PE, min_coi_PE,last_price):
    if row['PE_change_in_oi'] == max_coi_PE and row['PE_change_in_oi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['PE_change_in_oi'] == second_largest_coi_PE and row['PE_change_in_oi'] > 0:  
        return 'background-color: #a5d6a7;'
    elif row['PE_change_in_oi'] == min_coi_PE and row['PE_change_in_oi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] > last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'
    


def CE_color_total_oi(row, max_CE_oi, second_largest_CE_oi, min_CE_oi, last_price):
    if row['CE_oi'] == max_CE_oi and row['CE_oi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['CE_oi'] == second_largest_CE_oi and row['CE_oi'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['CE_oi'] == min_CE_oi and row['CE_oi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] < last_price:
        return 'background-color: #f2eed9;'

    else:
        return 'background-color: #ffffff;'


def PE_color_total_oi(row, max_PE_oi, second_largest_PE_oi, min_PE_oi, last_price):
    if row['PE_oi'] == max_PE_oi and row['PE_oi'] > 0:
        return 'background-color: #ffeb3b;'
    elif row['PE_oi'] == second_largest_PE_oi and row['PE_oi'] > 0:
        return 'background-color: #a5d6a7;'
    elif row['PE_oi'] == min_PE_oi and row['PE_oi'] < 0:
        return 'background-color: #FFC0CB;'
    elif row['strike'] > last_price:
        return 'background-color: #f2eed9;'
    else:
        return 'background-color: #ffffff;'