import random
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import nearest_points
import math
import random

def random_waypoints(poly,sensor_one,sensor_two):
    Xo_1 = sensor_one.x
    Yo_1 = sensor_one.y
    Xo_2 = sensor_two.x
    Yo_2 = sensor_two.y
    d = 0.005
    while True:
        rad = 2*math.pi*random.uniform(0,1)
        p1 = Point(Xo_1+d*math.cos(rad),Yo_1+d*math.sin(rad))
        p2 = Point(Xo_2-d*math.cos(rad),Yo_2-d*math.sin(rad))
        if poly.contains(p1) and poly.contains(p2):
            return p1, p2
