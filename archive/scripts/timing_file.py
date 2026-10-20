from bml_model import run_model, random, move_north, move_east
import timeit

if __name__ == "__main__":

    N=10000
    for n in range(1000,N, 1000):
        cars = random(N)
        starting_time = timeit.default_timer()

        new_cars = move_north(cars,N)
        print(n, timeit.default_timer()-starting_time)


