from iterate_periodic import generate_perm_arrays
from bml_model import run_model
import itertools
import numpy as np

def find_worst_3():
    three_arrs = generate_perm_arrays(3)
    return_arr = np.zeros((3,3))
    return_t = 0
    for arr in three_arrs:
        
        t = run_model(arr,3)
        print(arr,t)
        if t > return_t:
            return_arr = arr
            return_t = t
    
    # Returns 113113113, 17
    return return_arr, return_t

def find_worst_n(arr_n_minus_1,n):
    arr = np.zeros((n,n))
    arr[0:-1,1:] = arr_n_minus_1

    return_arr = np.zeros((n,n))
    return_t = 0

    for a in list(itertools.product([1,3],repeat=2*n-1))[10:-10]:
        b = list(a)
        arr[:,0] = b[:n]
        arr[-1,1:] = b[n:]
        
        t = run_model(arr,n)
        # print(arr,t)
        if t > return_t:
            return_arr = arr
            return_t = t
    return return_arr, return_t

# print(find_worst_3())

if __name__ == "__main__":

    print(find_worst_3())

    # x = np.array([[1,1,3],
    #             [1,1,3],
    #             [1,1,3]])

    # for n in range(4, 50):
    #     arr, t = find_worst_n(x,n)
    #     print(n,t,arr)
    #     x = arr
