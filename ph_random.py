import random
from shapely.geometry import Point
import math
import random

def generate_p1(poly,Xo,Yo):
    d1 = float(random.randrange(25, 50, 1)/10000)
    rad = 2*math.pi*random.uniform(0,1)
    if poly.contains(Point(Xo+d1*math.cos(rad),Yo+d1*math.sin(rad))):
        return Point(Xo+d1*math.cos(rad),Yo+d1*math.sin(rad)), rad
    else:
        generate_p1(poly,Xo,Yo)

def generate_p2(poly,Xo,Yo,rad):
    d2 = float(random.randrange(25, 50, 1)/10000)
    if poly.contains(Point(Xo-d2*math.cos(rad),Yo-d2*math.sin(rad))):
        return Point(Xo-d2*math.cos(rad),Yo-d2*math.sin(rad))
    else:
        generate_p2(poly,Xo,Yo,rad)

def random_waypoints(poly,Xo,Yo):
    while True:
        p1, rad = generate_p1(poly,Xo,Yo)
        p2 = generate_p2(poly,Xo,Yo,rad)
        if poly.contains(p1) and poly.contains(p2):
            return p1, p2
        else:
            random_waypoints(poly,Xo,Yo)