from routingpy import Valhalla
from routingpy.utils import decode_polyline6
from shapely.geometry import Point, shape
import json
import math
from time import sleep

def process_route_results(date_time, route):
    summary = route.raw["trip"]["summary"]
    polyline = route.raw["trip"]["legs"][0]["shape"]
    decoded = decode_polyline6(polyline)
    route_points = [list(element) for element in decoded]

    with open(f"./polygonized/polygonized_{str(date_time)}.json") as f:
        data = json.load(f)
        data['features'] = sorted(data['features'], key=lambda x: x["properties"]["AQI"], reverse=True)

    aqi = []
    temp = []
    points = [Point(i[0], i[1]) for i in route_points]
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
    total = 0
    total_distance = 0
    for i in range(len(aqi)-1):
        x_distance += int(110.574)*(aqi[i][1].x-aqi[i+1][1].x)
        y_distance += int(111.320)*math.cos((aqi[i][1].y+aqi[i+1][1].y)/2)*(aqi[i][1].y-aqi[i+1][1].y)
        level = aqi[i][0][1]
        distance = math.sqrt((abs(aqi[i][1].x-aqi[i+1][1].x))**2+(abs(aqi[i][1].y-aqi[i+1][1].y))**2)
        total += distance*level
        total_distance += distance

    return total, total_distance, summary, route_points

def generate_route(coords, threshold, date_time):
    sleep(2)
    client = Valhalla(base_url='https://valhalla1.openstreetmap.de')
    with open(f"./filtered/filtered_{str(date_time)}_{str(threshold)}.json", "r") as f:
        data = json.load(f)
        exclude_poly = data["features"][0]["geometry"]["coordinates"]
    
    if len(exclude_poly[0][0]):
        try:
            route = client.directions(locations=coords,instructions=True,profile="pedestrian",avoid_polygons=exclude_poly)
            output_dict = {"type": "FeatureCollection", "name": "filtered_output", "threshold": threshold, "features": [{"type": "Feature", "properties":{}, "geometry": {"type": "Polygon","coordinates": exclude_poly}},{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[0]}},{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[1]}}]}
        except Exception:
            return None, None, None
    else:
        route = client.directions(locations=coords,instructions=True,profile="pedestrian")
        output_dict = {"type": "FeatureCollection", "name": "filtered_output", "threshold": threshold, "features": [{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[0]}},{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[1]}}]}

    total, total_distance, summary, route_points = process_route_results(date_time, route)
    output_dict['features'].append({"type": "Feature", "properties":{}, "geometry": {"type": "LineString","coordinates": route_points}})

    route_output = json.dumps(route.raw, indent=4)
    with open(f"./route/route_{str(date_time)}_{str(threshold)}.json", "w") as f:
        f.write(route_output)

    output = json.dumps(output_dict, indent=4)
    with open(f"./results/results_{str(date_time)}_{str(threshold)}.json", "w") as f:
        f.write(output)

    return total/total_distance, total, summary

def generate_normal(coords, threshold, date_time):
    sleep(2)
    client = Valhalla(base_url='https://valhalla1.openstreetmap.de')
    normal = client.directions(locations=coords,instructions=True,profile="pedestrian")
    normal_output = json.dumps(normal.raw, indent=4)

    with open(f"./normal/normal_{str(date_time)}.json", "w") as f:
        f.write(normal_output)

    total, total_distance, summary, route_points = process_route_results(date_time, normal)

    return total/total_distance, total, summary