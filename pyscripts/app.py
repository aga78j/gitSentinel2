from flask import Flask, request
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
api = SentinelAPI('agarciabellan', '@Gar1983', 'https://apihub.copernicus.eu/apihub')

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    footprint = geojson_to_wkt(read_geojson('C:/Users/agarc/Desktop/TFG/gitSentinel2/archivos_geoJSON/murcia.geojson'))
    products = api.query(footprint,
                     date=(request.form.get('date_init').replace('-', ''), request.form.get('date_end').replace('-', '')),
                     platformname=request.form.get('platform'),
                     producttype = request.form.get('product'), #S2MSI1C
                     cloudcoverpercentage=(0, 30))
    api.download_all_quicklooks(products, directory_path='C:/Users/agarc/Desktop/TFG/gitSentinel2/fotos')
    return "terminado"