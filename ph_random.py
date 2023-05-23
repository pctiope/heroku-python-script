import random
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import nearest_points
import math
import random

def random_waypoints(poly,Xo,Yo):
    d = 0.02
    while True:
        rad = 2*math.pi*random.uniform(0,1)
        p1 = Point(Xo+d*math.cos(rad),Yo+d*math.sin(rad))
        p2 = Point(Xo-d*math.cos(rad),Yo-d*math.sin(rad))
        if poly.contains(p1) and poly.contains(p2):
            return p1, p2
