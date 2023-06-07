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

    with open(f"./results/{date_time}/polygonized.json", "r") as f:
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

def generate_route(coords, threshold, date_time, exclude_poly):
    #sleep(5)
    client = Valhalla(base_url='http://localhost:8002')
    
    visualization = {"type": "FeatureCollection", "name": "filtered_output", "threshold": threshold, "features": [{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[0]}},{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[1]}},{"type": "Feature", "properties":{}, "geometry": {"type": "Polygon","coordinates": exclude_poly}}]}

    try:
        # route = client.directions(locations=coords,instructions=True,profile="pedestrian",avoid_polygons=exclude_poly)
        route = client.directions(locations=coords,instructions=True,profile="bicycle",avoid_polygons=exclude_poly)
    except Exception as err:
        print(f"Error with finding AQI routing: {str(err)}") 
        return None, None, None, visualization, err

    total, total_distance, summary, route_points = process_route_results(date_time, route)
    visualization['features'].append({"type": "Feature", "properties":{}, "geometry": {"type": "LineString","coordinates": route_points}})

    route_output = json.dumps(route.raw, indent=4)
    with open(f"./results/{date_time}/route_{str(threshold)}.json", "w") as f:
        f.write(route_output)

    return total/total_distance, total, summary, visualization, None

def generate_normal(coords, threshold, date_time):
    #sleep(5)
    client = Valhalla(base_url='http://localhost:8002')
    
    try:
        # normal = client.directions(locations=coords,instructions=True,profile="pedestrian")
        normal = client.directions(locations=coords,instructions=True,profile="bicycle")
    except Exception as err:
        print(f"Error with finding normal routing: {str(err)}")              # IMPORTANT: case if normal routing throws an exception
        return None, None, None, None

    normal_output = json.dumps(normal.raw, indent=4)
    with open(f"./results/{date_time}/normal.json", "w") as f:
        f.write(normal_output)

    total, total_distance, summary, route_points = process_route_results(date_time, normal)

    return total/total_distance, total, summary, route_points