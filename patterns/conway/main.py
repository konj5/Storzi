import math

from jelka import Jelka
from jelka.shapes import Sphere
from jelka.types import Color

import numpy as np


jelka = Jelka(60)


def conway(board):
    newboard = np.zeros_like(board)

    print("adada2")

    a, b = board.shape

    print("adada1")

    for i in range(a):
        for j in range(b):
            s = board[(i-1)%a,j] + board[(i+1)%a,j] + board[i,(j-1)%b] + board[i,(j+1)%b]


            if s < 2 or s > 3:
                newboard[i,j] = 0
            else:
                newboard[i,j] = 1

    return newboard


###############################################################################################
#      Moj standardni postopek prodobivanja roba jelke                                        #
###############################################################################################
s = 0
N = 0
zmin = 100
zmax = -100
for light, position in jelka.positions_normalized.items():
    if zmin > position[2]: zmin = position[2]
    if zmax < position[2]: zmax = position[2]

    s += np.array(position)
    N += 1

a = 0.35  # Manualno fitani parametri
h = 1.15
bottom = 0.36

center_of_mass = s / N
#r0 = np.copy(center_of_mass)

center_of_mass[2] = 0  # Hočemo središče samo na 2D ravnini, ne v višini
############################################################################################


n1 = 6
n2 = 6
tmax = 100
steps_per_second = 3

#grid = np.random.randint(0,2,(n1,n2, tmax))

grid = np.zeros((n1,n2, tmax))
grid[:,:,0] = np.random.randint(0,2,(n1,n2))



for i in range(tmax-1):
    grid[:,:,i+1] = conway(grid[:,:,i])


def callback(jelka: Jelka):


    for light, position in jelka.positions_normalized.items():

        t = int((steps_per_second * jelka.frame/60) % tmax)

        rel_position = np.array(position) - center_of_mass
        x, y, z = rel_position

        r = np.sqrt(x**2 + y**2)
        phi = math.atan2(y,x)+np.pi


        i = int(n1 * (z-zmin)/(zmax-zmin))
        j = int(n2 * phi/(2*np.pi))


        if (not 3*(x**2 + y**2) < (a * (z - h)) ** 2):

            if grid[i,j,t] == 1:
                jelka.set_light(light, Color(255 , 255 , 255))

            elif grid[i,j,t] == 0:
                jelka.set_light(light, Color(124 , 45 , 223))




def main():
    jelka.run(callback)


main()
