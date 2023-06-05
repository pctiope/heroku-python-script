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
import pandas as pd
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

dt_format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
# date_time = "" # empty date_time to lessen file generation (comment if needed)
results_path = "./results/"
while 1:
    date_time = datetime.now().strftime(dt_format)
    path = os.path.join(results_path, date_time)
    # print(path)
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created successfully")
    except OSError as error:
        print(f"Directory '{path}' can not be created")
        break

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
    get_idw(date_time, 2)
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

    max_AQI = max(int(i) for i in US_AQI)
    threshold = max_AQI

    polygonize(date_time)

    normal_route_points = None
    while normal_route_points is None:
        # get pseudorandom waypoints for routing, centered around top random sensor
        top_rand = random.randint(0, len(sensors)//2)
        # print(sensors[top_rand].x,sensors[top_rand].y)
        first_point, second_point = random_waypoints(border_poly, sensors[top_rand].x, sensors[top_rand].y)
        waypoint_coords = [[first_point.x, first_point.y], [second_point.x, second_point.y]]
        
        average_normal_exposure, total_normal_exposure, normal_summary, normal_route_points = generate_normal(waypoint_coords, threshold, date_time)

    routing_results = {
        "selected middle sensor": sensors[top_rand].name,
        "selected sensor location": [sensors[top_rand].x, sensors[top_rand].y],
        "selected sensor AQI": sensors[top_rand].aqi,
        "waypoint coordinates": waypoint_coords,
        "average_normal_exposure": average_normal_exposure,
        "total_normal_exposure": total_normal_exposure,
        "max_aqi": max_AQI,
        "data": {}
    }

    # calculate total and average exposure of different thresholds
    threshold_history = []
    average_route_exp_history = []
    total_route_exp_history = []
    distance_route_history = []
    while threshold > 0:
        print(f"threshold: {str(threshold)}")
        routing_results['data'][threshold] = {}

        exclude_poly, area_diff = filter(threshold, date_time, border_poly)
        #routing_results['data'][threshold]["Exclude Polygon"] = exclude_poly
        routing_results['data'][threshold]["Exclude Area Ratio"] = area_diff

        average_route_exposure, total_route_exposure, route_summary, visualization, err = generate_route(waypoint_coords, threshold, date_time, exclude_poly)

        visualization['features'].append({"type": "Feature", "properties":{}, "geometry": {"type": "LineString","coordinates": normal_route_points}})
        if err is None:    
            routing_results['data'][threshold]["Error"] = "None"
            routing_results['data'][threshold]["average_route_exposure"] = average_route_exposure
            routing_results['data'][threshold]["total_route_exposure"] = total_route_exposure
            routing_results['data'][threshold]["route summary"] = route_summary

        else: # if there was an error in routing, just use normal route results
            routing_results['data'][threshold]["Error"] = str(err)
            routing_results['data'][threshold]["average_route_exposure"] = average_normal_exposure
            routing_results['data'][threshold]["total_route_exposure"] = total_normal_exposure
            routing_results['data'][threshold]["route summary"] = normal_summary

        routing_results['data'][threshold]["visualization"] = visualization

        threshold -= 1
        
        threshold_history.append(threshold)
        total_route_exp_history.append(routing_results['data'][threshold]["total_route_exposure"])
        average_route_exp_history.append(routing_results['data'][threshold]["average_route_exposure"])
        summary = routing_results['data'][threshold]["route summary"]
        distance_route_history.append(summary["length"])

        if (err is not None) and (err.message['error_code'] == 442):
            break

    total_normal_exp_history = [total_normal_exposure for _ in range(len(threshold_history))]
    average_normal_exp_history = [average_normal_exposure for _ in range(len(threshold_history))]
    distance_normal_history = [normal_summary["length"] for _ in range(len(threshold_history))]
    df = pd.DataFrame({'threshold': threshold_history,
                       'normal_distance': distance_normal_history,
                       'aqi_distance': distance_route_history,
                       'average_normal_exp': average_normal_exp_history,
                       'average_route_exp': average_route_exp_history,
                       'total_normal_exp': total_normal_exp_history,
                       'total_route_exp': total_route_exp_history})
    df_to_csv(df,date_time)

    export_routing_results(date_time, routing_results)
    #sleep(5)