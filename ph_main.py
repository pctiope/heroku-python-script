from datetime import datetime
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
import json
import random

import warnings
from sklearn.metrics import mean_squared_error
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from ph_aqi import init_sensors, get_sensor_data, df_to_csv, df_to_shp
from ph_idw import get_idw, get_error
from ph_polygonize import polygonize
from ph_filter import filter
from ph_routing import generate_route
from ph_normal import generate_normal
from ph_random import random_waypoints
from ph_export import export_idw_results, export_routing_results
from ph_update import update

class AQI_Sensor:
     def __init__(self,name,x,y,aqi):
        self.name = name
        self.x = x
        self.y = y
        self.aqi = aqi

dt_format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
while 1:
     # get AQI sensor data
     date_time = datetime.now().strftime(dt_format)
     WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
     Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
     df_to_csv(df, date_time)
     df_to_shp(df, date_time)

     # IDW methods
     get_idw(date_time)
     rmse_list = []
     for power in range(1,11):
             original_value, interpolated_value = get_error(date_time, power)
             rmse = mean_squared_error(original_value, interpolated_value, squared=False)
             rmse_list.append([power, rmse])
             print(f"RMSE (power={power}):", rmse)
     rmse_list = sorted(rmse_list, key=lambda x: x[1])
     print(f"Best power: {rmse_list[0][0]}")
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

     #calculate total and average exposure of different thresholds
     polygonize(date_time)
     update(date_time, border_poly)
     average_normal_exposure, total_normal_exposure, normal_summary = generate_normal(waypoint_coords, threshold, date_time)
     export_routing_results(date_time, sensors[top_rand], waypoint_coords, average_normal_exposure, total_normal_exposure, normal_summary)
     old_average_route_exposure, old_total_route_exposure = average_normal_exposure, total_normal_exposure
     old_route_summary = {}
     old_area_diff = 0
     while threshold > 0:
             print(f"threshold: {str(threshold)}")

             exclude_poly, area_diff = filter(threshold, date_time, border_poly)

             average_route_exposure, total_route_exposure, route_summary = generate_route(waypoint_coords, threshold, date_time)
             
             if (average_route_exposure is None or total_route_exposure is None or route_summary is None):
                     average_route_exposure = old_average_route_exposure
                     total_route_exposure = old_total_route_exposure
                     route_summary = old_route_summary
                     area_diff = old_area_diff
                     if (average_route_exposure == average_normal_exposure and total_route_exposure == total_normal_exposure):
                          threshold = max_AQI
                     print(route_summary, "route summary")
                     print(area_diff, 'area diff percentage')
                     print(average_route_exposure, average_normal_exposure, "average route exposure, average normal exposure")
                     print(total_route_exposure, total_normal_exposure, "total route exposure, total normal exposure")
                     export_routing_results(date_time, sensors[top_rand], waypoint_coords, average_route_exposure, total_route_exposure, route_summary, area_diff, threshold)
                     break

             if (average_route_exposure != old_average_route_exposure or total_route_exposure != old_total_route_exposure):
                     print(route_summary, "route summary")
                     print(area_diff, 'area diff percentage')
                     print(average_route_exposure, average_normal_exposure, "average route exposure, average normal exposure")
                     print(total_route_exposure, total_normal_exposure, "total route exposure, total normal exposure")
                     export_routing_results(date_time, sensors[top_rand], waypoint_coords, average_route_exposure, total_route_exposure, route_summary, area_diff, threshold)
                     threshold -= 1
             else:
                     threshold -= 5

                
             old_average_route_exposure = average_route_exposure
             old_total_route_exposure = total_route_exposure
             old_route_summary = route_summary
             old_area_diff = area_diff

                