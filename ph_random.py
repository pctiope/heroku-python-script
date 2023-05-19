import random
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import nearest_points

def random_waypoints(poly, max_poly):
     minx, miny, maxx, maxy = poly.bounds
     if len(max_poly[0][0]) > 0:
         #print(Polygon(max_poly[0]))
         #mp_coords = None
         #mp_coords = list(Polygon(zip(max_poly[0])).exterior.coords)
         obj = mapping(Polygon(max_poly[0]))
         mp_coords = obj['coordinates'][0]
         print(mp_coords)
     else:
         mp_coords = None
     while True:
         if mp_coords != None:
            mp = Point(random.choice(mp_coords))
            print(mp) 
            np_coords = list(nearest_points(poly, mp))
            np = Point(random.choice(np_coords))
            print(np, 'nearest')
         else:
            np = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         if poly.contains(p) and poly.contains(np):
             print('contains', np, )
             return np, p
