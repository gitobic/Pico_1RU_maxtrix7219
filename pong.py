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

# pong.py

from machine import Pin, SPI
import max7219
import time
import random

# 🔧 CONFIGURATION SETTINGS 🔧
num_max_modules = 12  # Number of MAX7219 modules in a row
game_speed = 0.1       # Speed of the game (lower = faster)
max_score = 5          # Max score before reset
paddle_length = 3      # Paddle size (height)
paddle_width = 2       # Paddle width (columns wide)
miss_chance = 0.1      # 10% chance a paddle will randomly "miss" the ball
reaction_time = 3      # Frames before impact when the paddle starts moving
brightness = 0         # Brightness level (0-15)

# 🔌 INITIALIZE DISPLAY 🔌
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, num_max_modules)

# 🔥 Set brightness (0-15)
display.brightness(brightness)

# Screen dimensions
width = num_max_modules * 8  # Total width of the display
height = 8  # MAX7219 is always 8 pixels tall

# PADDLE POSITION
left_paddle_y = height // 2 - paddle_length // 2
right_paddle_y = height // 2 - paddle_length // 2

# BALL POSITION AND DIRECTION
ball_x = width // 2
ball_y = height // 2
ball_dx = random.choice([-1, 1])  # Direction: -1 (left), 1 (right)
ball_dy = random.choice([-1, 0, 1])  # Vertical variation

# SCORES
left_score = 0
right_score = 0
allow_miss = False  # Flag to determine if a paddle will miss

def draw_paddle(x, y):
    """Draws a paddle at (x, y) with the configured width."""
    for i in range(paddle_length):  # Draw paddle height
        for j in range(paddle_width):  # Draw paddle width
            display.pixel(x + j, y + i, 1)  # Offset horizontally by width

def move_paddle(target_paddle_y, paddle_y):
    """Moves paddle toward target position."""
    if paddle_y < target_paddle_y:
        return min(paddle_y + 1, height - paddle_length)
    elif paddle_y > target_paddle_y:
        return max(paddle_y - 1, 0)
    return paddle_y  # Stay in place

def ai_paddle_movement():
    """Moves only the paddle that the ball is traveling toward and only just before impact."""
    global left_paddle_y, right_paddle_y, allow_miss

    # Determine how many frames until impact
    frames_until_impact = (width - ball_x) if ball_dx > 0 else ball_x

    # If the ball is moving right, control the right paddle
    if ball_dx > 0 and frames_until_impact <= reaction_time:
        if allow_miss:  # If AI is set to miss, do nothing
            return
        right_paddle_y = move_paddle(ball_y - paddle_length // 2, right_paddle_y)

    # If the ball is moving left, control the left paddle
    elif ball_dx < 0 and frames_until_impact <= reaction_time:
        if allow_miss:  # If AI is set to miss, do nothing
            return
        left_paddle_y = move_paddle(ball_y - paddle_length // 2, left_paddle_y)

def reset_ball():
    """Resets the ball position and randomizes direction."""
    global ball_x, ball_y, ball_dx, ball_dy, allow_miss
    ball_x = width // 2
    ball_y = height // 2
    ball_dx = random.choice([-1, 1])
    ball_dy = random.choice([-1, 0, 1])

    # Randomly decide if the paddle should miss
    allow_miss = random.random() < miss_chance

def update_ball():
    """Updates the ball's position and checks collisions."""
    global ball_x, ball_y, ball_dx, ball_dy, left_score, right_score

    next_x = ball_x + ball_dx
    next_y = ball_y + ball_dy

    # Ball Collision with Top and Bottom Walls
    if next_y < 0 or next_y >= height:
        ball_dy = -ball_dy  # Reverse vertical direction

    # Ball Collision with Left Paddle
    if next_x == paddle_width and left_paddle_y <= ball_y < left_paddle_y + paddle_length:
        ball_dx = 1  # Bounce right
        ball_dy = random.choice([-1, 0, 1])  # Random vertical change

    # Ball Collision with Right Paddle
    if next_x == width - paddle_width - 1 and right_paddle_y <= ball_y < right_paddle_y + paddle_length:
        ball_dx = -1  # Bounce left
        ball_dy = random.choice([-1, 0, 1])  # Random vertical change

    # Ball Out of Bounds (Scoring)
    if next_x < 0:
        right_score += 1  # Right player scores
        show_score()
        reset_ball()
    elif next_x >= width:
        left_score += 1  # Left player scores
        show_score()
        reset_ball()

    # Move ball
    ball_x += ball_dx
    ball_y += ball_dy

def show_score():
    """Shows the score for 3 seconds before resuming."""
    display.fill(0)
    display.text(str(left_score), width // 4, 1, 1)
    display.text(str(right_score), (width // 4) * 3, 1, 1)
    display.show()
    time.sleep(3)  # Pause for 3 seconds before resuming

# ⏳ GAME LOOP ⏳
while True:
    display.fill(0)  # Clear screen

    # Move only the paddle that the ball is approaching
    ai_paddle_movement()

    # Update ball movement
    update_ball()

    # Draw left paddle (starts at x=0)
    draw_paddle(0, left_paddle_y)

    # Draw right paddle (shift left by paddle width to fit on screen)
    draw_paddle(width - paddle_width, right_paddle_y)

    # Draw ball
    display.pixel(ball_x, ball_y, 1)

    # Display everything
    display.show()

    # Check if max score is reached
    if left_score >= max_score or right_score >= max_score:
        show_score()
        left_score = 0
        right_score = 0
        reset_ball()

    time.sleep(game_speed)  # Control game speed

