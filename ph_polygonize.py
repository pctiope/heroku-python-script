import rasterio
import json
import base64
from rasterio.features import shapes
from github import Github

def polygonize():
    mask = None
    with rasterio.Env():
        with rasterio.open(f"./results/Philippines_Pollution_idw.tif") as src:
        # with rasterio.open(f"./shapefiles/Philippines_Pollution_{date_time}_idw.tif") as src:
            image = src.read(1) # first band
            image = image.astype('int16')
            geoms = [{'type':'Feature','properties': {'AQI': v}, 'geometry': s} for s,v in shapes(image, mask=mask, transform=src.transform) if v <= 1000]

    output_dict = {"type": "FeatureCollection", "name": "polygonized", "features": geoms}
    json_output = json.dumps(output_dict, indent=4)
    with open(f"./results/polygonized.json", "w") as outfile:
        outfile.write(json_output)
        
    coded_string = "Z2hwXzY3emJ2MGpUdkZRVjdJR201ZXpNSWQ1dU5tOWFHRzNiakp3Tg=="
    g = Github(base64.b64decode(coded_string).decode("utf-8"))
    repo = g.get_repo("pctiope/express-leaflet")
    contents = repo.get_contents(f"./public/polygonized.json", ref="main")
    repo.update_file(contents.path, "updated polygonized.json", json_output, contents.sha, branch="main")