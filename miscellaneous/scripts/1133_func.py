import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.animation as animation

def F_2(i,j,k,n):
    if i <= n- np.floor(((k-1)-4*n+5)/2):
        if (i >= ((k-1)+7)/4):
            if (n-j)%2==0:
                return 1
            else:
                return 3
            
        elif (i <= ((k-1)+7-1)/4):
            if (n-j)%2==1:
                if ((i+np.floor((k-1)/2))%3 == 0) :
                    return 3
                if ((i+np.ceil((k-1)/2))%3 == 2) and (i+(3/4*((n-j+1)-2)) >= (k-1)/4):
                    return 1
            elif (n-j)%2 == 0:
                if ((i+np.ceil((k-1)/2))%3 != 2) and (i+(3/4*((n-j+1)-2)) >= (k-1)/4):
                    return 1
                
    elif i > n- np.floor(((k-1)-4*n+5)/2):
        if (i+(n-j+1) > n+np.floor(((k-1)-4*n+5)/2)):
            if (i+(n-j) - np.ceil((k-1)/2))%2 == 0:
                return 1
            

    return 0
    



def cars_func(k):
    cars = np.zeros((n,n))
    for i in range(len(cars)):
        for j in range(len(cars)):
            cars[i,n-j-1] = F_2(i+1,j+1,k,n)
    return cars

n=50
k=10
print(cars_func(6*n-5))
print((cars_func(6*n-6) == 0).all())

cmap = colors.ListedColormap(['k','r','b'])
fig, ax = plt.subplots()
plt.imshow(cars_func(150), cmap=cmap)
plt.axis('off')
plt.savefig('1133_regions_150_b.png',bbox_inches='tight',pad_inches=0, format='png', dpi=1200)
# plt.show()

# max_frame = 6*n-4+1

# frame_matrix = np.zeros((n,n,max_frame), dtype=int)
# for k in range(1,max_frame):
#     print(k)
#     # print(cars_func(k))
#     frame_matrix[:,:,int(k)-1] = cars_func(k).astype(int)
# fig,ax = plt.subplots() 
# cmap = colors.ListedColormap(['w','r','b'])
# print(frame_matrix[:,:,0])
# im = ax.imshow(frame_matrix[:,:,0].astype(int),cmap=cmap)

# plt.show()

# def update(frame):
#     # print(frame)
#     # print(frame_matrix[:,:,frame])
#     im.set_array(frame_matrix[:,:,frame].astype(int))
#     return [im]

# mat_anim = animation.FuncAnimation(fig, update, frames=max_frame-2, blit=True)

# FFwriter = animation.FFMpegWriter(fps=2)
# mat_anim.save(f'videos/wedge_func.mp4', writer = FFwriter, dpi=600)

