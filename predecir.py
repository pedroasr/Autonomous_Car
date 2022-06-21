import numpy as np
import cv2
from tensorflow.keras.models import load_model
import re

modelo = './modelo/modelo_0.02947_total.h5'
pesos = './modelo/pesos_0.02947_total.h5'
red = load_model(modelo)
red.load_weights(pesos)


def predict(file):
    indice = 0
    img = cv2.imread(file)
    valoresSalida = [float(s) for s in re.findall(r'-?\d+\.?\d*', file)]
    valores = np.empty((1, 24 * 18))
    contrast_img = cv2.addWeighted(img, 2.3, np.zeros(img.shape, img.dtype), 0, 0)
    gray_img = cv2.cvtColor(contrast_img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY_INV)
    imagen_re = cv2.resize(thresh1, (24, 18))
    final_img = imagen_re / 255
    for i in range(final_img.shape[0]):
        for j in range(final_img.shape[1]):
            valores[0, indice] = final_img[int(i), int(j)]
            indice = indice + 1

    respuesta = red.predict(valores)
    print('Eje izquierdo real: ', valoresSalida[7], ', Eje derecho real: ', valoresSalida[9])
    print('Eje izquierdo predicho: ', respuesta[0, 0], ', Eje derecho predicho: ', respuesta[0, 1])

    return respuesta


predict('imagenes_prueba/imagen_2021-02-16 14_47_53.876264_EjeIzda1_-1.0_EjeDcha4_-1.0.jpg')
