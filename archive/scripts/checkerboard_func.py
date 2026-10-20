import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.animation as animation

def F_2(i,j,k,n):
    if (i >= np.floor(k/2)+1) and (j <= n-np.floor(k/2)) and (i+j > n+1):
        return 3
    elif (i >= np.floor(k/2)+1) and (j <= n-np.floor(k/2)) and (i+j <= n+1):
        return 1
    
    if (i >= np.floor((n-j+np.floor((k+5)/2))/2)+1) and (j > n-np.floor(k/2)):
        return 3

    if (j <=n- np.ceil((i+np.floor((k-2)/2))/2)) and (i < np.floor(k/2)+1):
        return 1
    
    else:
        if ((i-j+np.ceil(k/2)+n)%3 == 0) and (j >= i + np.ceil((k-4*n)/2)+1):
            return 3
        if ((i -j+np.floor(k/2)+n-1)%3 == 0) and (j >= i + np.floor((k-4*n)/2)):
            return 1
        else:
            return 0

n=100

def cars_func(k):
    cars = np.zeros((n,n))
    for i in range(len(cars)):
        for j in range(len(cars)):
            cars[i,j] = F_2(i+1,j+1,k,n)
    return cars

# print(cars_func(13))

# cmap = colors.ListedColormap(['w','r','b'])
# fig, ax = plt.subplots()
# plt.imshow(cars, cmap=cmap)
# plt.axis('off')
# plt.show()

max_frame = 6*n-4 +1

frame_matrix = np.zeros((n,n,max_frame), dtype=int)
for k in range(0,max_frame):
    print(k)
    # print(cars_func(k))
    frame_matrix[:,:,int(k)] = cars_func(k).astype(int)

frame_matrix = frame_matrix[:,:,2:]
fig,ax = plt.subplots() 
cmap = colors.ListedColormap(['w','r','b'])
print(frame_matrix[:,:,0])
im = ax.imshow(frame_matrix[:,:,0].astype(int),cmap=cmap)

# plt.show()

def update(frame):
    # print(frame)
    # print(frame_matrix[:,:,frame])
    im.set_array(frame_matrix[:,:,frame].astype(int))
    return [im]

mat_anim = animation.FuncAnimation(fig, update, frames=max_frame-2, blit=True)

FFwriter = animation.FFMpegWriter(fps=20)
mat_anim.save(f'videos/wedge_func.mp4', writer = FFwriter, dpi=600)

