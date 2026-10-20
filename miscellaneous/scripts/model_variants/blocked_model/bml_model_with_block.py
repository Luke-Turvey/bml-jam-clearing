import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colors
import argparse

from PIL import Image


def move_north(G,n):
    # S = np.vstack((np.zeros((1,n)),G[:-1,:]))
    # I = G - S
    B = (G-np.vstack((np.zeros((1,n)),G[:-1,:])) == 3)*3
    A = np.vstack((B[1:,:], np.zeros((1,n))))
    N = G+A+B

    return (N-(N==6)*6).astype(int)

def move_east(G,n):
    # S = np.hstack((G[:, 1:], np.zeros((n,1))))
    # I = G-S
    B = ((G-np.hstack((G[:, 1:], np.zeros((n,1)))))==1)
    A = np.hstack((np.zeros((n,1)), B[:,:-1]))
    N = G+A+B
    
    return (N-(N==2)*2).astype(int)
 
def run_model(cars,n,p):
    t = 0
    while t< 10000:
        if t%2==1:
            cars = move_north(cars,n)
            bottom_row = ((np.random.rand(n) < p/2)*2+1).astype(int)
            cars[-1,:] = bottom_row
        else:
            cars = move_east(cars,n)    
            left_col = ((np.random.rand(n) < p/2)).astype(int)
            cars[:,0] = left_col
        
        cars[0,-1] = 1

        t+=1
        if t%500 == 0:
            print(t)
        # if t==12000:
        #     cmap = colors.ListedColormap(['k','r','b'])
        #     fig, ax = plt.subplots()
        #     plt.imshow(cars, cmap=cmap)
        #     plt.axis('off')
        #     fig.savefig(f'{t}_{n}_{p}.png',bbox_inches='tight',pad_inches=0, format='png', dpi=1200)
    
    print(cars)
    with open(f"{t}_{n}_{p}.npy", "wb") as f:
        np.save(f, cars)  
       
    return t

def animate_model(cars,n,p):
    
    max_frame = int(20)
    frame_matrix = np.zeros((n,n,max_frame+1), dtype=int)
    frame_matrix[:,:,0] = cars

    t = 0
    while (t < max_frame):
        if t%2==1:
            cars = move_north(cars,n)
            bottom_row = ((np.random.rand(n) < p/2)*2+1).astype(int)
            cars[-1,:] = bottom_row
        else:
            cars = move_east(cars,n)    
            left_col = ((np.random.rand(n) < p/2)).astype(int)
            cars[:,0] = left_col

        cars[0,-1] = 1

        t+=1
        frame_matrix[:,:,t] = cars - (cars == 3)+1

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

    FFwriter = animation.FFMpegWriter(fps=1)
    mat_anim.save(f'videos/{p}_{n}.mp4', writer = FFwriter, dpi=600)


if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-n", "--n", help="grid size")
    argParser.add_argument("-p", "--p", help="prob")

    args = argParser.parse_args()
    print("args.n=%s" % args.n)

    n = int(args.n)
    p = float(args.p)

    cars = np.zeros((n,n)).astype(int)
    cars[0,-1]=1
    cars[0,-2]=3

    n = len(cars)
    # animate_model(cars,n,p)
    print(run_model(cars,n,p))
    # run_model_with_tracking(cars,n)

