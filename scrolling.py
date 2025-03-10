'''
References:
2025-03-09

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

# scrolling.py

from machine import Pin, SPI
import max7219
from time import sleep

#	CONFIGURATION SETTINGS
num_max_modules = 12  # Number of MAX7219 modules in a row
scroll_speed = .05    # Scrolling speed in seconds per frame
scrolling_message = "They see me scrollin' ... my Pico "  # Text to scroll
brightness = 0         # Brightness level (0-15)

#	INITIALIZE DISPLAY
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)

display = max7219.Matrix8x8(spi, cs, num_max_modules)
display.brightness(brightness)

#	CALCULATE DISPLAY WIDTH & TEXT SIZE
display_width = num_max_modules * 8  # Total width in pixels
text_width = len(scrolling_message) * 8  # Total text width in pixels

#	Clear display before scrolling
display.fill(0)
display.show()
sleep(1)

#	SCROLLING LOOP
while True:
    for x in range(display_width, -text_width, -1):     
        display.fill(0)
        display.text(scrolling_message, x, 0, 1)
        display.show()
        sleep(scroll_speed)


