import math
import numpy as np

a = 10
b = 10
N_ts = 10

def conway(board):
    newboard = np.zeros_like(board)

    for i in range(a):
        for j in range(b):
            s = np.sum(board[(i-1)%a:(i+1)%a, (j-1)%b:(j+1)%b])-board[i,j]

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




