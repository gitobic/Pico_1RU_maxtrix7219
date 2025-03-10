'''
Status: Not woking

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

# scrolling_with_fonts.py

from machine import Pin, SPI
import max7219
from time import sleep

# 🔧 CONFIGURATION
num_max_modules = 12
scroll_speed = 0.00001
scrolling_message = "ABC ABC ABC AAAA BBBB CCCC "
brightness = 0

# Custom 5x8 pixel font (expand this for full alphabet)
FONT_5x8 = {
    "A": [0x00, 0x7C, 0x12, 0x12, 0x7C, 0x00],  # A
    "B": [0x00, 0x7E, 0x4A, 0x4A, 0x34, 0x00],  # B
    "C": [0x00, 0x3C, 0x42, 0x42, 0x24, 0x00],  # C
    " ": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Space
}

# Initialize SPI and Display
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, num_max_modules)
display.brightness(brightness)

display_width = num_max_modules * 8  # Display width in pixels
column_offset = display_width  # Start off-screen

# Function to draw a character from FONT_5x8
def draw_char(display, char, x):
    if char in FONT_5x8:
        bitmap = FONT_5x8[char]
        for col in range(len(bitmap)):  # Loop through each column of pixels
            for row in range(8):  # Loop through each row of pixels
                pixel_on = (bitmap[col] >> row) & 1
                display.pixel(x + col, row, pixel_on)

# Scrolling Loop
while True:
    for x in range(display_width, -len(scrolling_message) * 6, -1):  
        display.fill(0)

        for i, char in enumerate(scrolling_message):
            draw_char(display, char, x + (i * 6))

        display.show()
        sleep(scroll_speed)

