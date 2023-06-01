import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

import os
from time import sleep
from datetime import datetime
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
import json
import random
from sklearn.metrics import mean_squared_error

from ph_aqi import init_sensors, get_sensor_data, df_to_csv, df_to_shp
from ph_idw import get_idw, get_error
from ph_polygonize import polygonize
from ph_filter import filter
from ph_routing import generate_route, generate_normal
from ph_random import random_waypoints
from ph_export import export_idw_results, export_routing_results

class AQI_Sensor:
    def __init__(self,name,x,y,aqi):
        self.name = name
        self.x = x
        self.y = y
        self.aqi = aqi

while 1:
    dt_format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
    date_time = datetime.now().strftime(dt_format)
    # date_time = "" # empty date_time to lessen file generation (comment if needed)
    results_path = "./results/"
    path = os.path.join(results_path, date_time)
    try:
        os.makedirs(path, exist_ok = True)
        print("Directory '%s' created successfully" % path)
    except OSError as error:
        print("Directory '%s' can not be created" % path)

    # get AQI sensor data
    WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
    Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
    # df_to_csv(df, date_time)
    df_to_shp(df, date_time)

    # IDW methods
    rmse_list = []
    for power in range(1,11):
            original_value, interpolated_value = get_error(date_time, power)
            rmse = mean_squared_error(original_value, interpolated_value, squared=False)
            rmse_list.append([power, rmse])
            print(f"RMSE (power={power}):", rmse)
    rmse_list = sorted(rmse_list, key=lambda x: x[1])
    print(f"Best power: {rmse_list[0][0]}")
    get_idw(date_time, rmse_list[0][0])
    export_idw_results(date_time, df, rmse_list)

    # get border polygon
    with open("./metro_manila.geojson") as f:
        data = json.load(f)
        border_poly = Polygon(data['features'][0]['geometry']['coordinates'][0][0])

    sensors = [
        AQI_Sensor(Sensor_Name[i], X_location[i], Y_location[i], US_AQI[i])
        for i in range(len(Sensor_Name))
    ]
    sensors = sorted(sensors, key=lambda x: x.aqi, reverse=True)
    top_rand = random.randint(0, len(sensors)//2)
    # print(sensors[top_rand].x,sensors[top_rand].y)

    # get pseudorandom waypoints for routing, centered around top random sensor
    first_point, second_point = random_waypoints(border_poly, sensors[top_rand].x, sensors[top_rand].y)
    waypoint_coords = [[first_point.x, first_point.y], [second_point.x, second_point.y]]

    max_AQI = max(int(i) for i in US_AQI)
    threshold = max_AQI

    polygonize(date_time)

    average_normal_exposure, total_normal_exposure, normal_summary, normal_route_points = generate_normal(waypoint_coords, threshold, date_time)
    routing_results = {
        "selected middle sensor": sensors[top_rand].name,
        "selected sensor location": [sensors[top_rand].x, sensors[top_rand].y],
        "selected sensor AQI": sensors[top_rand].aqi,
        "waypoint coordinates": waypoint_coords,
        "average_normal_exposure": average_normal_exposure,
        "total_normal_exposure": total_normal_exposure
    }

    # calculate total and average exposure of different thresholds
    route_exposure_history = [] # tuples of (average_route_exposure, total_route_exposure)
    old_average_route_exposure, old_total_route_exposure = average_normal_exposure, total_normal_exposure
    old_route_summary = {}
    old_area_diff = 0
    while threshold > 0:
        print(f"threshold={str(threshold)}:")
        routing_results[str(threshold)] = {}

        exclude_poly, area_diff = filter(threshold, date_time, border_poly)
        routing_results[str(threshold)]["Exclude Polygon"] = exclude_poly
        routing_results[str(threshold)]["Exclude Area Ratio"] = area_diff

        average_route_exposure, total_route_exposure, route_summary, visualization, err = generate_route(waypoint_coords, threshold, date_time)
        
        if len(route_exposure_history):
            if (route_exposure_history[-1][0] != average_route_exposure or route_exposure_history[-1][1] != total_route_exposure):
                threshold -= 1
            else:
                threshold -= 5
        else:
            threshold -= 1

        route_exposure_history.append((average_route_exposure, total_route_exposure))
        visualization['features'].append({"type": "Feature", "properties":{}, "geometry": {"type": "LineString","coordinates": normal_route_points}})
        if err is None:    
            routing_results[str(threshold)]["Error"] = "None"
            routing_results[str(threshold)]["average_route_exposure"] = average_route_exposure
            routing_results[str(threshold)]["total_route_exposure"] = total_route_exposure
            routing_results[str(threshold)]["route summary"] = route_summary
        else:   # if there was an error in routing, just use normal route results
            routing_results[str(threshold)]["Error"] = err
            routing_results[str(threshold)]["average_route_exposure"] = average_normal_exposure
            routing_results[str(threshold)]["total_route_exposure"] = total_normal_exposure
            routing_results[str(threshold)]["route summary"] = normal_summary
        
        routing_results[str(threshold)]["visualization"] = visualization

    export_routing_results(date_time, routing_results)
    sleep(5)