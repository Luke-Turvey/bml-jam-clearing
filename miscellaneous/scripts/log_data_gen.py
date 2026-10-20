

import numpy as np
import argparse
import csv
from bml_model import run_model, general_periodic



def iterated_model(l,u,b):
    last_num = np.emath.logn(b, u)
    first_num = np.emath.logn(b, l)
    for t in np.arange(first_num,last_num,0.1):
        grid_size = int(b**t)
        
        three_arr = np.array([[1,3,3],
                            [3,3,3],
                            [1,1,3]])
        cars = general_periodic(three_arr, grid_size)
        name = f"log_g_periodic_base_{b}_{''.join(list(map(str,three_arr.flatten())))}"


        time = run_model(cars,grid_size)
        print(grid_size, time)



        with open(f'csv_files/{name}.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([grid_size,time])

        cars = general_periodic(three_arr, grid_size+1)
        time = run_model(cars,grid_size+1)
        with open(f'csv_files/{name}.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([grid_size+1,time])

        cars = general_periodic(three_arr, grid_size+2)
        time = run_model(cars,grid_size+2)
        with open(f'csv_files/{name}.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([grid_size+2,time])


argParser = argparse.ArgumentParser()

argParser.add_argument("-l", "--lower", help="smallest grid size run")
argParser.add_argument("-u", "--upper", help="largest grid size run")
argParser.add_argument("-b", "--base", help = "logarithm base to iterate over")


args = argParser.parse_args()
iterated_model(int(args.lower), int(args.upper), int(args.base))

    
