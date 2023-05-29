import json
import base64
from github import Github
from shapely.geometry import Point, Polygon, shape, mapping
from pyproj import Geod
from shapely.ops import unary_union

def filter(threshold, date_time, poly):
    geod = Geod(ellps="WGS84")
    filename = "./temp/polygonized"+str(threshold)+".json"
    with open(filename) as f:
        data = json.load(f)
    sorted_data = sorted(data['features'], key=lambda x: x["properties"]["AQI"], reverse=True)
    temp = []
    for polygon in sorted_data:
        if polygon["properties"]["AQI"] >= threshold and polygon["properties"]["AQI"] <= 500:
            coordinates = polygon["geometry"]
            temp.append(shape(coordinates))
    
    exclude_poly = [[[]]]
    poly_area = 0
    if len(temp):
        unions = unary_union(temp)
        if (isinstance(mapping(unions)["coordinates"], list)):
            exclude_poly = [poly[0] for poly in mapping(unions)["coordinates"]]
            poly_area, poly_perimeter = geod.geometry_area_perimeter(Polygon(exclude_poly[0]))
        elif (isinstance(mapping(unions)["coordinates"], tuple)):
            exclude_poly = mapping(unions)["coordinates"]
            poly_area, poly_perimeter = geod.geometry_area_perimeter(Polygon(exclude_poly[0]))
        else:
            print("Something went wrong")
        print(poly_area, 'poly area')
    
    maps = Polygon(poly)
    maps_area, maps_perimeter = geod.geometry_area_perimeter(maps)

    output_dict = {"type": "FeatureCollection", "name": "filtered_output", "threshold": threshold, "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": [{"type": "Feature", "properties":{}, "geometry": {"type": "Polygon","coordinates": exclude_poly}}]}
    json_output = json.dumps(output_dict, indent=4)
    
    with open("./temp/filtered"+str(threshold)+".json", "w") as outfile:
        outfile.write(json_output)

    coded_string = "Z2hwXzY3emJ2MGpUdkZRVjdJR201ZXpNSWQ1dU5tOWFHRzNiakp3Tg=="
    g = Github(base64.b64decode(coded_string).decode("utf-8"))
    repo = g.get_repo("pctiope/express-leaflet")
    contents = repo.get_contents("/public/filtered.json", ref="main")
    repo.update_file(contents.path, "updated filtered.json", json_output, contents.sha, branch="main")

    return exclude_poly, abs(poly_area/maps_area)*100
    
