import numpy as np
import argparse
import csv
from bml_model import run_model, random, blocked, checkerboard, periodic,blocked_diagonal, general_periodic



def iterated_model(l,u,s,init):
    for n in range(l,u,s):
        
        if args.init == "checkerboard":
            cars = checkerboard(n)
        elif args.init == "random":
            cars = random(n)
        elif args.init == "blocked":
            cars = blocked(n)

        elif args.init == "periodic":
            
            three_arr = np.array([[3,3,1],
                                  [3,1,1],
                                  [1,3,1]])
            cars = periodic(three_arr, n)
            init = f"{args.init}_{''.join(list(map(str,three_arr.flatten())))}"

        elif args.init == "g_periodic":
            print(n)
            three_arr = np.array([[1,3,3],
                                [3,3,3],
                                [1,1,3]])
            cars = general_periodic(three_arr, n)
            print(np.shape(cars))
            args.init = f"g_periodic_{args.init}_{n}_{''.join(list(map(str,three_arr.flatten())))}"

        elif args.init == "blocked_diagonal":
            cars=blocked_diagonal(n,int(args.step))

        time = run_model(cars,n)

        with open(f'csv_files/{init}.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([n,time])


argParser = argparse.ArgumentParser()
argParser.add_argument("-l", "--lower", help="smallest grid size run")
argParser.add_argument("-u", "--upper", help="largest grid size run")
argParser.add_argument("-s", "--step", help = "step between grid sizes")
argParser.add_argument("-i", "--init", help="checkerboard, random, blocked, g_periodic")

args = argParser.parse_args()
iterated_model(int(args.lower), int(args.upper), int(args.step), args.init)

    

