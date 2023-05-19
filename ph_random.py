import random
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import nearest_points

def random_waypoints(poly, max_poly):
     minx, miny, maxx, maxy = poly.bounds
     if len(max_poly[0]) > 0:
         max_poly_only = Polygon(max_poly[0])
         print(max_poly_only)
         obj = mapping(max_poly_only)
         mp_coords = max_poly_only['coordinates']
         #mp_coords = None
     else:
         mp_coords = None
     while True:
         if mp_coords != None:
            mp = random.choice(mp_coords)
            np_coords = list(nearest_points(poly, mp))
            np = random.choice(np_coords).wkt
         else:
            np = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         if poly.contains(p) and poly.contains(np):
             return np, p
