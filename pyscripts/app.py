import fnmatch
import os
import zipfile
import cv2
import mysql.connector

from mysql.connector import errorcode
from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from werkzeug.utils import secure_filename, redirect
from PIL import Image

Image.MAX_IMAGE_PIXELS = None



###CONFIGURACIÓN DE FLASK Y USUARIO COPERNICUS

api = SentinelAPI('agarciabellan', '@Gar1983', 'https://apihub.copernicus.eu/apihub')

app=Flask(__name__,template_folder='../templates')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_JSON'] = '../archivos_geoJSON'



####OBTENER TABLA DE METADATOS DE MYSQL####

@app.route('/metadatos')
def metadatos():
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="@Gar1983", database="sentinel")
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM productos ')
    datos=cursor.fetchall()

    return render_template('tab_metadatos.html', productos=datos)




@app.route('/proyecto')
def proyecto():

    return render_template('proyecto.html')





###OBTENER TAMAÑO DEL ARCHIVO MIENTRAS SE ESTA DESCARGANDO
@app.route('/file_size', methods=['GET', 'OPTIONS'])
@cross_origin()
def file_size():
    suma = 0

    with open("suma.txt", "r") as file:
        suma = file.readline()

    cmd = 'ls -l ../fotos'
    stream = os.popen(cmd)
    output = stream.readlines()
    return suma + ":" + str(os.path.getsize('../fotos/' + output[-1].split()[-1]))


####OBTENER EL TAMAÑO TOTAL DEL PRODUCTO DESCARGADO MEDIANTE METADATOS
def get_max_size(products):
    suma = 0.0

    for key in products.keys():
        size = float(products[key]['size'].split(' ')[0])
        suma += size

    return suma * (1024 * 1024)



#DESCARGAR PRODUCTO
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

    suma = get_max_size(products)

    with open("suma.txt", "w") as file:
        file.write(str(suma))

        ####INSERTAR METADATOS A tabla productos

        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="@Gar1983",
                database="sentinel"
            )
            print("Conexion correcta con BBDD sentinel")
            for key in products.keys():
                sql = '''INSERT INTO productos(identifier, platformname, platformserialidentifier, processinglevel, orbitnumber, orbitdirection, ingestiondate, cloudcoverpercentage, instrumentname, size, footprint) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                params = (products[key]['identifier'], products[key]['platformname'], products[key]['platformserialidentifier'], products[key]['processinglevel'], products[key]['orbitnumber'], products[key]['orbitdirection'],products[key]['ingestiondate'], products[key]['cloudcoverpercentage'], products[key]['instrumentname'], products[key]['size'], products[key]['footprint'])
                cursor = mydb.cursor()
                cursor.execute(sql, params)
                mydb.commit()
                print("Se ha insertado un producto a la tabla productos")

        except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Acceso denegado, revisar user/password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("La BBDD no existe")
                else:
                    print(err)

        except Exception as err:
            print("\nFailed to insert row into table scr:\n" + str(sql))
            print(Exception, err)



    api.download_all(products, directory_path='../fotos')

   #DESCOMPRIMIR PRODUCTO PARA OBTENER IMAGENES JP2

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


    #####CONVERTIR IMAGEN _TCI(4,3,2) de JP2 a JPG

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


    #######ELIMINAR ARCHIVOS DEL SERVIDOR################
    ####BORRAR PRODUCTO .zip/.SAFE/.zip.incomplete
    cmd = 'rm -rf ../fotos/*.zip && rm -rf ../fotos/*.SAFE'
    stream = os.popen(cmd)
    output2 = stream.readlines()

    ####BORRAR archivos geoJSON
    cmd = 'rm -rf ../archivos_geoJSON/*.geojson'
    stream = os.popen(cmd)
    output3 = stream.readlines()

    ####BORRAR imagen.jpg

    cmd = 'rm -rf ../templates/imagen.jpg'
    stream = os.popen(cmd)
    output4 = stream.readlines()

    ####BORRAR contenido archivo suma.txt
    cmd = '> suma.txt'
    stream = os.popen(cmd)
    output5 = stream.readlines()

    ####CREAR ARCHIVO 0.zip
    cmd = 'touch ../fotos/0.zip'
    stream = os.popen(cmd)
    output2 = stream.readlines()


    return redirect('https://www.tfg-sentinel2.eu/')






