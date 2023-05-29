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
    idw.accuracy_standard_idw(
        input_point_shapefile="./shapefiles/Philippines_Pollution_"+date_time+".shp",
        # input_point_shapefile="./shapefiles/Philippines_Pollution.shp",
        extent_shapefile="./shapefiles/Philippines_Border.shp",
        column_name="US AQI",
        power=2,
        search_radious=15,
        output_resolution=250,
    )

def blank_raster(extent_shapefile=''):
    calculationExtent = gpd.read_file(extent_shapefile)

    minX = floor(calculationExtent.bounds.minx)
    minY = floor(calculationExtent.bounds.miny)
    maxX = ceil(calculationExtent.bounds.maxx)
    maxY = ceil(calculationExtent.bounds.maxy)
    longRange = sqrt((minX - maxX)**2)
    latRange = sqrt((minY - maxY)**2)

    gridWidth = 400
    pixelPD = (gridWidth / longRange)  # Pixel Per Degree
    gridHeight = floor(pixelPD * latRange)
    BlankGrid = np.ones([gridHeight, gridWidth])

    blank_filename = extent_shapefile.rsplit('.', 1)[0] + '_blank.tif'

    with rasterio.open(
            blank_filename,
            "w",
            driver='GTiff',
            height=BlankGrid.shape[0],
            width=BlankGrid.shape[1],
            count=1,
            dtype=BlankGrid.dtype,  #BlankGrid.dtype, np.float32, np.int16
            crs=CRS.from_string(calculationExtent.crs.srs),
            transform=from_bounds(minX, minY, maxX, maxY, BlankGrid.shape[1], BlankGrid.shape[0]),
            nodata=32767) as dst:
        dst.write(BlankGrid, 1)    

def crop_resize(input_raster_filename='',
                extent_shapefile_name='',
                max_height_or_width=250):
    # Here, co-variable raster file (elevation in this case) is croped and resized using rasterio.
    BD = gpd.read_file(extent_shapefile_name)
    elevation = rasterio.open(input_raster_filename)

    # Using mask method from rasterio.mask to clip study area from larger elevation file.
    croped_data, croped_transform = mask(dataset=elevation,
                                         shapes=BD.geometry,
                                         crop=True,
                                         all_touched=True)
    croped_meta = elevation.meta
    croped_meta.update({
        'height': croped_data.shape[-2],
        'width': croped_data.shape[-1],
        'transform': croped_transform
    })

    croped_filename = input_raster_filename.rsplit('.', 1)[0] + '_croped.tif'
    with rasterio.open(croped_filename, 'w', **croped_meta) as croped_file:
        croped_file.write(croped_data)  # Save the croped file as croped_elevation.tif to working directory.

    # Calculate resampling factor for resizing the elevation file, this is done to reduce calculation time.
    # Here 250 is choosed for optimal result, it can be more or less depending on users desire.
    # max_height_or_width = 250
    resampling_factor = max_height_or_width / max(rasterio.open(croped_filename).shape)

    # Reshape/resize the croped elevation file and save it to working directory.
    with rasterio.open(croped_filename, 'r') as croped_elevation:

        resampled_elevation = croped_elevation.read(
            out_shape=(croped_elevation.count,
                       int(croped_elevation.height * resampling_factor),
                       int(croped_elevation.width * resampling_factor)),
            resampling=Resampling.bilinear)

        resampled_transform = croped_elevation.transform * croped_elevation.transform.scale(
            croped_elevation.width / resampled_elevation.shape[-1],
            croped_elevation.height / resampled_elevation.shape[-2])

        resampled_meta = croped_elevation.meta
        resampled_meta.update({
            'height': resampled_elevation.shape[-2],
            'width': resampled_elevation.shape[-1],
            'dtype': np.float64,
            'transform': resampled_transform
        })

        resampled_filename = input_raster_filename.rsplit(
            '.', 1)[0] + '_resized.tif'
        with rasterio.open(resampled_filename, 'w', **resampled_meta) as resampled_file:
            resampled_file.write(resampled_elevation )  # Save the resized file as resampled_elevation.tif in working directory.
    
def accuracy_standard_idw(input_point_shapefile='',
                          extent_shapefile='',
                          column_name='',
                          power=2,
                          search_radious=4,
                          output_resolution=250):
    blank_raster(extent_shapefile)
    
    blank_filename = extent_shapefile.rsplit('.', 1)[0] + '_blank.tif'
    crop_resize(input_raster_filename=blank_filename,
                extent_shapefile_name=extent_shapefile,
                max_height_or_width=output_resolution)
    
    resized_raster_name = blank_filename.rsplit('.', 1)[0] + '_resized.tif'

    with rasterio.open(resized_raster_name) as baseRasterFile:
        inputPoints = gpd.read_file(input_point_shapefile)
        # obser_df stands for observation_dataframe, lat, lon, data_value for each station will be stored here.
        obser_df = pd.DataFrame()
        obser_df['station_name'] = inputPoints.iloc[:, 0]

        # create two list of indexes of station longitude, latitude in elevation raster file.
        lons, lats = baseRasterFile.index(
            [lon for lon in inputPoints.geometry.x],
            [lat for lat in inputPoints.geometry.y])
        obser_df['lon_index'] = lons
        obser_df['lat_index'] = lats
        obser_df['data_value'] = inputPoints[column_name]
        obser_df['predicted'] = 0.0

        cv = LeaveOneOut()
        for train_ix, test_ix in cv.split(obser_df):
            test_point = obser_df.iloc[test_ix[0]]
            train_df = obser_df.iloc[train_ix]

            obser_df.loc[test_ix[0], 'predicted'] = standard_idw(
                lon=test_point.lon_index,
                lat=test_point.lon_index,
                longs=train_df.lon_index,
                lats=train_df.lat_index,
                d_values=train_df.data_value,
                id_power=power,
                s_radious=search_radious)
        return obser_df.data_value.to_list(), obser_df.predicted.to_list()