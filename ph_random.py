import random
from shapely.geometry import Point
import math
import random

def random_waypoints(poly,Xo,Yo):
    while True:
        d = float(random.randrange(5, 100, 5)/10000)
        rad = 2*math.pi*random.uniform(0,1)
        p1 = Point(Xo+d*math.cos(rad),Yo+d*math.sin(rad))
        p2 = Point(Xo-d*math.cos(rad),Yo-d*math.sin(rad))
        print(d, 'distance', rad, 'radian, ', p1, 'p1, ', p2, 'p2')
        if poly.contains(p1) and poly.contains(p2):
            return p1, p2
        d = float(random.randrange(5, 100, 5)/10000)
        rad = 2*math.pi*random.uniform(0,1)
