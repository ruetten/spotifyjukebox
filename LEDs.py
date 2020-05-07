import board
import neopixel
import time
from math import floor

num_pixels = 300
pixels = neopixel.NeoPixel(board.D18, num_pixels)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)

def rainbow_cycle(wait):
    print("rainbow time")
    for j in list(range(255)):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j*100
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

b = 0.4
red = floor(255*b)
blue = 0
green = 0
increasingRed = False
increasingBlue = True
increasingGreen = False
lingerAtRed = False
decreasingRed = True
decreasingBlue = False
decreasingGreen = False
sleepAmount = .5
while True:
    print(str(red) + " " + str(green) + " " + str(blue))
    pixels.fill((red, green, blue))
    pixels.show()
    time.sleep(sleepAmount)
    if increasingRed:
        if red != floor(255*b):   
            red = red + 1
    elif decreasingRed:
        if red != 0:
            red = red - 1
            
    if increasingBlue:
        blue = blue + 1
        if blue == floor(165*b):
            decreasingRed = False
            increasingRed = True
            increasingBlue = False
            decreasingBlue = True
    elif decreasingBlue:
        blue = blue - 1
        if blue == 0:
            increasingRed = False
            decreasingBlue = False
            increasingGreen = True
            
    if increasingGreen:
        green = green + 1
        if green == floor(165*b):
            decreasingRed = False
            increasingRed = True
            increasingGreen = False
            decreasingGreen = True
    elif decreasingGreen:
        green = green - 1
        if green == 0:
            lingerAtRed = True
            
    if lingerAtRed:
        time.sleep(sleepAmount*165)
        lingerAtRed = False
        decreasingRed = True
        increasingRed = False
        decreasingGreen = False
        increasingBlue = True
            
#     if increasingRed:
#         red = red + 1
#         if red == 255:
#             increasingRed = False
#             increasingBlue = True
#     elif decreasingRed:
#         red = red - 1
#         if red == 0:
#             decreasingRed = False
#             decreasingBlue = True
#             
#     if increasingBlue:
#         blue = blue + 1
#         if blue == 255:
#             increasingBlue = False
#             decreasingRed = True
#     elif decreasingBlue:
#         blue = blue - 1
#         if blue == 0:
#             increasingRed = True
#             decreasingBlue = False

