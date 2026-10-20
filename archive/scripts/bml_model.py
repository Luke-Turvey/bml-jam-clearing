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
 
def run_model(cars,n):
    t = 0
    while (cars != 0).any():
        t+=1
        if t%2==1:
            cars = move_north(cars,n)
        else:
            cars = move_east(cars,n)
        
        if t%1000 == 0:
            print(t)
        # if t==5*n:
        #     cmap = colors.ListedColormap(['w','r','b'])
        #     fig, ax = plt.subplots()
        #     plt.imshow(cars, cmap=cmap)
        #     plt.axis('off')
        #     fig.savefig(f'gperiodic_133333113_{n}.png',bbox_inches='tight',pad_inches=0, format='png', dpi=1200)
    
            
    return t

def run_model_with_tracking(cars,n):
    tracking_mat = np.zeros(np.shape(cars))
    t=0
    while (cars != 0).any():
        if t%2==0:
            cars = move_north(cars,n)
        else:
            cars = move_east(cars,n)
        t+=1
        for i,row in enumerate(cars):
            # print(row)
            zero_length = np.argmax((row == 1))
            if tracking_mat[i, zero_length-1] == 0:
                tracking_mat[i, zero_length-1] = t
        
        if t%1000 == 0:
            print(t)
    tracking_mat[:,-1] = tracking_mat[:,-2]+2
    print(tracking_mat)

    fig, ax = plt.subplots()
    plt.imshow(tracking_mat, cmap='rainbow')
    for (j,i),label in np.ndenumerate(tracking_mat):
        ax.text(i,j,str(int(label)),ha="center",va="center",color="w",size=1)
    plt.axis('off')
    fig.savefig(f'images/{args.init}_{n}_trackingmat.svg',bbox_inches='tight',pad_inches=0, format='svg', dpi=1200)
    

def animate_model(cars,n,init):
    
    max_frame = int(1500)
    frame_matrix = np.zeros((n,n,max_frame+1), dtype=int)
    frame_matrix[:,:,0] = cars

    t = 0
    while (t < max_frame) and (cars != 0).any():
        if t%2==0:
            cars = move_north(cars,n)
        else:
            cars = move_east(cars,n)
         
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

    FFwriter = animation.FFMpegWriter(fps=2)
    mat_anim.save(f'videos/{init}_{n}.mp4', writer = FFwriter, dpi=600)

def checkerboard(n):
    arr = np.zeros((n,n))
    for i in range(0,n):
        for j in range(0,n):
            if (i +j) % 2 == 0:
                arr[i,j] = 3
            else:
                arr[i,j] = 1
    return arr.astype(int)

def random(n):
    return ((np.random.rand(n,n) > 0.5)*2+1).astype(int)

def blocked(n):
    arr = np.flipud(np.tri(n,n,-1).T) * 2 +1
    return arr

