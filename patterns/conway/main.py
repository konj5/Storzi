import math

from jelka import Jelka
from jelka.shapes import Sphere
from jelka.types import Color

import numpy as np


jelka = Jelka(60)


#board = np.load("patterns\\conway\\game.npy")

######################################################################
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
##############################################################

a,b,_ = board.shape

def getConwayFunction(tmax):
    def ConwayFunc(t):
        n = int(t/tmax)
        return board[:,:,n]
    
    return ConwayFunc

#######################################
tmax = 100
#######################################


###############################################################################################
#      Moj standardni postopek prodobivanja roba jelke                                        #
###############################################################################################
s = 0
N = 0
for light, position in jelka.positions_normalized.items():
    s += np.array(position)
    N += 1

#a = 0.35  # Manualno fitani parametri
h = 1.15
bottom = 0.36

center_of_mass = s / N
#r0 = np.copy(center_of_mass)

center_of_mass[2] = 0  # Hočemo središče samo na 2D ravnini, ne v višini

"""
rel_position = r - center_of_mass
x, y, z = rel_position
x**2 + y**2 = (a * (z - h)) ** 2  To je rob jelke
"""
############################################################################################


ConwayFunc = getConwayFunction(tmax)

def callback(jelka: Jelka):



    #Reset za vse luči
    for light, position in jelka.positions_normalized.items():
        jelka.set_light(light, Color(0, 0, 0))

    #Postavimo na prave vrednosti

    grid = ConwayFunc(t = (jelka.frame / 60) % tmax)

    for light, position in jelka.positions_normalized.items():
        rel_position = np.array(position) - center_of_mass
        x, y, z = rel_position

        r = np.sqrt(x**2 + y**2)
        phi = math.atan2(y,x)


        i = int((z-h)/(1-h))
        j = int(phi/(2*np.pi))

        if grid[i,j] == 1 and r > 0.3:
            jelka.set_light(light, Color(255, 255, 255))




def main():
    jelka.run(callback)


main()
