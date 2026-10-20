import numpy as np
from bml_model import run_model, random,periodic,animate_model

def alterations(arr):
    altered_arrs = []
    for i in range(n):
        for j in range(n):
            altered_arr = np.zeros((n,n))+arr
            altered_arr[i,j] = (arr[i,j]+2) %4
            altered_arrs.append(altered_arr)

    return altered_arrs

def mcmc_iteration(arr):
    running_t = 0
    running_cars = np.zeros((n,n))
    for a in alterations(arr):
            t = run_model(a,n)
            # print(t,a)
            if t >= running_t:
                running_t = t
                running_cars = a

    return running_t, running_cars

def mcmc(cars,iterations=100):
    n=len(cars)
    mcmc_cars = cars
    old_t = 0
    for i in range(iterations):
        new_t, mcmc_cars = mcmc_iteration(mcmc_cars)
        if (old_t == new_t):
            break
        old_t=new_t
        print(new_t)

    return new_t,mcmc_cars

if __name__=="__main__":
    q = np.array([[1,1,3],
                  [1,3,3],
                  [3,1,3]])
    n=24
    cars = periodic(q,n)
    t,new_cars = mcmc(cars)
    animate_model(new_cars,n, "mcmc_find")