from time import sleep
from datetime import datetime
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
import json
from ph_aqi import init_sensors, get_sensor_data, df_to_csv, df_to_shp
from ph_idw import get_idw
from ph_polygonize import polygonize
from ph_filter import filter
from ph_routing import generate_route
from ph_normal import generate_normal
from ph_random import random_waypoints
import random

with open("./metro_manila.geojson") as f:
        data = json.load(f)

class Sensor:
     def __init__(self,name,x,y,aqi):
        self.name = name
        self.x = x
        self.y = y
        self.aqi = aqi

while 1:
    format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
    date_time = datetime.now().strftime(format)
    WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
    Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
    df_to_csv(df, date_time)
    df_to_shp(df, date_time)
    get_idw(date_time)
    max_AQI = max([int(i) for i in US_AQI])
    threshold = max_AQI
    print("threshold: "+str(threshold))
    polygonize(threshold, date_time)
    exclude_poly = filter(threshold, date_time)
    print(exclude_poly)
    poly = Polygon(data['features'][0]['geometry']['coordinates'][0][0])
    
    sensors = []
    for i in range(len(Sensor_Name)):
         sensors.append(Sensor(Sensor_Name[i],X_location[i],Y_location[i],US_AQI[i]))
    sensors = sorted(sensors, key=lambda x: x.aqi, reverse=True)
    top5_rand = random.randint(0,2)
    print(sensors[top5_rand].x,sensors[top5_rand].y)
    first_point, second_point = random_waypoints(poly, sensors[0].x, sensors[0].y)
    coords = [[first_point.x, first_point.y], [second_point.x, second_point.y]]
    route_exposure = generate_route(coords, threshold)
    sleep(5)
    normal_exposure = generate_normal(coords, threshold)
    old_route_exp, old_normal_exp = route_exposure, normal_exposure
    print(route_exposure, normal_exposure, "route exposure, normal exposure")
    i = max_AQI - 1
    while i > 0:
        threshold = i
        print("threshold: "+str(threshold))
        polygonize(threshold, date_time)
        exclude_poly = filter(threshold, date_time)
        route_exposure = generate_route(coords, threshold)
        if route_exposure > old_route_exp or route_exposure == None:
            route_exposure = generate_route(coords, old_threshold)
            print(old_route_exp, old_normal_exp, "route exposure, normal exposure")
            break
        if route_exposure != old_route_exp or normal_exposure != old_normal_exp:
            print(route_exposure, normal_exposure, "route exposure, normal exposure")
            i -= 1
        else:
            i -= 5
        old_route_exp, old_normal_exp, old_threshold = route_exposure, normal_exposure, threshold