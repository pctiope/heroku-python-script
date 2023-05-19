import random
from shapely.geometry import Point
from shapely.ops import nearest_points

def random_waypoints(poly, max_poly):
     minx, miny, maxx, maxy = poly.bounds
     mp_coords = list(max_poly.exterior.coords)
     while True:
         mp = random.choice(mp_coords)
         np_coords = list(nearest_points(poly, mp))
         np = random.choice(np_coords).wkt
         p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         if poly.contains(np) and poly.contains(p):
             return np, p
