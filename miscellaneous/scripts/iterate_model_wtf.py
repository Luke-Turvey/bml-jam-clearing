from bml_model import run_model, general_periodic
import numpy as np
import csv

if __name__ == "__main__":
    three_arr = np.array([[1,3,3],
                              [3,3,3],
                              [1,1,3]])
    
    print(general_periodic(three_arr, 99))
    filename = f"g_periodic_133333113"
    for n in range(1,1000):
        cars = general_periodic(three_arr, n)
        # print(n, cars)
        time = run_model(cars,n)
        print(n,time)

        with open(f'csv_files/{filename}.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([n,time])
    # print(general_periodic(three_arr, 1))
    # print(run_model(general_periodic(three_arr,1),1))