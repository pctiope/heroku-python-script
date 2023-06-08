import random
from shapely.geometry import Point
import math
import random

def generate_p1(poly,Xo,Yo,mode):
    if mode == 'bicycle':
        d1 = float(random.randrange(250, 300, 10)/10000)
    else:
        d1 = float(random.randrange(40, 80, 10)/10000)
    rad = 2*math.pi*random.uniform(0,1)
    if poly.contains(Point(Xo+d1*math.cos(rad),Yo+d1*math.sin(rad))):
        point1, radians1 = Point(Xo+d1*math.cos(rad),Yo+d1*math.sin(rad)), rad
        print(point1, radians1)
        return point1, radians1
    else:
        generate_p1(poly,Xo,Yo)

def generate_p2(poly,Xo,Yo,rad,mode):
    if mode == 'bicycle':
        d2 = float(random.randrange(250, 300, 10)/10000)
    else:
        d2 = float(random.randrange(40, 80, 10)/10000)
    if poly.contains(Point(Xo-d2*math.cos(rad),Yo-d2*math.sin(rad))):
        point2 = Point(Xo-d2*math.cos(rad),Yo-d2*math.sin(rad))
        print(point2)
        return point2
    else:
        generate_p2(poly,Xo,Yo,rad)

def random_waypoints(poly,Xo,Yo,mode):
    while True:
        p1, rad = generate_p1(poly,Xo,Yo,mode)
        p2 = generate_p2(poly,Xo,Yo,rad,mode)
        if poly.contains(p1) and poly.contains(p2):
            return p1, p2
        else:
            random_waypoints(poly,Xo,Yo)