import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from time import sleep
from datetime import datetime
from shapely.geometry.polygon import Polygon
import json
import random
from sklearn.metrics import mean_squared_error

from ph_aqi import init_sensors, get_sensor_data
from ph_idw import get_idw, get_error
from ph_polygonize import polygonize
from ph_filter import filter

class AQI_Sensor:
    def __init__(self,name,x,y,aqi):
        self.name = name
        self.x = x
        self.y = y
        self.aqi = aqi

date_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
# get AQI sensor data
WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)

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
threshold = max_AQI*random.randint(55, 95)/100
polygonize(date_time)
filter(threshold, date_time, border_poly)
sleep(60)