import json

def export_initial(date_time, df, rmse_list):
    json_output = df.to_json(orient='index')
    json_output.append({"type": dict(rmse_list)})
    json_output = json.dumps(json_output, indent=4)
    with open("./initial/initial_"+str(date_time)+".json","w") as f:
        f.write(json_output)