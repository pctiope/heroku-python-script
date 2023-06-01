import json

def export_idw_results(date_time, df, rmse_list):
    json_output = df.to_dict(orient='index')
    json_output['power and rmse'] = dict(rmse_list)
    json_output['date_time'] = date_time
    outfile = json.dumps(json_output, indent=4)
    with open(f"./idw_results/idw_{str(date_time)}.json", "w") as f:
        f.write(outfile)

def export_routing_results(date_time, sensor, waypoint_coords, max_AQI, average_route_exposure, total_route_exposure, summary, area_diff=0, threshold=None):
    json_output = {
        'date_time': date_time,
        'sensor': {
            'sensor_name': sensor.name,
            'sensor_X': sensor.x,
            'sensor_y': sensor.y,
            'sensor_aqi': sensor.aqi,
        },
        'waypoints': waypoint_coords,
        'max AQI': max_AQI,
        'threshold': threshold,
        'average_route_exposure': average_route_exposure,
        'total_route_exposure': total_route_exposure,
        'excluded_area_ratio': area_diff,
        'summary': summary,
    }
    outfile = json.dumps(json_output, indent=4)
    with open(f"./route_results/route_results_{str(date_time)}_{str(threshold)}.json", "w") as f:
        f.write(outfile)
