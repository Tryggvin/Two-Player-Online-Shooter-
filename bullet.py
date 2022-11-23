from Base3DObjects import Sphere
from math import *

class bullet():
    def __init__(self, x, y, z, angle):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.alive = True
        self.shape = Sphere()
    
    def update(self, delta_time):
        self.x += 12*cos(self.angle)*delta_time
        self.z += -12*sin(self.angle)*delta_time

    def set(self, x, y, z, angle):
        self.angle = angle
        self.x = 0.1*cos(angle)+x
        self.z = -0.1*sin(angle)+z
        self.y = y
    
    