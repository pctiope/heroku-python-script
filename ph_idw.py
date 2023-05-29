from pyidw import idw

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