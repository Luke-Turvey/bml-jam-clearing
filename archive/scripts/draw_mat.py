import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

file = "113133313_1500/mat_9500"
cars = np.load(f"{file}.npy")

print(cars)

cmap = colors.ListedColormap(['w','r','b'])
fig, ax = plt.subplots()
plt.imshow(cars, cmap=cmap)
plt.axis('off')
fig.savefig(f'{file}_w.png',bbox_inches='tight',pad_inches=0, format='png', dpi=2000)
    