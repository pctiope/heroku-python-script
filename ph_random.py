import random
from shapely.geometry import Point
import math
import random

def random_waypoints(poly,Xo,Yo):
    while True:
        d1 = float(random.randrange(25, 100, 5)/10000)
        rad1 = 2*math.pi*random.uniform(0,1)
        p1 = Point(Xo+d1*math.cos(rad1),Yo+d1*math.sin(rad1))
        if not poly.contains(p1):
            continue
        
        d2 = float(random.randrange(25, 100, 5)/10000)
        rad2 = 2*math.pi*random.uniform(0,1)
        p1 = Point(Xo+d2*math.cos(rad2),Yo+d2*math.sin(rad2))
        p2 = Point(Xo-d2*math.cos(rad2),Yo-d2*math.sin(rad2))
        # print(d, 'distance', rad, 'radian, ', p1, 'p1, ', p2, 'p2')
        if poly.contains(p1) and poly.contains(p2):
            return p1, p2
