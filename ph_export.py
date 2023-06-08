import json

def export_idw_results(date_time, df, rmse_list):
    json_output = df.to_dict(orient='index')
    json_output['power and rmse'] = dict(rmse_list)
    json_output['date_time'] = date_time
    outfile = json.dumps(json_output, indent=4)
    with open(f"./results/{date_time}/aqi_idw_results.json", "w") as f:
        f.write(outfile)

def export_routing_results(date_time, routing_results, mode, run):
    outfile = json.dumps(routing_results, indent=4)
    with open(f"./results/{date_time}/{mode}/{run}/route_results.json", "w") as f:
        f.write(outfile)
