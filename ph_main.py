import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from time import sleep
from datetime import datetime
from shapely.geometry.polygon import Polygon
import json
import random
import os

from ph_aqi import init_sensors, get_sensor_data, df_to_shp
from ph_idw import get_idw
from ph_polygonize import polygonize
from ph_filter import filter

class AQI_Sensor:
    def __init__(self,name,x,y,aqi):
        self.name = name
        self.x = x
        self.y = y
        self.aqi = aqi

path = "./results/"
os.makedirs(path, exist_ok=True)
print(f"Directory '{path}' created successfully")

# get AQI sensor data
WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
df_to_shp(df)

# IDW methods
get_idw(2)

# get border polygon
with open("./metro_manila.geojson") as f:
    data = json.load(f)
    border_poly = Polygon(data['features'][0]['geometry']['coordinates'][0][0])
sensors = [
    AQI_Sensor(Sensor_Name[i], X_location[i], Y_location[i], US_AQI[i])
    for i in range(len(Sensor_Name))
]
sensors = sorted(sensors, key=lambda x: x.aqi, reverse=True)
print(sensors)

# polygonize and filter
max_AQI = max(int(i) for i in US_AQI)
threshold = max_AQI*random.randint(55, 95)/100
print(max_AQI, threshold)
polygonize()
filter(threshold, border_poly)
sleep(30)