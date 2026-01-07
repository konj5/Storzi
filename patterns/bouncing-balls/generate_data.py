import math

from jelka import Jelka
from jelka.shapes import Sphere
from jelka.types import Color
import numpy as np
from scipy.interpolate import CubicSpline
from tqdm import trange

jelka = Jelka(60)

##### Predprocesiranje roba jelk
s = 0
N = 0
for light, position in jelka.positions_normalized.items():
    s += np.array(position)
    N += 1

a = 0.35  # Manualno fitani parametri
h = 1.15
bottom = 0.36

center_of_mass = s / N
r0 = np.copy(center_of_mass)

center_of_mass[2] = 0  # Hočemo središče samo na 2D ravnini, ne v višini


#######

####################################### TU SO NASTAVLJIVI PARAMETRI

v0 = 0.24  # Povprečna začetna hitrost kroglic
std_v = 0.05 # Standardna deviacija začetne hitrosti kroglic
radius0 = 0.1  # povprečni radij krogle
std_rad = 0.01 # Standardna deviacija radija kroglic
N = 2 # Število kroglic
decay_rate = 0.1 # faktor [0,inf], s katerim upada svetlost sledi : exp(- decay_rate * t)

tmax = 100  # Čas v sekundah preden se vzorec ponovi
dt = 0.001  # Časovni korak integracije (mora biti majhen, sicer krogla prebije steno)

RGB = [0,0,255] #Barva žogic

metadata = [v0, std_v, radius0, std_rad, N, decay_rate, tmax, dt, RGB]
#######################################

def get_random_inside():
    while(True):
        r = 2*(2*np.random.random(3)-1)
        x,y,z = r

        if (z < bottom) or (z > 0.9) or (x**2 + y**2 > (a * (z - h)) ** 2 and z < 500) or (x**2 + y**2 > (a * (z - h)) ** 2):
            return r
        
def get_random_velocity():
    direction =  np.random.normal(0, 1, 3)
    direction = direction / np.linalg.norm(direction)

    return (v0 + np.random.normal(0, std_v, 1)) * direction

def get_trajectory(dt, tmax):
    """generate = True
    try:
        data = np.load("patterns\\bouncing-balls\\data.npy", allow_pickle=True)
        generate = False
    except OSError:
        pass

    if generate == False:
        file_metadata = data[0]
        generate = file_metadata != metadata
    
    if generate == True:"""

    ts = np.arange(0, tmax, dt)
    rs = np.zeros((N, len(ts), 3))
    vs = np.zeros((N, len(ts), 3))
    radiuses = np.zeros(N)
    masses = np.zeros(N)

    for i in trange(0, N, desc="generating random parameters", leave = True):
        rs[i, 0, :] = get_random_inside()
        vs[i, 0, :] = get_random_velocity()
        radiuses[i] = np.abs(radius0 * np.random.normal(0, std_rad))
        masses[i] = 4*np.pi*radiuses[i]**3 / 3

    for i in trange(1, len(ts), desc="calculating trajectory", leave = True):
        for j in range(N):
            r = rs[j, i - 1, :] + dt * vs[j, i - 1, :]
            r, v = reflect_from_actual_cone(r, vs[j, i - 1, :], dt)
            rs[j, i, :] = r
            vs[j, i, :] = v

        rs[:,i-1,:], vs[:,i-1,:] = reflect_from_eachother(rs[:,i-1,:],vs[:,i-1,:], radiuses, masses)

    ##### Razredči ts, saj za risanje ne potrebujemo toliko točk kot smo za simulatijo

    step =  len(ts) //  (tmax*60)
    ts = ts[::step]
    rs = rs[:, ::step, :]


    ########### Zdaj imamo trajektorijo, pretvoriti moramo v funkcije svetlosti lučk

    lights = np.zeros((len(ts), len(jelka.lights), 3), dtype=float)

    for i in trange(0, len(ts), desc="transforming into lights format", leave = True):
        if i != 0:
            lights[i, :, :] = lights[i-1, :, :] * np.exp(-decay_rate * dt)


        j = -1
        for light, position in jelka.positions_normalized.items():
            j+=1
            
            for k in range(N):
                if is_in_ball(radiuses[k], position, rs[k,i,:]):
                    lights[i, j, :] = RGB
                    break


    

    data = np.array([metadata, CubicSpline(ts, lights, axis=0)], dtype=object)
    np.save("patterns\\bouncing-balls\\data.npy", data, allow_pickle=True)


    return data[1]


def is_in_ball(radij, pozicija, r):
    return radij**2 > (pozicija[0] - r[0]) ** 2 + (pozicija[2] - r[2]) ** 2 + (pozicija[1] - r[1]) ** 2


def reflect_from_actual_cone(r, v, timestep):
    rel_position = r - center_of_mass
    x, y, z = rel_position

    if z < bottom:
        # print("bottom")
        r = r - v * timestep
        v[2] = -v[2]

    elif z > 0.9:  # Da se ne zatakne na vrhu
        # print("vrh")
        r = r - v * timestep
        v[2] = -v[2]

    elif x**2 + y**2 > (a * (z - h)) ** 2 and z < 500:
        # Da se ne zatakne v kotu odbijemo od valja
        normal_vector = np.array([x / np.sqrt(x**2 + y**2), y / np.sqrt(x**2 + y**2), 0])

        # Standardna formula za zraljenje vzdolž vektorja
        v_mirrored = v - 2 * np.einsum("i,i,j->j", v, normal_vector, normal_vector)
        v = v_mirrored

    elif x**2 + y**2 > (a * (z - h)) ** 2:
        # print("side")
        r = r - v * timestep

        # Vektor pravokoten na stožec
        normal_vector = 1 / np.sqrt(1 + a**2) * np.array([x / np.sqrt(x**2 + y**2), y / np.sqrt(x**2 + y**2), -a])

        # Standardna formula za zrcaljenje vzdolž vektorja
        v_mirrored = v - 2 *  np.einsum("i,i,j->j", v, normal_vector, normal_vector)
        v = v_mirrored

    return r, v

def reflect_from_eachother(r,v, radiuses, masses):
    for i in range(N):
        for j in range(i+1, N):
            if np.linalg.norm(r[i,:]-r[j,:]) > radiuses[i]+radiuses[j]: continue
            
            #pravokotna hitrost
            normal = (r[j,:] - r[i,:]) / np.linalg.norm(r[j,:] - r[i,:])
            u1 = np.einsum("i,i->", normal, v[i,:])
            u2 = np.einsum("i,i->", normal, v[j,:])

            alpha = masses[j]/masses[i]
            a = alpha**2 + alpha
            b = -2*u2*alpha**2 + 2*alpha*u1
            c = -alpha*u2**2 + 2*alpha*u1*u2
            sols = np.roots([a,b,c])

            if sols[0]*u2 <= 0:
                new_u2 = sols[0]
                new_u1 = u1 + alpha * (u2-new_u2)
            else:
                new_u2 = sols[1]
                new_u1 = u1 + alpha * (u2-new_u2)

            v[i,:] = v[i,:] + normal * (new_u1-u1)
            v[j,:] = v[j,:] + normal * (new_u2-u2)

    return r, v


get_trajectory(dt, tmax)




#TO JE PREVELKO !!!!!!! (razredči v času po tem ko je trajektorija določena)
