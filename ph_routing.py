from routingpy import Valhalla
from routingpy.utils import decode_polyline6
from shapely.geometry import Point, Polygon, shape, mapping
import json

def generate_route(coords, threshold):
    client = Valhalla(base_url='https://valhalla1.openstreetmap.de')

    with open("./temp/filtered"+str(threshold)+".json","r") as f:
        data = json.load(f)
        exclude_poly = data["features"][0]["geometry"]["coordinates"]

    route = client.directions(locations=coords,instructions=True,profile="pedestrian",exclude_polygon=exclude_poly)

    '''json_output = json.dumps(route.raw, indent=4)
    with open("./temp/route_results"+date_time+".json","w") as f:
        f.write(json_output)'''
        
    polyline = route.raw["trip"]["legs"][0]["shape"]
    decoded = decode_polyline6(polyline)
    route = [list(element) for element in decoded]

    
    aqi = []
    temp = []
    total = 0
    with open("./temp/polygonized"+str(threshold)+".json") as f:
        data = json.load(f)
    data['features'] = sorted(data['features'], key=lambda x: x["properties"]["AQI"], reverse=True)
    print(data)
    for i in route:
        i[0], i[1] = i[1], i[0]
    points = [Point(i[0], i[1]) for i in route]
    for polygon in data['features']:
        if polygon["properties"]["AQI"] <= 500:
            coordinates = polygon["geometry"]
            temp.append([shape(coordinates),polygon["properties"]["AQI"]])
    for i in points:
        for j in temp:
            if j[0].contains(i):
                aqi.append([j,i])
                break
    for i in range(len(aqi)-1):
        distance = aqi[i][1].distance(aqi[i+1][1])
        level = aqi[i][0][1]
        total += distance*level
    print(total, "for threshold", threshold)
