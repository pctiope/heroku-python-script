import json

def export_idw_results(date_time, df, rmse_list):
    json_output = df.to_dict(orient='index')
    json_output['power and rmse'] = dict(rmse_list)
    json_output['date_time'] = date_time
    outfile = json.dumps(json_output, indent=4)
    with open("./idw_results/idw_"+str(date_time)+".json","w") as f:
        f.write(outfile)

def export_routing_results(date_time, sensor, waypoint_coords, average_route_exposure, total_route_exposure, area_diff):
    json_output = {}
    json_output['date_time'] = date_time
    json_output['sensor'] = {'sensor_name': sensor.name, 'sensor_X': sensor.x, 'sensor_y': sensor.y, 'sensor_aqi': sensor.aqi}
    json_output['waypoints'] = waypoint_coords
    json_output['average_route_exposure'] = average_route_exposure
    json_output['total_route_exposure'] = total_route_exposure
    json_output['excluded_area_ratio'] = area_diff
    outfile = json.dumps(json_output, indent=4)
    with open("./route_results/route_"+str(date_time)+".json","w") as f:
        f.write(outfile)
