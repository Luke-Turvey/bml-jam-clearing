import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

if __name__ == "__main__":


    df = pd.read_csv(f'csv_files/g_periodic_133333113.csv', header=None, names = ["n", "t"])
    sns.scatterplot(data=df, x="n", y="t",size=1)

    plt.xlabel("$n$")
    plt.ylabel("$t$")

    plt.show()