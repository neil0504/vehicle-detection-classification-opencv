import math
import os
import sys
import threading
import time
import cv2
import pygame
# from gtts import gTTS

from win32com.client import Dispatch

import vehicle_count

defaultRed = 10
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 80

timeElapsed = 0
simTime = 200

signalCoods = [(165, 170)]
signalTimerCoods = [(165, 150)]

signals = []
currentGreen = 0

pygame.init()
simulation = pygame.sprite.Group()

frame = None

detectionTime = 5

signalGreen = 0

carTime = 3.25
bikeTime = 2.25
busTime = 4.25
truckTime = 4.25

noOfCars = 0
noOfBikes = 0
noOfBuses = 0
noOfTrucks = 0
noOfLanes = 2

video_counter = 0
cap = None

total_vehicles = 0

# tts = gTTS(text="Detecting Vehicles", lang='en')
# tts.save("pcvoice.mp3")

speak = Dispatch("SAPI.SpVoice").Speak


def simulationTime():
    global timeElapsed, simTime
    while True:

        time.sleep(1)
        timeElapsed += 1
        if timeElapsed == simTime:
            print("Time's UP")
            os._exit(1)


def initialize():
    ts1 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    repeat()


def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfLanes
    global carTime, busTime, truckTime, bikeTime
    global total_vehicles
    # os.system("start pcvoice.mp3")
    speak("Detecting Vehicles")
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0

    noOfCars, noOfBikes, noOfBuses, noOfTrucks = vehicle_count.from_static_image(frame)

    noOfCars, noOfBikes, noOfBuses, noOfTrucks = int(noOfCars), int(noOfBikes), int(noOfBuses), int(noOfTrucks)

    total_vehicles += (noOfCars + noOfBikes + noOfBuses + noOfTrucks)

    greenTime = math.ceil(((noOfCars * carTime) + (noOfBuses * busTime) + (
            noOfTrucks * truckTime) + (noOfBikes * bikeTime)) / (noOfLanes + 2))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes)
    print('Green Time: ', greenTime)
    if greenTime < defaultMinimum:
        greenTime = defaultMinimum
    elif greenTime > defaultMaximum:
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[0].green = greenTime
    speak(f"{noOfCars} cars, {noOfBikes} motorbikes, {noOfBuses} buses and {noOfTrucks} trucks detected")
    speak(f"Green time is {greenTime} seconds")


def runVideo():
    global frame, cap
    print(cap)
    # cap = cv2.VideoCapture('F:\\Videos and Pics\\VID_20211001_072900.mp4')
    while True:
        _, frame = cap.read()
        img = cv2.resize(frame, (0, 0), None, fx=0.5, fy=0.5)
        cv2.imshow("image", img)
        if cv2.waitKey(1) == ord('q'):
            break

    vehicle_count.cap.release()
    cv2.destroyAllWindows()
    # vehicle_count.realTime()


def repeat():
    global currentGreen
    global signalGreen
    print("Inside: ", signals[0].red)
    while signals[0].red > 0:
        # printStatus()

        if signals[0].red == detectionTime:  # set time of next green signal
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            # setTime()
        time.sleep(1)
        updateValues()
    signalGreen = 1

    while signalGreen and signals[0].green > 0:
        # printStatus()

        time.sleep(1)
        updateValues()

    signals[0].red = defaultRed

    thread_choose_video_1 = threading.Thread(name="Choose Video", target=chooseVideo, args=())
    thread_choose_video_1.daemon = True
    thread_choose_video_1.start()

    repeat()


def updateValues():
    global signalGreen
    i = 0
    if i == currentGreen:
        if signals[i].red > 0:
            signals[i].red -= 1
            signalGreen = 0
        else:
            signals[i].green -= 1
            signals[i].totalGreenTime += 1
            signalGreen = 1


def chooseVideo():
    global video_counter, cap
    video_counter += 1
    cap = cv2.VideoCapture("Program Samples\\sample_{}.mp4".format(video_counter))
    print("Video = sample_{}".format(video_counter))


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

    thread_choose_video = threading.Thread(name="Choose Video", target=chooseVideo, args=())
    thread_choose_video.start()
    thread_choose_video.join()

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
    screenWidth = 400
    screenHeight = 400
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('background.jpg')

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

        screen.blit(background, (0, 0))
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

        signalTexts = [""]

        signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
        screen.blit(signalTexts[i], signalTimerCoods[i])

        timeElapsedText = font.render(("Time Elapsed: " + str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, (200, 50))

        pygame.display.update()


Main()
