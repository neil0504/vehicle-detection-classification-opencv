import random
import math
import time
import threading
# from vehicle_detection import detection
import pygame
# import pygame.font
import sys
import os
import vehicle_count
import cv2

defaultRed = 20
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 100

timeElapsed = 0
simTime = 120

signalCoods = [(530 / 2, 230)]
signalTimerCoods = [(530 / 2, 210)]

signals = []
currentGreen = 0  # Indicates which signal is green
currentYellow = 0  # Indicates whether yellow signal is on or off

pygame.init()
simulation = pygame.sprite.Group()

frame = None

detectionTime = 5

signalGreen = 0

carTime = 2
bikeTime = 1
rickshawTime = 2.25
busTime = 2.5
truckTime = 2.5

noOfLanes = 2


def simulationTime():
    global timeElapsed, simTime
    while True:
        timeElapsed += 1
        time.sleep(1)
        if timeElapsed == simTime:
            totalVehicles = 0
            # print('Lane-wise Vehicle Counts')
            # for i in range(noOfSignals):
            #     print('Lane', i + 1, ':', vehicles[directionNumbers[i]]['crossed'])
            #     totalVehicles += vehicles[directionNumbers[i]]['crossed']
            # print('Total vehicles passed: ', totalVehicles)
            # print('Total time passed: ', timeElapsed)
            # print('No. of vehicles passed per unit time: ', (float(totalVehicles) / float(timeElapsed)))
            print("Time's UP")
            os._exit(1)


def initialize():
    ts1 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    repeat()


def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws, noOfLanes
    global carTime, busTime, truckTime, rickshawTime, bikeTime
    # os.system("say detecting vehicles, " + directionNumbers[(currentGreen + 1) % noOfSignals])
    #    detection_result=detection(currentGreen,tfnet)
    #    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (noOfBuses*busTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
    #    if(greenTime<defaultMinimum):
    #       greenTime = defaultMinimum
    #    elif(greenTime>defaultMaximum):
    #       greenTime = defaultMaximum
    # greenTime = len(vehicles[currentGreen][0])+len(vehicles[currentGreen][1])+len(vehicles[currentGreen][2])
    # noOfVehicles = len(vehicles[directionNumbers[nextGreen]][1])+len(vehicles[directionNumbers[nextGreen]][2])-vehicles[directionNumbers[nextGreen]]['crossed']
    # print("no. of vehicles = ",noOfVehicles)
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0
    # for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
    #     vehicle = vehicles[directionNumbers[nextGreen]][0][j]
    #     if (vehicle.crossed == 0):
    #         vclass = vehicle.vehicleClass
    #         # print(vclass)
    #         noOfBikes += 1
    # for i in range(1, 3):
    #     for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
    #         vehicle = vehicles[directionNumbers[nextGreen]][i][j]
    #         if vehicle.crossed == 0:
    #             vclass = vehicle.vehicleClass
    #             # print(vclass)
    #             if vclass == 'car':
    #                 noOfCars += 1
    #             elif vclass == 'bus':
    #                 noOfBuses += 1
    #             elif vclass == 'truck':
    #                 noOfTrucks += 1
    #             elif vclass == 'rickshaw':
    #                 noOfRickshaws += 1
    # # print(noOfCars)

    noOfCars, noOfBikes, noOfBuses, noOfTrucks = vehicle_count.from_static_image(frame)
    noOfCars = int(noOfCars)
    noOfBikes = int(noOfBikes)
    noOfBuses = int(noOfBuses)
    noOfTrucks = int(noOfTrucks)
    greenTime = math.ceil(((noOfCars * carTime) + (noOfBuses * busTime) + (
            noOfTrucks * truckTime) + (noOfBikes * bikeTime)) / (noOfLanes + 1))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes)
    print('Green Time: ', greenTime)
    if greenTime < defaultMinimum:
        greenTime = defaultMinimum
    elif greenTime > defaultMaximum:
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[0].green = greenTime


def runVideo():
    global frame
    print(vehicle_count.cap)
    while True:
        _, frame = vehicle_count.cap.read()
        # cv2.imshow("image", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    vehicle_count.cap.release()
    cv2.destroyAllWindows()
    # vehicle_count.realTime()


def repeat():
    global currentGreen, currentYellow, nextGreen
    global signalGreen
    print("Inside: ", signals[0].red)
    while signals[0].red > 0:  # while the timer of current green signal is not zero
        # printStatus()
        updateValues()
        if signals[0].red == detectionTime:  # set time of next green signal
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            # setTime()
        time.sleep(1)
    signalGreen = 1
    # set yellow signal on
    # vehicleCountTexts[currentGreen] = "0"
    # reset stop coordinates of lanes and vehicles
    # for i in range(0, 3):
    #     stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
    #     for vehicle in vehicles[directionNumbers[currentGreen]][i]:
    #         vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while signalGreen and signals[0].green > 0:  # while the timer of current yellow signal is not zero
        # printStatus()
        updateValues()
        time.sleep(1)

    signals[0].red = defaultRed
    # currentYellow = 0  # set yellow signal off

    # reset all signal times of current signal to default times
    # signals[currentGreen].green = defaultGreen
    # signals[currentGreen].yellow = defaultYellow
    # signals[currentGreen].red = defaultRed
    #
    # currentGreen = nextGreen  # set next signal as green signal
    # # nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
    # signals[nextGreen].red = signals[currentGreen].yellow + signals[
    #     currentGreen].green  # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()


def updateValues():
    # for i in range(0, noOfSignals):
    i=0
    if i == currentGreen:
        if signals[i].red > 0:
            signals[i].red -= 1
            signalGreen = 0
        else:
            signals[i].green -= 1
            signals[i].totalGreenTime += 1
    # else:
    #     signals[i].red -= 1


class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0


class Main:
    global signalGreen
    thread_video = threading.Thread(name="ActualVideo", target=runVideo, args=())
    thread_video.daemon = True
    thread_video.start()

    thread4 = threading.Thread(name="simulationTime", target=simulationTime, args=())
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    thread2.daemon = True
    thread2.start()

    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 700
    screenHeight = 700
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/mod_int.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # screen.blit(background, (0, 0))
        i = 0
        if not signalGreen:
            if signals[i].red > 0:
                signals[i].signalText = signals[i].red
            else:
                signals[i].signalText = "STOP"
            screen.blit(redSignal, signalCoods[i])
        else:
            if signals[i].green > 0:
                signals[i].signalText = signals[i].green
            else:
                signals[i].signalText = "GO"
            screen.blit(greenSignal, signalCoods[i])
        # if i == currentGreen:
        #     if currentYellow == 1:
        #         if signals[i].yellow == 0:
        #             signals[i].signalText = "STOP"
        #         else:
        #             signals[i].signalText = signals[i].yellow
        #         screen.blit(yellowSignal, signalCoods[i])
        #     else:
        #         if signals[i].green == 0:
        #             signals[i].signalText = "SLOW"
        #         else:
        #             signals[i].signalText = signals[i].green
        #         screen.blit(greenSignal, signalCoods[i])
        # else:
        #     if signals[i].red <= 10:
        #         if signals[i].red == 0:
        #             signals[i].signalText = "GO"
        #         else:
        #             signals[i].signalText = signals[i].red
        #     else:
        #         signals[i].signalText = "---"
        #     screen.blit(redSignal, signalCoods[i])
        signalTexts = [""]

        signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
        screen.blit(signalTexts[i], signalTimerCoods[i])

        timeElapsedText = font.render(("Time Elapsed: " + str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, (900 / 2, 50))

        pygame.display.update()


Main()
