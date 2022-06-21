# ControlPS3
# https://theraspberryblonde.wordpress.com/2016/06/29/ps3-joystick-control-with-pygame/


import pygame, sys

# PWM y GPIO control vehículo
# https://www.electronicwings.com/raspberry-pi/raspberry-pi-pwm-generation-using-python-and-c

import RPi.GPIO as GPIO

import cv2

import time
from datetime import datetime
from datetime import date
from time import sleep

import os

os.environ["DISPLAY"] = ":0"

# Necesito 4 pines de salida.
# Dos PWM para la velocidad de los motores
# y otros dos L/H para el sentido de rotación de los motores.

directionRight = 31  # Conectar a D4
speedRight = 33  # PWM pin connected Right motor #Conectar a M1 -> D5
speedLeft = 35  # PWM pin connected Left motor #Conectar a M2 -> D6
directionLeft = 37  # Conectar a D7

fotoLed = 16  # para indicar que está tomando fotos.

GPIO.setwarnings(False)  # disable warnings
GPIO.setmode(GPIO.BOARD)  # set pin numbering system # Referencia a la posición física.

GPIO.setup(fotoLed, GPIO.OUT)
GPIO.output(fotoLed, False)

GPIO.setup(directionLeft, GPIO.OUT)
GPIO.setup(directionRight, GPIO.OUT)

GPIO.setup(speedLeft, GPIO.OUT)
pwmLeft = GPIO.PWM(speedLeft,
                   100)  # create PWM instance with frequency #En el código de ejemplo usa 1000, pero no me va bien. Uso 100.
pwmLeft.start(0)  # start PWM of required Duty Cycle

GPIO.setup(speedRight, GPIO.OUT)
pwmRight = GPIO.PWM(speedRight, 100)  # create PWM instance with frequency
pwmRight.start(0)  # start PWM of required Duty Cycle

botonFoto = False

# setup the pygame window
pygame.init()
# window = pygame.display.set_mode((200, 200), 0, 32)

# how many joysticks connected to computer?
joystick_count = pygame.joystick.get_count()
print("There is " + str(joystick_count) + " joystick/s")

countFailures = 5

while (1):
    if joystick_count == 0:
        countFailures = countFailures - 1
        if countFailures == 0:
            # if no joysticks, quit program safely
            print("Error, I did not find any joysticks")
            pygame.quit()
            sys.exit()
        sleep(5)

    else:
        # initialise joystick
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        break

axes = joystick.get_numaxes()
buttons = joystick.get_numbuttons()
hats = joystick.get_numhats()

print("There is " + str(axes) + " axes")
print("There is " + str(buttons) + " button/s")
print("There is " + str(hats) + " hat/s")


def getAxis(eje1, eje4):  # aquí es dónde proceso lo que hago con los mandos.

    # when nothing is moved on an axis, the VALUE IS NOT EXACTLY ZERO
    # so this is used not "if joystick value not zero"
    valorEje1 = joystick.get_axis(eje1)
    valorEje4 = joystick.get_axis(eje4)
    if valorEje1 < -0.1 or valorEje1 > 0.1:
        # value between 1.0 and -1.0
        print("\tAxis 1 (VerticalIzda) value is %s" % (valorEje1))
    else:
        valorEje1 = 0

    if valorEje4 < -0.1 or valorEje4 > 0.1:
        print("\tAxis 4 (verticalDcha)value is %s" % (valorEje4))
    else:
        valorEje4 = 0

    # Me interesa los ejes 1 (hat izda) y 4(hat dcha)
    # tengo que transformar los valores -1 -> +1 a PWM (0 -> 100)
    # y el valor positivo/negativo en dirección F/B

    if valorEje1 < 0:
        GPIO.output(directionLeft, True)
    else:
        GPIO.output(directionLeft, False)

    if valorEje4 < 0:
        GPIO.output(directionRight, True)
    else:
        GPIO.output(directionRight, False)

    pot = 50  # JK pot = 100 va a toda velocidad.
    pwmRight.ChangeDutyCycle(int(abs(valorEje4) * pot))
    pwmLeft.ChangeDutyCycle(int(abs(valorEje1) * pot))


def getButton(number):
    # returns 1 or 0 – pressed or not

    if ((number == 14) & joystick.get_button(number)):
        # just prints id of button
        print("Se ha activado la cámara, botón presionado abajo %s" % (number))
        GPIO.output(fotoLed, True)
        return True

    if ((number == 13) & joystick.get_button(number)):
        # just prints id of button
        print("Se ha DesActivado la cámara, botón presionado abajo %s" % (number))
        GPIO.output(fotoLed, False)
        return False


def getHat(number):
    if joystick.get_hat(number) != (0, 0):
        # returns tuple with values either 1, 0 or -1
        print("Hat value is %s, %s" % (joystick.get_hat(number)[0], joystick.get_hat(number)[1]))
        print("Hat ID is %s" % (number))


# Continuación dl código principal.
# Creo la cámara.
cam = cv2.VideoCapture(0)

while True:
    for event in pygame.event.get():
        # loop through events, if window shut down, quit program
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if axes != 0:
        # for i in range(axes): #recojo los valores de cada eje.  Sólo me interesan el 1 y el 4
        getAxis(1, 4)

    #  if buttons != 0:
    #    for i in range(buttons):
    #      if getButton(i) == True:
    #          print ("botonFoto = true")
    #      else:
    #          print("BF = False")

    if joystick.get_button(15):
        # MEJOR QUE CON EL número, con el esto otro.
        # if event.type == pygame.JOYBUTTONDOWN:
        # just prints id of button
        print("Se ha activado la cámara, botón presionado boton abajo ")
        GPIO.output(fotoLed, True)
        botonFoto = True
    # if event.type == pygame.JOYBUTTONUP:
    if joystick.get_button(14):
        # just prints id of button
        print("Se ha DesActivado la cámara, botón presionado arriba")
        GPIO.output(fotoLed, False)
        # botonFoto = False
        botonFoto = True

    # if hats != 0:
    # for i in range(hats):
    #  getHat(i)

    # tomo la imagen y la guardo
    ret, image = cam.read()

    if (ret & (botonFoto == True)):
        print("Tomando Foto")
        cv2.imshow('Snapshot', image)
        # cv2.waitKey(0)
        cv2.destroyWindow('Snapshot')
        # today = date.today()
        valorEje1 = joystick.get_axis(1)
        valorEje4 = joystick.get_axis(4)
        now = datetime.now()
        nombreArchivo = "./imagenes/imagen_" + str(now) + "_EjeIzda1_" + str(valorEje1) + "_EjeDcha4_" + str(
            valorEje4) + ".jpg"
        # nombreArchivo = "imagen_" + str(today) + "_" + str(now.hour) + "_" + str(now.minute) + "_" +format(now.second) + ".jpg"
        cv2.imwrite(nombreArchivo, image)

    sleep(0.1)

# Libero la cámara cuando termina el código
cam.release()
