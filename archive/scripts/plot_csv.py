import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
import argparse

def data_func(a):
    if args.j == "log":
        return np.log2(a)
    else:
        return a
    
def linreg(X,Y):
    A = np.vstack([X, np.ones(len(X))]).T
    m, c = np.linalg.lstsq(A, Y, rcond=None)[0]


    return m, c

if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-f", "--file", help="csv file to run")
    argParser.add_argument("-j", "--j", help="function on the x and y coordinates")
    args = argParser.parse_args()

    df = pd.read_csv(f'csv_files/{args.file}.csv', header=None)

    
    x = np.array(data_func(df.iloc[3:,0]))
    y = np.array(data_func(df.iloc[3:,1]))
    
    b = 10  # base

    
    with plt.style.context("fast"):
        
        plt.rcParams["figure.figsize"] = [7.50, 5.00]
        plt.rcParams["figure.autolayout"] = True
        plt.grid(True)
        plt.loglog(x, y, '.',base=b)


        X,Y = np.log(x) / np.log(b) , np.log(y) / np.log(b)
        m,c = linreg(X,Y)
        print(m,c)
        plt.plot( 2**X, 2**(m*X+c), color = 'r', alpha = 0.2 )
        print(f"y={round(m,3)} x + {round(c, 2)}")


        # DOuble line code
        # slx = X[x % 3 == 2]
        # sly = Y[x % 3 == 2]
        # lx = X[x % 3 != 2]
        # ly = Y[x % 3 != 2]

        # slm, slc = linreg(slx, sly)
        # lm, lc = linreg(lx,ly)

        # print(f"y={round(slm,3)} x + {round(slc, 2)}")
        # print(f"y={round(lm,3)} x + {round(lc, 2)}")

        # plt.plot( 2**slx, 2**(slm*slx+slc), color = 'r', alpha = 0.2 )
        # plt.plot( 2**lx, 2**(lm*lx+lc), color = 'r', alpha = 0.2 )

        

        # place text (1,12) for periodic
        # place text ()
        plt.xlabel("$n$")
        plt.ylabel("$T(G_n,n)$")
        
    # plt.savefig(f'{args.file}_plot.png')


    # plt.show()
