import math

from jelka import Jelka
from jelka.shapes import Sphere
from jelka.types import Color
import numpy as np
from scipy.interpolate import CubicSpline



data = np.load("patterns\\bouncing-balls\\data.npy", allow_pickle=True)
v0, std_v, radius0, std_rad, N, decay_rate, tmax, dt, RGB = data[0]
lights_func = data[1]

def callback(jelka: Jelka):
    t = (jelka.frame / 60) % tmax
    lights = lights_func(t)



jelka.run(callback)


#jelka.set_light(light, cols[j])