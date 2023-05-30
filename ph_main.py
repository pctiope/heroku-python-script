from time import sleep
from datetime import datetime
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
import json
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
import random
from ph_initial import export_initial


with open("./metro_manila.geojson") as f:
        data = json.load(f)

class Sensor:
     def __init__(self,name,x,y,aqi):
        self.name = name
        self.x = x
        self.y = y
        self.aqi = aqi

format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
while 1:
        date_time = datetime.now().strftime(format)
        WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
        Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
        df_to_csv(df, date_time)
        df_to_shp(df, date_time)
        get_idw(date_time)
        rmse_list = []
        for power in range(1,11):
                original_value, interpolated_value = get_error(date_time, power)
                rmse = mean_squared_error(original_value, interpolated_value, squared=False)
                rmse_list.append([power, rmse])
                print(f"RMSE (power={power}):", rmse)
        rmse_list = sorted(rmse_list, key=lambda x: x[1])
        print(f"Best power: {rmse_list[0][0]}")
        export_initial(date_time, df, rmse_list)
        max_AQI = max(int(i) for i in US_AQI)
        poly = Polygon(data['features'][0]['geometry']['coordinates'][0][0])
        sensors = []
        for i in range(len(Sensor_Name)):
             sensors.append(Sensor(Sensor_Name[i],X_location[i],Y_location[i],US_AQI[i]))
        sensors = sorted(sensors, key=lambda x: x.aqi, reverse=True)
        top_rand = random.randint(0, len(sensors)//2)
        print(sensors[top_rand].x,sensors[top_rand].y)
        first_point, second_point = random_waypoints(poly, sensors[top_rand].x, sensors[top_rand].y)
        coords = [[first_point.x, first_point.y], [second_point.x, second_point.y]]
        threshold = max_AQI
        print(f"threshold: {str(threshold)}")
        polygonize(threshold, date_time)
        
        exclude_poly, area_diff = filter(threshold, date_time, poly)
        print(area_diff, 'area diff percentage')
        route_exposure, total_route = generate_route(coords, threshold, date_time)
        sleep(2)
        normal_exposure, total_normal = generate_normal(coords, threshold, date_time)
        old_route_exp, old_normal_exp = route_exposure, normal_exposure
        old_total_route, old_total_normal = total_route, total_normal
        print(route_exposure, normal_exposure, "route exposure, normal exposure")
        print(total_route, total_normal, "total route exposure, total normal exposure")
        i = max_AQI - 1
        while i > 0:
                threshold = i
                print(f"threshold: {str(threshold)}")
                polygonize(threshold, date_time)
                exclude_poly, area_diff = filter(threshold, date_time, poly)
                route_exposure, total_route = generate_route(coords, threshold, date_time)
                sleep(2)
                if route_exposure is None and total_route is None:
                        route_exposure, total_route = generate_route(coords, threshold, date_time)
                        print(route_exposure, normal_exposure, "route exposure, normal exposure")
                        print(total_route, total_normal, "total route exposure, total normal exposure")
                        print(area_diff, 'area diff percentage')
                        break
                if (route_exposure is not None and total_route is not None) and (route_exposure != old_route_exp or normal_exposure != old_normal_exp or total_route != old_total_route or total_normal != old_total_normal):
                    print(route_exposure, normal_exposure, "route exposure, normal exposure")
                    print(total_route, total_normal, "total route exposure, total normal exposure")
                    print(area_diff, 'area diff percentage')
                    i -= 1
                else:
                    i -= 5
                old_route_exp, old_normal_exp, old_threshold = route_exposure, normal_exposure, threshold
                old_total_route, old_total_normal = total_route, total_normal