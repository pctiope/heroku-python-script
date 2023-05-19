import random
from shapely.geometry import Point
from shapely.ops import nearest_points

def random_waypoints(poly, max_poly):
     minx, miny, maxx, maxy = poly.bounds
     mp_coords = list(max_poly.exterior.coords)
     while True:
         if len(mp_coords) > 0:
            mp = random.choice(mp_coords)
            np_coords = list(nearest_points(poly, mp))
            np = random.choice(np_coords).wkt
         else:
            np = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         if poly.contains(p) and poly.contains(np):
             return np, p
