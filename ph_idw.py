from pyidw import idw
import numpy as np
from math import sqrt, floor, ceil
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.crs import CRS
from rasterio.transform import from_bounds
import fiona
from rasterio.enums import Resampling
from sklearn.metrics import r2_score
from sklearn.model_selection import LeaveOneOut
from matplotlib import colors

def get_idw(date_time):
    idw.idw_interpolation(
        input_point_shapefile="./shapefiles/Philippines_Pollution_"+date_time+".shp",
        # input_point_shapefile="./shapefiles/Philippines_Pollution.shp",
        extent_shapefile="./shapefiles/Philippines_Border.shp",
        column_name="US AQI",
        power=2,
        search_radious=15,
        output_resolution=250,
    )

def get_error(date_time):
    return idw.accuracy_standard_idw(
        input_point_shapefile="./shapefiles/Philippines_Pollution_"+date_time+".shp",
        # input_point_shapefile="./shapefiles/Philippines_Pollution.shp",
        extent_shapefile="./shapefiles/Philippines_Border.shp",
        column_name="US AQI",
        power=2,
        search_radious=15,
        output_resolution=250,
    )