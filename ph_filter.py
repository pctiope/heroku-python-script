import json
import base64
#from github import Github
from shapely.geometry import Point, Polygon, shape, mapping
from shapely.ops import unary_union

def filter(threshold, date_time):
    filename = "./temp/polygonized"+str(threshold)+".json"
    with open(filename) as f:
        data = json.load(f)
    sorted_data = sorted(data['features'], key=lambda x: x["properties"]["AQI"], reverse=True)
    temp = []
    for polygon in sorted_data:
        if polygon["properties"]["AQI"] >= threshold and polygon["properties"]["AQI"] <= 500:
            coordinates = polygon["geometry"]
            temp.append(shape(coordinates))
    
    highest_aqi_poly = [[[]]]
    aqi_highest_poly = sorted_data[0]["properties"]["AQI"]
    highest_aqi_poly = mapping(temp[0])["coordinates"]
    #print(highest_aqi_poly, aqi_highest_poly)
    exclude_poly = [[[]]]
    if len(temp):
        unions = unary_union(temp)
        # print(mapping(unions)["coordinates"])
        if (isinstance(mapping(unions)["coordinates"],list)):
            exclude_poly = [poly[0] for poly in mapping(unions)["coordinates"]]
        elif (isinstance(mapping(unions)["coordinates"],tuple)):
            exclude_poly = mapping(unions)["coordinates"]
        else:
            print("Something went wrong")
    # print(exclude_poly)

    output_dict = {"type": "FeatureCollection", "name": "filtered_output", "threshold": threshold, "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": [{"type": "Feature", "properties":{}, "geometry": {"type": "Polygon","coordinates": exclude_poly}}]}
    json_output = json.dumps(output_dict, indent=4)
    with open("./temp/filtered"+str(threshold)+".json", "w") as outfile:
        outfile.write(json_output)
        
    return highest_aqi_poly, aqi_highest_poly
    
    '''coded_string = "Z2hwXzY3emJ2MGpUdkZRVjdJR201ZXpNSWQ1dU5tOWFHRzNiakp3Tg=="
    g = Github(base64.b64decode(coded_string).decode("utf-8"))
    repo = g.get_repo("pctiope/express-leaflet")
    contents = repo.get_contents("/public/filtered.json", ref="main")
    repo.update_file(contents.path, "updated filtered.json", json_output, contents.sha, branch="main")'''