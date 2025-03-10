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

# pole_position.py

from machine import Pin, SPI
import max7219
import time
import random

# 🔧 CONFIGURATION SETTINGS 🔧
num_max_modules = 12   # Number of MAX7219 modules in a row
speed = 0.1            # Speed of the animation (lower = faster)
brightness = 0         # Brightness level (0-15)
curve_intensity = 1    # How sharply the road curves (higher = more aggressive turns)
lane_divider_spacing = 2  # Spacing between dashed lines

# 🔌 INITIALIZE DISPLAY 🔌
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, num_max_modules)

# 🔥 Set brightness
display.brightness(brightness)

# Screen dimensions
width = num_max_modules * 8  # Total width of the display
height = 8  # MAX7219 is always 8 pixels tall

# 🌄 ROAD VARIABLES 🌄
road_center = width // 2  # Road center position
road_width = width // 3  # Base width of the road at the bottom
curve_direction = random.choice([-1, 1])  # -1 (left), 1 (right)
curve_timer = 0  # Determines when to change curves
max_curve_shift = width // 4  # Max left/right movement

lane_divider_offset = 0  # Controls the movement of the dashed lines

def draw_road():
    """Draws a road with correct perspective: wide at the bottom, narrow at the top."""
    display.fill(0)  # Clear screen

    for y in range(height):
        perspective = y * 2  # Road gets narrower higher up

        left_road = max(road_center - (road_width // 2) + perspective, 0)
        right_road = min(road_center + (road_width // 2) - perspective, width - 1)
        center_road = road_center  # Center lane moves with road

        # Draw road edges
        if 0 <= left_road < width:
            display.pixel(left_road, y, 1)
        if 0 <= right_road < width:
            display.pixel(right_road, y, 1)

        # Draw dashed center lane
        if y % 2 == (lane_divider_offset % 2):  # Makes it dashed
            if left_road + 2 < center_road < right_road - 2:  # Keep it within the road
                display.pixel(center_road, y, 1)

def update_road():
    """Moves the road left or right and updates lane dividers."""
    global road_center, curve_direction, curve_timer, lane_divider_offset

    # Change curve direction randomly over time
    curve_timer += 1
    if curve_timer > random.randint(10, 20):  # Change direction randomly
        curve_timer = 0
        curve_direction = random.choice([-1, 1])  # Left or right turn

    # Shift the road position
    road_center += curve_direction * curve_intensity

    # Keep the road within boundaries
    if road_center < max_curve_shift:
        road_center = max_curve_shift
        curve_direction = 1
    elif road_center > width - max_curve_shift:
        road_center = width - max_curve_shift
        curve_direction = -1

    # Move the lane dividers for a moving effect
    lane_divider_offset = (lane_divider_offset + 1) % lane_divider_spacing

# ⏳ GAME LOOP ⏳
while True:
    draw_road()
    update_road()
    display.show()
    time.sleep(speed)

