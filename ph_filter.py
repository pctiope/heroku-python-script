import json
from shapely.geometry import Polygon, shape, mapping
from pyproj import Geod
from shapely.ops import unary_union

def filter(threshold, date_time, poly):
    geod = Geod(ellps="WGS84")
    with open(f"./results/{date_time}/polygonized.json", "r") as f:
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
        # print(abs(poly_area), 'poly area')

    maps = Polygon(poly)
    maps_area, maps_perimeter = geod.geometry_area_perimeter(maps)

    # output_dict = {"type": "FeatureCollection", "name": "filtered_output", "threshold": threshold, "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": [{"type": "Feature", "properties":{}, "geometry": {"type": "Polygon","coordinates": exclude_poly}}]}
    # json_output = json.dumps(output_dict, indent=4)
    # with open(f"./results/{date_time}/filtered_{threshold}.json", "w") as outfile:
    #     outfile.write(json_output)

    return exclude_poly, abs(poly_area/maps_area)*100
    
