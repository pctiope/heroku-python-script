from time import sleep
from datetime import datetime
from random import randint
import os
from ph_aqi import init_sensors, get_sensor_data, df_to_csv, df_to_shp
from ph_idw import get_idw
from ph_polygonize import polygonize
from ph_filter import filter
from github import Github
import base64
import json

while 1:
    format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
    date_time = datetime.now().strftime(format)

    #ph_aqi functions
    WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
    Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
    df_to_csv(df, date_time)
    df_to_shp(df, date_time)

    #ph_idw functions
    get_idw(date_time)

    #ph_polygonize functions
    max_AQI = max([int(i) for i in US_AQI])
    threshold = randint(2*max_AQI//3,max_AQI)
    print("threshold: "+str(threshold))
    polygonize(threshold, date_time)

    #ph_filter functions
    filter(threshold, date_time)

    # Path
    path = "./temp/filtered.json"
    # Check whether a path pointing to a file
    isFile = os.path.isfile(path)
    print(isFile)

    filename = "./temp/filtered.json"
    with open(filename) as f:
        data = json.load(f)
    json_output = json.dumps(data, indent=4)
    coded_string = "Z2hwXzY3emJ2MGpUdkZRVjdJR201ZXpNSWQ1dU5tOWFHRzNiakp3Tg=="
    g = Github(base64.b64decode(coded_string).decode("utf-8"))
    repo = g.get_repo("pctiope/express-leaflet")
    contents = repo.get_contents("/public/filtered.json", ref="main")
    repo.update_file(contents.path, "updated filtered.json", json_output, contents.sha, branch="main")

    sleep(15)    # temporary