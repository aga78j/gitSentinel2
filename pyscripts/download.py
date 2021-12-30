from flask import Flask, request
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
api = SentinelAPI('agarciabellan', '@Gar1983', 'https://apihub.copernicus.eu/apihub')

app = Flask(__name__)

@app.route("/", methods=["GET"])
def main():
    pass

@app.route('/download', methods=['POST'])
def download():
    file = request.files.get("geoJSON")

    if file.filename != "":
        file.save("C:/Users/agarc/Desktop/TFG/gitSentinel2/archivos_geoJSON/json.geojson")

    footprint = geojson_to_wkt(read_geojson("C:/Users/agarc/Desktop/TFG/gitSentinel2/archivos_geoJSON/json.geojson"))
    products = api.query(footprint,
                     date=(request.form.get('date_init').replace('-', ''), request.form.get('date_end').replace('-', '')),
                     platformname=request.form.get('platform'),
                     producttype = request.form.get('product'),
                     cloudcoverpercentage=(0, int(request.form.get("cloud"))))
                     
    #print(request.form.get('date_init').replace('-', ''), request.form.get('date_end').replace('-', ''), request.form.get('platform'), request.form.get('product'))
    api.download_all(products, directory_path='C:/Users/agarc/Desktop/TFG/gitSentinel2/fotos')
    return "terminado"

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="@Gar1983"
)

print(mydb)