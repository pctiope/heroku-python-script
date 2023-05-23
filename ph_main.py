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
from ph_random import random_waypoints

with open("./metro_manila.geojson") as f:
        data = json.load(f)

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
    max_poly = filter(threshold, date_time)
    old_max_poly = max_poly
    print(max_poly)
    poly = Polygon(data['features'][0]['geometry']['coordinates'][0][0])
    temp = 0
    max_idx = None
    for idx,aqi in enumerate(US_AQI):
         if aqi > temp:
              temp = aqi
              max_idx = idx
    first_point, second_point = random_waypoints(poly, X_location[max_idx], Y_location[max_idx])          
    coords = [[first_point.x, first_point.y], [second_point.x, second_point.y]]
    route_exposure, normal_exposure = generate_route(coords, threshold)
    print(route_exposure, normal_exposure, "route exposure, normal exposure")
    old_route_exp = route_exposure
    old_normal_exp = normal_exposure
    for i in range(max_AQI-1, 0, -1):
        threshold = i
        print("threshold: "+str(threshold))
        polygonize(threshold, date_time)
        max_poly = filter(threshold, date_time)
        '''if max_poly != old_max_poly:
            print(max_poly)'''
        old_max_poly = max_poly
        route_exposure, normal_exposure = generate_route(coords, threshold)
        if route_exposure != old_route_exp or normal_exposure != old_normal_exp:
            print(route_exposure, normal_exposure, "route exposure, normal exposure")
        old_route_exp = route_exposure
        old_normal_exp = normal_exposure
    #sleep(60)    # temporary