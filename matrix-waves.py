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

# matrix-waves

from machine import Pin, SPI
import max7219
import math
import time
import random

#	CONFIGURATION SETTINGS
num_max_modules = 12   # Number of MAX7219 modules in a row
brightness = 0         # Global brightness level (0-15)
wave_speed = 0.07      # Speed of wave animation (lower = faster)
wave_amplitude = 3     # Amplitude (height of wave in pixels)
wave_frequency = 0.5   # Frequency (wavelength size)
wave_types = ["Sonar_Left_to_Right", "Sonar_Right_to_Left"]  # Options: "sine", "cosine", "triangle", "KITT", "MiddleOut", "MiddleIn", "Sonar_Left_to_Right", "Sonar_Right_to_Left", "EQ"

#	INITIALIZE DISPLAY
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, num_max_modules)
display.brightness(brightness)

#	Screen dimensions
width = num_max_modules * 8  # 12 * 8 = 96 pixels
height = 8  # MAX7219 is always 8 pixels tall
num_bars = width // 6  # Number of EQ bars (each bar is 6 pixels wide)

#	WAVE FUNCTIONS
def sine_wave(x, time_offset):
    """Generates a sine wave pattern."""
    return int((math.sin(x * wave_frequency + time_offset) * wave_amplitude) + (height // 2))

def cosine_wave(x, time_offset):
    """Generates a cosine wave pattern."""
    return int((math.cos(x * wave_frequency + time_offset) * wave_amplitude) + (height // 2))

def triangle_wave(x, time_offset):
    """Generates a triangle wave pattern."""
    return int(((abs(((x + time_offset) % (2 * math.pi)) - math.pi) - (math.pi / 2)) * (2 * wave_amplitude)) + (height // 2))

def kitt_wave(frame):
    """Knight Rider-style bouncing LED."""
    bar_width = 6  # Size of the block
    pos = (frame % (width * 2 - bar_width * 2))  # Bounce within range
    if pos >= width:
        pos = (width * 2 - bar_width * 2) - pos  # Reverse direction
    return [pos + i for i in range(bar_width)]  # Return block range

def middle_out_wave(frame):
    """Expands from the middle outward."""
    radius = frame % (width // 2)  # Expanding radius
    return list(range((width // 2) - radius, (width // 2) + radius + 1))

def middle_in_wave(frame):
    """Contracts from the edges inward."""
    max_radius = width // 2
    radius = max_radius - (frame % max_radius)  # Shrinking radius
    return list(range((width // 2) - radius, (width // 2) + radius + 1))

def sonar_left_to_right(frame):
    """Sweeping motion left to right."""
    return [frame % width]  # Returns a single column position

def sonar_right_to_left(frame):
    """Sweeping motion right to left."""
    return [width - 1 - (frame % width)]  # Returns a single column position

def eq_display(frame):
    """Simulated EQ bars moving up and down randomly."""
    bar_heights = [random.randint(1, height) for _ in range(num_bars)]  # Randomized bar heights
    columns = []
    
    for i, bar_height in enumerate(bar_heights):
        x_start = i * 6  # Each bar is 6 pixels wide
        for x in range(x_start, x_start + 5):  # Draw bars with spacing
            for y in range(height - bar_height, height):
                columns.append((x, y))  # Store coordinates for lighting

    return columns

#	Map wave type to function
wave_functions = {
    "sine": sine_wave,
    "cosine": cosine_wave,
    "triangle": triangle_wave,
    "KITT": kitt_wave,
    "MiddleOut": middle_out_wave,
    "MiddleIn": middle_in_wave,
    "Sonar_Left_to_Right": sonar_left_to_right,
    "Sonar_Right_to_Left": sonar_right_to_left,
    "EQ": eq_display
}

#	Validate selected wave types
selected_wave_functions = [wave_functions[w] for w in wave_types if w in wave_functions]

#	ANIMATION LOOP
frame = 0  #	Used for movement
while True:
    display.fill(0)  #	Clear screen

    for wave_function in selected_wave_functions:
        if wave_function in [sine_wave, cosine_wave, triangle_wave]:
            #	Smooth waveform display
            for x in range(width):
                y = wave_function(x, frame * wave_speed)  #	Compute y position
                if 0 <= y < height:
                    display.pixel(x, y, 1)  #	Light up the corresponding pixel

        elif wave_function in [eq_display]:
            #	EQ display effect
            for x, y in wave_function(frame):
                display.pixel(x, y, 1)

        else:
            #	Bouncing block, middle, and sonar waves
            for x in wave_function(frame):
                if 0 <= x < width:
                    for y in range(height):  #	Fill the column
                        display.pixel(x, y, 1)

    display.show()
    frame += 1  #	Advance animation frame
    time.sleep(wave_speed)  #	Control speed