def factorial_config(k):
    n = np.math.factorial(k)
    arr = np.zeros((n,n))
    for i in range(k+1,0,-1):
        arr[:,(n//i)-1] = 3
        arr[n-(n//i),:] = 1
    return arr

def fib_spiral_config(n):
    k = int(np.log2(n))
    if np.log2(n) %1 != 0:
        n = 2**(k)
    
    arr = np.ones((n,n),dtype=np.uint8)
    for j in range(0,k):
        # print(n-(2**j),n-(2**(j+1)))
        # print(arr[n-(2**(j+1))+1:, 2**j-1:2**(j+1)-1].shape)
        arr[n-(2**(j+1))+1:, 2**j-1:2**(j+1)-1] = 3

    return arr

def blocked_rcotr(n):
    arr = np.flipud(np.tri(n,n,0).T) * 2 +1
    return arr

def blocked_back(n):
    arr = np.tri(n,n,-1)*2+1
    return arr

def blocked_fractal(n):
    if np.log2(n) %1 != 0:
        n = 2**(int(np.log2(n)))
    
    if n != 4:
        a = np.hstack((blocked(n//2), blocked_fractal(n//2)))
        b = np.hstack((blocked(n//2), blocked_rcotr(n//2)))
        return np.vstack((a,b))
    else:
        return blocked_2_2(4)
    

def blocked_2_2(n):
    a = np.hstack((blocked(n//2), blocked(n//2)))
    return np.vstack((a,a))

def blocked_diagonal(n,k):
    freq = n // k
    b = blocked(k)
    new_n = k*freq
    arr = np.zerobinwidths((new_n, new_n))
    for i in range(0,new_n, k):
        for j in range(0,new_n, k):
            if (i+j - (new_n-k))%(2*k) == 0:
                arr[i:i+k, j:j+k] = b

    return arr.astype(np.uint8)

def periodic(per, n):
    period = len(per)
    freq = n // period
    new_n = period*freq
    arr = np.zeros((new_n, new_n))
    
    for i in range(0,new_n, period):
        for j in range(0,new_n, period):
            arr[i:i+period, j:j+period] = per

    return arr

def general_periodic(per, n):
    period = len(per)
    freq = n // period
    new_n = period*freq + period

    temp_arr = periodic(per, new_n)

    return temp_arr[-n:, 0:n]
    

def array_load(file):
    return np.load(file)

def delete(cars, top, bottom, left, right):
    c = cars[top:-bottom, left:-right]
    return c

if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-n", "--n", help="grid size")
    argParser.add_argument("-i", "--init", help="checkerboard, random, blocked, periodic, 22blocked, blocked_fractal,blocked_diagonal, test_init")

    args = argParser.parse_args()
    print("args.n=%s" % args.n)
    print("args.n=%s" % args.init)

    n = int(args.n)
    if args.init == "checkerboard":
        cars = checkerboard(n)
    elif args.init == "random":
        cars = random(n)
    elif args.init == "blocked":
        cars = blocked(n)
    elif args.init == "periodic":
        # three_arr = np.array([[1,3],
        #                      [1,3]])
        three_arr = np.array([[1,3,3],
                              [1,3,1],
                              [3,1,3]])
        # three_arr = np.array([[1,1,1,1],
        #                      [1,1,1,3],
        #                      [1,1,3,3],
        #                      [1,3,3,3]])
        # three_arr = np.array([[3,1,1,1,1,1],
        #                       [1,1,1,1,1,3],
        #                       [1,1,1,1,3,3],
        #                       [1,1,1,3,3,3],
        #                       [1,1,3,3,3,3],
        #                       [1,3,3,3,3,3]])
    
        cars = periodic(three_arr, n)
        n = len(cars)
        args.init = f"{args.init}_{n}_{''.join(list(map(str,three_arr.flatten())))}"
    elif args.init == "g_periodic":
        # three_arr = np.array([[3,3],
        #                      [1,1]])
        three_arr = np.array([[1,3,3],
                              [3,3,3],
                              [1,1,3]])
        cars = general_periodic(three_arr, n)
        args.init = f"{args.init}_{n}_{''.join(list(map(str,three_arr.flatten())))}"
    elif args.init == "22blocked":
        cars=blocked_2_2(n)
    elif args.init == "blocked_fractal":
        cars=blocked_fractal(n)
    elif args.init == "blocked_diagonal":
        cars=blocked_diagonal(n,10)
    elif args.init=="blocked_back":
        cars=blocked_back(n)
    elif args.init=="fib_spiral":
        cars=fib_spiral_config(n)
    elif args.init=="fac":
        cars=factorial_config(n)
    else :
        cars = array_load(f"{args.init}.npy")
    
    # cars = delete(cars, 2,3,3,3)
    # cars[:,-1] = 0
    # cars[:,-2] = 0
    # cars[0,:] = 0
    # cars[1,:] = 0

    print(cars)
    print(np.sum(np.sum(cars==1)))
    print(np.sum(np.sum(cars==3)))

    n,m = np.shape(cars)
    print(n,m)
    # animate_model(cars,n,args.init)
    print(run_model(cars,n))
    # run_model_with_tracking(cars,n)

