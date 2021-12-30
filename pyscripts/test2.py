    
# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

api = SentinelAPI('agarciabellan', '@Gar1983', 'https://apihub.copernicus.eu/apihub')


# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('archivos_geoJSON/murcia.geojson'))
products = api.query(footprint,
                     date=('20211209', '20211224'),
                     platformname='Sentinel-2',
                     producttype = 'S2MSI1C',
                     cloudcoverpercentage=(0, 30))

# download all results from the search
#api.download_all(products, directory_path='C:/Users/agarc/Desktop/TFG/gitSentinel2/fotos')
api.download_all_quicklooks(products)

# convert to Pandas DataFrame
#products_df = api.to_dataframe(products)

#print(products_df.to_string(index=False))

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
#api.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
#api.to_geodataframe(products)