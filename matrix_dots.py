'''
Date: 2025-03-09

References:
https://www.reddit.com/r/homelab/comments/1iboomc/i_spent_a_few_days_designing_a_1u_bar_of_leds/?share_id=6Zg07iPYEONgRl4184CpN&utm_medium=ios_app&utm_name=iossmf&utm_source=share&utm_term=4
https://microcontrollerslab.com/max7219-led-dot-matrix-display-raspberry-pi-pico/
https://github.com/mcauser/micropython-max7219

MAX7219 Module	->	Pico
VCC	->	VBUS (5V)
GND	->	GND
DIN	->	GP3 (SPI0_TX)
CS	->	GP5 (SPI0_CSN)
CLK	->	GP2 (SPI0_SCK)

'''

#	matrix-dots.py

from machine import Pin, SPI
import max7219
import random
from time import sleep

#	CONFIGURATION SETTINGS
num_max_modules = 12   # Number of MAX7219 modules in a row
brightness = 0         # Global brightness level (0-15)
change_speed = 1    # Flickering update interval

#	INITIALIZE DISPLAY
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, num_max_modules)
display.brightness(brightness)

#	Screen dimensions
width = num_max_modules * 8  # 12 * 8 = 96 pixels
height = 8  # MAX7219 is always 8 pixels tall

while True:
    display.fill(0)  # Clear screen before update
    
    for y in range(height):
        for x in range(width):
            display.pixel(x, y, random.getrandbits(1))  # Random ON/OFF pixels

    display.show()
    
    #	Pause for random flickering effect
    sleep(change_speed)


