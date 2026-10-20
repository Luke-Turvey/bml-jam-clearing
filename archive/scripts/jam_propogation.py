from bml_model import move_north, move_east
import matplotlib.animation as animation
from matplotlib import colors
import matplotlib.pyplot as plt
import numpy as np

n=100

initial_grid = np.array([[1,1,3],
                         [1,3,3],
                         [3,1,3]])

total_grid = np.zeros((n,n))
total_grid[:len(initial_grid), -len(initial_grid):] = initial_grid

max_frame = int(1500)
frame_matrix = np.zeros((n,n,max_frame+1), dtype=int)
frame_matrix[:,:,0] = total_grid

t = 1
while (t < max_frame) and (total_grid != 0).any():

    active_grid_size = int(np.floor((t-1)/2)+3)
    active_grid = total_grid[:active_grid_size,-active_grid_size:]
    if active_grid_size < n-1:
        if t%2==1:
            total_grid[:active_grid_size,-active_grid_size:] = move_north(active_grid,active_grid_size)
            total_grid[active_grid_size,-active_grid_size:] = 3
        else:
            total_grid[:active_grid_size,-active_grid_size:] = move_east(active_grid,active_grid_size)
            total_grid[:active_grid_size+1,-active_grid_size-1] = 1
    else:
        if t%2==1:
            total_grid = move_north(total_grid,n)
        else:
            total_grid = move_east(total_grid,n)

    t+=1
    frame_matrix[:,:,t] = total_grid - (total_grid == 3)+1

max_frame = t

fig,ax = plt.subplots() 
cmap = colors.ListedColormap(['w','w','r','b'])
im = ax.imshow(frame_matrix[:,:,0],cmap=cmap)

def update(frame):
    print(frame)
    im.set_data(frame_matrix[:,:,frame])
    # print(frame_matrix[::-1])   
    im.set_cmap(cmap)
    return [im]

mat_anim = animation.FuncAnimation(fig, update, frames=max_frame, blit=True)

FFwriter = animation.FFMpegWriter(fps=20)
mat_anim.save(f'videos/jam_propogation_{n}.mp4', writer = FFwriter, dpi=600)