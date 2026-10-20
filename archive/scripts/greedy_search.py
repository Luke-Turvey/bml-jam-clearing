import argparse
import numpy as np
from bml_model import random, run_model, animate_model
import matplotlib.pyplot as plt

if __name__=="__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-n", "--n", help="grid size")
    argParser.add_argument("-iters", "--iterations", help="")

    args = argParser.parse_args()

    init = "random_greedy"

    iters = args.iterations
    n = int(args.n)

    running_t = 0
    running_cars=np.zeros((n,n))
    t_arr = []

    for i in range(int(iters)):
        cars = random(n)
        t = run_model(cars,n)
        t_arr.append(t)
        if t >= running_t:
            running_cars = cars
            running_t = t
        print(i,t,running_t)

    animate_model(running_cars,n,init)

    plt.hist(t_arr,bins=range(min(t_arr), max(t_arr) + 2, 2))

    plt.show()
