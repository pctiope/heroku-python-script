import random
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import nearest_points

def random_waypoints(poly, max_poly):
    '''print(poly, type(poly))
    print(max_poly, type(max_poly))'''
    if max_poly is not None:
        polydiff = poly.difference(max_poly)
        minxdiff, minydiff, maxxdiff, maxydiff = polydiff.bounds
        '''print(polydiff, type(polydiff))'''
    else:
        minxdiff, minydiff, maxxdiff, maxydiff = poly.bounds
    '''if len(max_poly[0][0]) > 0:
        obj = mapping(Polygon(max_poly[0]))
        mp_coords = obj['coordinates'][0]
        print(mp_coords)
    else:
        mp_coords = None'''
    while True:
        p1 = Point(random.uniform(minxdiff, maxxdiff), random.uniform(minydiff, maxydiff))
        p2 = Point(random.uniform(minxdiff, maxxdiff), random.uniform(minydiff, maxydiff))
        if poly.contains(p1) and poly.contains(p2):
            print('contains', p1, p2)
            return p1, p2
