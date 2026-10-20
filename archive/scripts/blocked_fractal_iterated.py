import numpy as np
import csv
from bml_model import run_model, blocked_fractal, fib_spiral_config

for k in range(10,15):
    n = 2**k
    print(n)
    cars = fib_spiral_config(n)
    time = run_model(cars,n)
    with open(f'csv_files/fib_spiral.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([n,time])