import os
import cv2


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
