import pandas as pd
import numpy as np
from os import listdir
from scipy.stats import linregress

from iterate_periodic import is_equiv, generate_perm_arrays

def gen_list_of_difs(df):
    n = len(df)
    lst = [df.iloc[j,1]-df.iloc[j-1,1] for j in range(1,n)]
    # print(df,lst)

    return lst

def is_periodic(lst):
    n = len(lst)
    rep_list = []
    for period in range(1,n//2):
        k= n//period
        cut_list = lst[:period*k][::-1]
        cut_arr = np.array(cut_list).reshape(k,period)   
        num_of_reps = 0
        repeating = True
        
        while repeating:
            if num_of_reps > len(cut_arr[:,0])-2:
                repeating=False
            elif (cut_arr[num_of_reps,:] == cut_arr[num_of_reps+1,:]).all():
                num_of_reps+=1
            else:
                repeating=False
        rep_list.append(num_of_reps)
    
    return np.argmax(rep_list)+1, np.max(rep_list)

def calculate_power(df):
    a = linregress(np.log(list(df.iloc[:,0])), np.log(list(df.iloc[:,1])))
    return float(a.slope)

for file in listdir("csv_files/periodic_csv_full/"):
    df = pd.read_csv(f"csv_files/periodic_csv_full/{file}", header=None)
    lst_of_difs = gen_list_of_difs(df)
    # print(file, lst_of_difs)

    lud = {"1": "\\trc", "3":"\\tuc"}

    period, num_of_periods = is_periodic(lst_of_difs)
    if not ( (period == 1) and (num_of_periods == 0)):
        config = f"{file[:-4]}" # & NOT LINEAR 
        slope = np.average(lst_of_difs[::-1][:period])
        power = calculate_power(df)
        power_string = "{:.3f}".format(power)
        slope_string = f"{round(slope//3)}"

        # === POWER STRING === 
        # print(f"\\begin{{tikzpicture}}[scale=1.1] \n {lud[config[0]]}{{0}}{{0}} {lud[config[1]]}{{0.6}}{{0}} {lud[config[2]]}{{1.2}}{{0}} \n {lud[config[3]]}{{0}}{{-0.6}} {lud[config[4]]}{{0.6}}{{-0.6}} {lud[config[5]]}{{1.2}}{{-0.6}} \n {lud[config[6]]}{{0}}{{-1.2}} {lud[config[7]]}{{0.6}}{{-1.2}} {lud[config[8]]}{{1.2}}{{-1.2}} \n \\node at (0.9,-1.5) {{{power_string}}}; \\end{{tikzpicture}} \\hspace{{0.2cm}}")
        
        # === LINEAR STRING ===
        print(f"\\begin{{tikzpicture}}[scale=1.1] \n {lud[config[0]]}{{0}}{{0}} {lud[config[1]]}{{0.6}}{{0}} {lud[config[2]]}{{1.2}}{{0}} \n {lud[config[3]]}{{0}}{{-0.6}} {lud[config[4]]}{{0.6}}{{-0.6}} {lud[config[5]]}{{1.2}}{{-0.6}} \n {lud[config[6]]}{{0}}{{-1.2}} {lud[config[7]]}{{0.6}}{{-1.2}} {lud[config[8]]}{{1.2}}{{-1.2}} \n \\node at (0.9,-1.5) {{{slope_string}}}; \\end{{tikzpicture}} \\hspace{{0.2cm}}")

        print("%")
    # else:
    #     slope = np.average(lst_of_difs[::-1][:period])
    #     print(f"{file[:-4]} &  LINEAR \\\\") #, SLOPE: {slope/3}")


a = np.array([[1,1,3],
              [1,3,3],
              [3,3,3]])

# for file in listdir("csv_files/periodic_csv_full/"):
#     b = np.array(list(file[:-4])).astype(int).reshape(3,3)

#     if is_equiv(a,b):
#         df = pd.read_csv(f"csv_files/periodic_csv_full/{file}", header=None)
#         lst_of_difs = gen_list_of_difs(df)
#         period, num_of_periods = is_periodic(lst_of_difs)
#         if (period == 1) and (num_of_periods == 0):
#             print(f"{b} & NOT LINEAR \\\\")
#         else:
#             slope = np.average(lst_of_difs[::-1][:period])
#             print(f"{b} &  LINEAR \\\\, SLOPE: {slope/3}")
