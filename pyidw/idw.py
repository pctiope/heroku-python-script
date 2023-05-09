"""
Created on 31 Jan, 2021
Update on 02 Feb, 2022
@author: Md. Yahya Tamim
version: 0.2.14
"""

import numpy as np
from math import sqrt, floor, ceil
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.crs import CRS
from rasterio.transform import from_bounds
from rasterio.enums import Resampling


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


#################################################


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


#################################################


# def standard_idw(lon, lat, elev, longs, lats, elevs, d_values, id_power, p_degree, s_radious):
def standard_idw(lon, lat, longs, lats, d_values, id_power, s_radious):
    """regression_idw is responsible for mathmatic calculation of idw interpolation with regression as a covariable."""
    calc_arr = np.zeros(shape=( len(longs), 6))  # create an empty array shape of (total no. of observation * 6)
    calc_arr[:, 0] = longs  # First column will be Longitude of known data points.
    calc_arr[:, 1] = lats  # Second column will be Latitude of known data points.
    #     calc_arr[:, 2] = elevs    # Third column will be Elevation of known data points.
    calc_arr[:, 3] = d_values  # Fourth column will be Observed data value of known data points.

    # Fifth column is weight value from idw formula " w = 1 / (d(x, x_i)^power + 1)"
    # >> constant 1 is to prevent int divide by zero when distance is zero.
    calc_arr[:, 4] = 1 / (np.sqrt((calc_arr[:, 0] - lon)**2 + (calc_arr[:, 1] - lat)**2)**id_power + 1)

    # Sort the array in ascendin order based on column_5 (weight) "np.argsort(calc_arr[:,4])"
    # and exclude all the rows outside of search radious "[ - s_radious :, :]"
    calc_arr = calc_arr[np.argsort(calc_arr[:, 4])][-s_radious:, :]

    # Sixth column is multiplicative product of inverse distant weight and actual value.
    calc_arr[:, 5] = calc_arr[:, 3] * calc_arr[:, 4]
    # Divide sum of weighted value vy sum of weights to get IDW interpolation.
    idw = calc_arr[:, 5].sum() / calc_arr[:, 4].sum()
    return idw


#################################################


def idw_interpolation(input_point_shapefile='',
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
    #     baseRasterFile = rasterio.open(resized_raster_name) # baseRasterFile stands for resampled elevation.

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

        idw_array = baseRasterFile.read(1)
        for x in range(baseRasterFile.height):
            for y in range(baseRasterFile.width):
                if baseRasterFile.read(1)[x][y] == 32767:
                    continue
                else:
                    idw_array[x][y] = standard_idw(
                        lon=x,
                        lat=y,
                        longs=obser_df.lon_index,
                        lats=obser_df.lat_index,
                        d_values=obser_df.data_value,
                        id_power=power,
                        s_radious=search_radious)

        output_filename = input_point_shapefile.rsplit('.', 1)[0] + '_idw.tif'
        with rasterio.open(output_filename, 'w', **baseRasterFile.meta) as std_idw:
            std_idw.write(idw_array, 1)

        # show_map(output_filename)