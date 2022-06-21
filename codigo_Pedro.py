import RPi.GPIO as GPIO
import numpy as np
from tensorflow.keras.models import load_model
import cv2

# Cargamos el modelo y los pesos de la red
modelo = 'modelo_0.05779_total.h5'
pesos = 'pesos_0.05779_total.h5'

red = load_model(modelo)
red.load_weights(pesos)

alpha = 0.75

# Necesito 4 pines de salida.
# Dos PWM para la velocidad de los motores

directionRight = 31  # Conectar a D4
speedRight = 33  # PWM pin connected Right motor #Conectar a M1 -> D5
speedLeft = 35  # PWM pin connected Left motor #Conectar a M2 -> D6
directionLeft = 37  # Conectar a D7

GPIO.setwarnings(False)  # disable warnings
GPIO.setmode(GPIO.BOARD)  # set pin numbering system # Referencia a la posición física.

GPIO.setup(directionLeft, GPIO.OUT)
GPIO.setup(directionRight, GPIO.OUT)

GPIO.setup(speedLeft, GPIO.OUT)
pwmLeft = GPIO.PWM(speedLeft,
                   100)  # create PWM instance with frequency #En el código de ejemplo usa 1000, pero no me va bien. Uso 100.
pwmLeft.start(0)  # start PWM of required Duty Cycle

GPIO.setup(speedRight, GPIO.OUT)
pwmRight = GPIO.PWM(speedRight, 100)  # create PWM instance with frequency
pwmRight.start(0)  # start PWM of required Duty Cycle

cam = cv2.VideoCapture(0)

memoria = np.zeros((1, 2))

while (True):
    ret, img = cam.read()
    indice = 0
    valores = np.empty((1, 24 * 18))
    contrast_img = cv2.addWeighted(img, 2.3, np.zeros(img.shape, img.dtype), 0, 0)
    gray_img = cv2.cvtColor(contrast_img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY_INV)
    resize_img = cv2.resize(thresh, (24, 18))
    final_img = resize_img / 255

    for i in range(final_img.shape[0]):
        for j in range(final_img.shape[1]):
            valores[0, indice] = final_img[i, j]
            indice = indice + 1

    output = red.predict(valores)
    Eje_izq = alpha * output[0, 0] + (1 - alpha) * memoria[0, 0]
    Eje_dch = alpha * output[0, 1] + (1 - alpha) * memoria[0, 1]
    memoria[0, 0] = output[0, 0]
    memoria[0, 1] = output[0, 1]

    if Eje_izq < 0:
        GPIO.output(directionLeft, True)
    else:
        GPIO.output(directionLeft, False)

    if Eje_dch < 0:
        GPIO.output(directionRight, True)
    else:
        GPIO.output(directionRight, False)

    pot = 50  # JK pot = 100 va a toda velocidad.
    pwmRight.ChangeDutyCycle(int(abs(Eje_dch) * pot))
    pwmLeft.ChangeDutyCycle(int(abs(Eje_izq) * pot))

cam.release()
