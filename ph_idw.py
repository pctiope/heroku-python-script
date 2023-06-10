from pyidw import idw

def get_idw(power):
    idw.idw_interpolation(
        input_point_shapefile="./results/Philippines_Pollution.shp",
        # input_point_shapefile="./shapefiles/Philippines_Pollution_"+date_time+".shp",
        extent_shapefile="./shapefiles/Philippines_Border.shp",
        column_name="US AQI",
        power=power,
        search_radious=15,
        output_resolution=250,
    )

# def get_error(date_time, power):
#     return idw.accuracy_standard_idw(
#         input_point_shapefile=f"./results/{date_time}/Philippines_Pollution.shp",
#         # input_point_shapefile="./shapefiles/Philippines_Pollution_"+date_time+".shp",
#         extent_shapefile="./shapefiles/Philippines_Border.shp",
#         column_name="US AQI",
#         power=power,
#         search_radious=15,
#         output_resolution=250,
#     )