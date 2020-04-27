import board
import neopixel
import time

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

while True:
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(60.0/(84.635))
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(60.0/(84.635))
    pixels.fill((0, 0, 255))
    pixels.show()
    time.sleep(60.0/84.635)
