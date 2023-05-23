from routingpy import Valhalla
from routingpy.utils import decode_polyline6
from shapely.geometry import Point, Polygon, shape, mapping
import json
import math

def generate_normal(coords, threshold):
    client = Valhalla(base_url='https://valhalla1.openstreetmap.de')

    with open("./temp/filtered"+str(threshold)+".json","r") as f:
        data = json.load(f)
        exclude_poly = data["features"][0]["geometry"]["coordinates"]

    route = client.directions(locations=coords,instructions=True,profile="pedestrian")
    #print(route)

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
    x_distance = 0
    y_distance = 0
    total_distest = 0
    for i in range(len(aqi)-1):
        #print(aqi[i][1].x,aqi[i][1].y)
        x_distance += int(110.574)*(aqi[i][1].x-aqi[i+1][1].x)
        y_distance += int(111.320)*math.cos((aqi[i][1].y+aqi[i+1][1].y)/2)*(aqi[i][1].y-aqi[i+1][1].y)
        level = aqi[i][0][1]
        distance = math.sqrt((abs(aqi[i][1].x-aqi[i+1][1].x))**2+(abs(aqi[i][1].y-aqi[i+1][1].y))**2)
        total += distance*level
        total_distest += distance
    return total/total_distest
