from routingpy import Valhalla
from routingpy.utils import decode_polyline6
from shapely.geometry import Point, Polygon, shape, mapping
import json
import math
import base64
from time import sleep
from github import Github

def calculate(result, threshold):
    polyline = result.raw["trip"]["legs"][0]["shape"]
    decoded = decode_polyline6(polyline)
    route_points = [list(element) for element in decoded]
    aqi = []
    temp = []
    total = 0
    with open("./temp/polygonized"+str(threshold)+".json") as f:
        data = json.load(f)
    data['features'] = sorted(data['features'], key=lambda x: x["properties"]["AQI"], reverse=True)
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
    total_distest = 0
    for i in range(len(aqi)-1):
        x_distance += int(110.574)*(aqi[i][1].x-aqi[i+1][1].x)
        y_distance += int(111.320)*math.cos((aqi[i][1].y+aqi[i+1][1].y)/2)*(aqi[i][1].y-aqi[i+1][1].y)
        level = aqi[i][0][1]
        distance = math.sqrt((abs(aqi[i][1].x-aqi[i+1][1].x))**2+(abs(aqi[i][1].y-aqi[i+1][1].y))**2)
        total += distance*level
        total_distest += distance
    return total/total_distest

def generate_route(coords, threshold):
    client = Valhalla(base_url='https://valhalla1.openstreetmap.de')

    with open("./temp/filtered"+str(threshold)+".json","r") as f:
        data = json.load(f)
        exclude_poly = data["features"][0]["geometry"]["coordinates"]
        print(exclude_poly)
        if exclude_poly == [[[]]]:
            route = client.directions(locations=coords,instructions=True,profile="pedestrian")
        else:
            route = client.directions(locations=coords,instructions=True,profile="pedestrian",avoid_polygons=exclude_poly)
    route = client.directions(locations=coords,instructions=True,profile="pedestrian",avoid_polygons=exclude_poly)
    output_dict = {"type": "FeatureCollection", "name": "filtered_output", "threshold": threshold, "features": [{"type": "Feature", "properties":{}, "geometry": {"type": "Polygon","coordinates": exclude_poly}},{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[0]}},{"type": "Feature", "properties":{}, "geometry": {"type": "Point","coordinates": coords[1]}}]}
    json_output = json.dumps(output_dict, indent=4)
    route_output = json.dumps(route.raw, indent=4)
    coded_string = "Z2hwXzY3emJ2MGpUdkZRVjdJR201ZXpNSWQ1dU5tOWFHRzNiakp3Tg=="
    g = Github(base64.b64decode(coded_string).decode("utf-8"))
    repo = g.get_repo("pctiope/heroku-python-script")
    contents = repo.get_contents("/geojson/route.geojson", ref="dev")
    repo.update_file(contents.path, "updated route.geojson", json_output, contents.sha, branch="dev")
    contents = repo.get_contents("/results/route_results.raw", ref="dev")
    repo.update_file(contents.path, "updated route_results.raw", route_output, contents.sha, branch="dev")
    return calculate(route, threshold)