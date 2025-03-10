from micropython import const
import framebuf
import utime

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)

class Matrix8x8:
    def __init__(self, spi, cs, num, brightness_mode=False):
        """
        MAX7219 Driver for 8x8 LED matrices.
        
        brightness_mode=True enables per-pixel brightness simulation (via PWM).
        """
        self.spi = spi
        self.cs = cs
        self.cs.init(cs.OUT, True)
        self.buffer = bytearray(8 * num)
        self.brightness_buffer = [[15 for _ in range(8 * num)] for _ in range(8)]  # Per-pixel brightness
        self.num = num
        self.brightness_mode = brightness_mode  # Enable brightness simulation?
        fb = framebuf.FrameBuffer(self.buffer, 8 * num, 8, framebuf.MONO_HLSB)
        self.framebuf = fb
        self.fill = fb.fill
        self.pixel = fb.pixel
        self.hline = fb.hline
        self.vline = fb.vline
        self.line = fb.line
        self.rect = fb.rect
        self.fill_rect = fb.fill_rect
        self.text = fb.text
        self.scroll = fb.scroll
        self.blit = fb.blit
        self.init()

    def _write(self, command, data):
        self.cs(0)
        for m in range(self.num):
            self.spi.write(bytearray([command, data]))
        self.cs(1)

    def init(self):
        for command, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7),
            (_DECODEMODE, 0),
            (_SHUTDOWN, 1),
        ):
            self._write(command, data)

    def brightness(self, value):
        """Set global brightness (0-15)."""
        if not 0 <= value <= 15:
            raise ValueError("Brightness out of range")
        self._write(_INTENSITY, value)

    def set_pixel_brightness(self, x, y, brightness):
        """Set individual pixel brightness (0-15)."""
        if not (0 <= brightness <= 15):
            brightness = 15  # Default to max if out of range
        self.brightness_buffer[y][x] = brightness

    def show(self, pwm_frame=0):
        """Render frame, applying brightness simulation if enabled."""
        for y in range(8):
            self.cs(0)
            for m in range(self.num):
                byte = 0
                for bit in range(8):
                    x = (m * 8) + bit
                    if self.brightness_mode:
                        # Apply software PWM to simulate brightness
                        if self.brightness_buffer[y][x] > pwm_frame:
                            byte |= (1 << bit)
                    else:
                        # Default binary display
                        if self.buffer[(y * self.num) + m] & (1 << bit):
                            byte |= (1 << bit)
                self.spi.write(bytearray([_DIGIT0 + y, byte]))
            self.cs(1)

