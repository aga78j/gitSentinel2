import fnmatch
import os
import zipfile
import rasterio
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

    # CONVERTIR JP2-PNG IMAGEN

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


    return redirect('https://www.tfg-sentinel2.eu/')




@app.route('/show', methods=['GET'])
def show():
    R10 = '../fotos/S2A_MSIL2A_20211201T105421_N0301_R051_T30SXG_20211201T153252.SAFE/GRANULE/L2A_T30SXG_A033653_20211201T105655/IMG_DATA/R10m'

    b4 = rasterio.open(R10 + '/T30SXG_20211201T105421_B04_10m.jp2', driver='JP2OpenJPEG')
    b3 = rasterio.open(R10 + '/T30SXG_20211201T105421_B03_10m.jp2', driver='JP2OpenJPEG')
    b2 = rasterio.open(R10 + '/T30SXG_20211201T105421_B02_10m.jp2', driver='JP2OpenJPEG')

    with rasterio.open('RGB3.tiff', 'w', driver='Gtiff', width=b4.width, height=b4.height, count=3, crs=b4.crs,
                       transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
        rgb.write(b4.read(1), 3)
        rgb.write(b3.read(1), 2)
        rgb.write(b2.read(1), 1)
        plot.show(rgb)


    return"terminado"


