import rasterio
import json
from rasterio.features import shapes

def polygonize(date_time):
    mask = None
    with rasterio.Env():
        with rasterio.open("./results/"+date_time+"/Philippines_Pollution_idw.tif") as src:
        # with rasterio.open(f"./shapefiles/Philippines_Pollution_{date_time}_idw.tif") as src:
            image = src.read(1) # first band
            image = image.astype('int16')
            geoms = [{'type':'Feature','properties': {'AQI': v}, 'geometry': s} for s,v in shapes(image, mask=mask, transform=src.transform) if v <= 1000]
    
    output_dict = {"type": "FeatureCollection", "name": "polygonized", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": geoms}
    json_output = json.dumps(output_dict, indent=4)
    with open(f"./results/{date_time}/polygonized.json", "w") as outfile:
        outfile.write(json_output)