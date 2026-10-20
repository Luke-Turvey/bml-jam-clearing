import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

matrix = np.random.rand(10, 10,100)

fig, ax = plt.subplots()
im = ax.imshow(matrix[:,:,0])

def update(frame):
    
    im.set_array(matrix[:,:,frame])
    return [im]

mat_anim = animation.FuncAnimation(fig, update, frames=100, blit=True)

FFwriter = animation.FFMpegWriter(fps=10)
mat_anim.save('animation.mp4', writer = FFwriter)


