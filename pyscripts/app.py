import fnmatch
import os
import zipfile
import cv2

from flask import Flask, request
from flask_cors import CORS, cross_origin
from matplotlib import pyplot as plot
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from werkzeug.utils import secure_filename, redirect
from PIL import Image



#DESCARGAR PRODUCTO

api = SentinelAPI('agarciabellan', '@Gar1983', 'https://apihub.copernicus.eu/apihub')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_JSON'] = '../archivos_geoJSON'


@app.route('/file_size', methods=['GET', 'OPTIONS'])
@cross_origin()
def file_size():
    cmd = 'ls -l ../fotos'
    stream = os.popen(cmd)
    output = stream.readlines()
    return str(os.path.getsize('../fotos/' + output[-1].split()[-1]))



def get_max_size(products):
    suma = 0.0

    for key in products.keys():
        size = float(products[key]['size'].split(' ')[0])
        suma += size

    return suma

@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        file = request.files['geoJSON']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_JSON'], filename))
    footprint = geojson_to_wkt(read_geojson("../archivos_geoJSON/" + filename))
    products = api.query(footprint,
                         date=(
                             request.form.get('date_init').replace('-', ''),
                             request.form.get('date_end').replace('-', '')),
                         platformname=request.form.get('platform'),
                         producttype=request.form.get('product'),
                         cloudcoverpercentage=(0, int(request.form.get("cloud"))),
                         limit=1)


    api.download_all(products, directory_path='../fotos')

   #DESCOMPRIMIR PRODUCTO

    cmd = 'ls -l ../fotos'
    stream = os.popen(cmd)
    output = stream.readlines()

    ruta_zip = "../fotos/" + output[-1].split()[-1]
    ruta_extraccion = "../fotos/"
    password = None
    archivo_zip = zipfile.ZipFile(ruta_zip, "r")
    try:
        for file in archivo_zip.namelist():
            if fnmatch.fnmatch(file, "*.jp2"):
                print(file)
                archivo_zip.extract(file, pwd=password, path=ruta_extraccion)

    except:
        pass

    archivo_zip.close()

    def get_tci_file(path):
        for root, subdir, files in os.walk(path):
            for file in files:
                if "TCI" in file:
                    return os.path.join(root, file)

    def tci_to_jpg(path):
        tci_file = get_tci_file(path)
        if tci_file:
            imagen = cv2.imread(tci_file)
            cv2.imwrite("../templates/imagen.jpg", imagen)
        else:
            print("No se ha encontrado ningún fichero TCI en " + path)

    tci_to_jpg("../fotos")

    ###RESIZE IMAGEN 512x512 JPG-PNG
    img = Image.open('../templates/imagen.jpg')
    new_img = img.resize((512, 512))
    new_img.save('../templates/imagen_resize.png', 'png')

####BORRAR PRODUCTO .zip/.SAFE/.zip.incomplete

    cmd = 'rm -rf ../fotos/*.zip && rm -rf ../fotos/*.SAFE'
    stream = os.popen(cmd)
    output2 = stream.readlines()

####BORRAR archivos geoJSON
    cmd = 'rm -rf ../archivos_geoJSON/*.geojson'
    stream = os.popen(cmd)
    output2 = stream.readlines()


    return redirect('https://www.tfg-sentinel2.eu/')






