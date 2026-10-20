import numpy as np
from bml_model import run_model, periodic
import itertools
import csv

def is_equiv(arr_1, arr_2):
    if (arr_1 == arr_2).all():
        return True
    if (arr_1+arr_2 == 4).all():
        return True
    
    # for i in range(len(arr_1)):
    #     arr_shift = np.vstack(((arr_1[i:,:]),arr_1[:i,:]))
    #     for j in range(len(arr_2)):
    #         if ((np.hstack(((arr_shift[:,j:]),arr_shift[:,:j]))) == arr_2).all():
    #             return True
    # return False

def generate_perm_arrays(k):
    arrs = []
    for a in itertools.product([1,3],repeat=k**2):
        candidate_arr = np.array(a).reshape(k,k)

        arrs.append(candidate_arr)
    
    return arrs


if __name__ == "__main__":
    print(2**9)
    # print(len(generate_perm_arrays(4)))

    k=3
    for arr in generate_perm_arrays(k)[377:]:
        print(f'{"".join(list(map(str,arr.flatten())))}')  
        
        checks = 100
        N = k*checks

        for n in range(k,N, k):
            cars = periodic(arr,n)
            time = run_model(cars, n)
            print(n,time)
            with open(f'csv_files/periodic_csv_full/{"".join(list(map(str,arr.flatten())))}.csv', 'a', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow([n,time])

