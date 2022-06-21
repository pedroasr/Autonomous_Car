import os
import cv2
import numpy as np
import re

indice_x = 0
indice_y = 0

dir = 'D:/imagenes_prueba3'

path, dirs, files = next(os.walk(dir))
file_count = len(files)

with os.scandir(dir) as imagenes:
    valores = np.empty((file_count, 24 * 18 + 2))

    for imagen in imagenes:
        valoresSalida = [float(s) for s in re.findall(r'-?\d+\.?\d*', imagen.name)]
        img = cv2.imread(dir + '/' + imagen.name)
        contrast_img = cv2.addWeighted(img, 2.3, np.zeros(img.shape, img.dtype), 0, 0)
        gray_img = cv2.cvtColor(contrast_img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY_INV)
        imagen_re = cv2.resize(thresh1, (24, 18))
        final_img = imagen_re / 255
        valores[indice_x, indice_y] = valoresSalida[7]
        valores[indice_x, indice_y + 1] = valoresSalida[9]
        for i in range(final_img.shape[0]):
            for j in range(final_img.shape[1]):
                valores[indice_x, indice_y + 2] = final_img[i, j]
                indice_y = indice_y + 1
        indice_x = indice_x + 1
        indice_y = 0

    valores = np.round(valores, 3)

np.savetxt('data.csv', valores, delimiter=',')
