import math
import numpy as np

a = 5
b = 5
N_ts = 100

def conway(board):
    newboard = np.zeros_like(board)

    for i in range(a):
        for j in range(b):
            s = board[(i-1)%a,j] + board[(i+1)%a,j] + board[i,(j-1)%b] + board[i,(j+1)%b]


            if s < 2 or s > 3:
                newboard[i,j] = 0
            else:
                newboard[i,j] = 1

    return newboard

board = np.zeros((a,a, N_ts), dtype=np.byte)

board[:,:,0] = np.random.randint(0,2,(a,a))

for i in range(N_ts-1):
    board[:,:,i+1] = conway(board[:,:,i])



np.save("patterns\\conway\\game.npy", board)


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Create figure and axis
fig, ax = plt.subplots()

# Initial frame
im = ax.imshow(board[:, :, 0], cmap="viridis", vmin=0, vmax=1)
ax.set_title("t = 0")
plt.colorbar(im, ax=ax)

def update(t):
    """Update function for animation."""
    im.set_data(board[:, :, t])
    ax.set_title(f"t = {t}")
    return im,

# Create animation
ani = FuncAnimation(
    fig,
    update,
    frames=N_ts,
    interval=100,   # milliseconds between frames
    blit=True
)

plt.show()




