# ILI9488 standalone SPI driver for MicroPython
# Screen: KMRTM35018-SPI V.10 | ILI9488 | 3.5" | 480x320 | SPI | RGB666 | BGR
#
# No LVGL, no external frameworks needed.
# Streaming mode: draws directly to display row-by-row (no full framebuffer).
#
# Usage:
#   from drivers.display.ili9488_raw import ILI9488
#   from machine import SPI, Pin
#   spi  = SPI(1, baudrate=40_000_000, polarity=0, phase=0, sck=Pin(12), mosi=Pin(11), miso=None)
#   disp = ILI9488(spi, cs=Pin(10,Pin.OUT), dc=Pin(14,Pin.OUT), rst=Pin(9,Pin.OUT), bl=Pin(13,Pin.OUT))
#   disp.init()
#   disp.fill(ILI9488.BLACK)
#   disp.fill_rect(10, 10, 100, 50, ILI9488.WHITE)

import time
import struct


class ILI9488:

    WHITE = b'\xFF\xFF\xFF'
    BLACK = b'\x00\x00\x00'
    RED   = b'\xFF\x00\x00'
    GREEN = b'\x00\xFF\x00'
    BLUE  = b'\x00\x00\xFF'

    def __init__(self, spi, cs, dc, rst, bl, width=480, height=320):
        self._spi = spi
        self._cs  = cs
        self._dc  = dc
        self._rst = rst
        self._bl  = bl
        self.width  = width
        self.height = height

    # ---- low-level ---------------------------------------------------------

    def _write(self, cmd, data=None):
        self._cs(0)
        self._dc(0); self._spi.write(bytes([cmd]))
        if data:
            self._dc(1); self._spi.write(bytes(data))
        self._cs(1)

    def _set_window(self, x0, y0, x1, y1):
        self._cs(0)
        self._dc(0); self._spi.write(b'\x2A')
        self._dc(1); self._spi.write(struct.pack('>HH', x0, x1))
        self._dc(0); self._spi.write(b'\x2B')
        self._dc(1); self._spi.write(struct.pack('>HH', y0, y1))
        self._cs(1)

    # ---- init --------------------------------------------------------------

    def init(self):
        self._rst(0); time.sleep_ms(10)
        self._rst(1); time.sleep_ms(120)

        self._write(0x01); time.sleep_ms(200)  # SWRESET
        self._write(0x11); time.sleep_ms(120)  # SLPOUT

        self._write(0xE0, [0x00,0x03,0x09,0x08,0x16,
                           0x0A,0x3F,0x78,0x4C,0x09,
                           0x0A,0x08,0x16,0x1A,0x0F])
        self._write(0xE1, [0x00,0x16,0x19,0x03,0x0F,
                           0x05,0x32,0x45,0x46,0x04,
                           0x0E,0x0D,0x35,0x37,0x0F])
        self._write(0xC0, [0x17, 0x15])
        self._write(0xC1, [0x41])
        self._write(0xC5, [0x00, 0x12, 0x80])
        self._write(0x36, [0x20 | 0x40 | 0x08])  # landscape + BGR
        self._write(0x3A, [0x66])                  # 18-bit / RGB666 over SPI
        self._write(0xB0, [0x00])
        self._write(0xB1, [0xA0])
        self._write(0xB4, [0x02])
        self._write(0xB6, [0x02, 0x02, 0x3B])
        self._write(0xB7, [0xC6])
        self._write(0xF7, [0xA9, 0x51, 0x2C, 0x02])
        self._write(0x29); time.sleep_ms(100)      # DISPON
        self._bl(1)

    # ---- drawing -----------------------------------------------------------

    def fill_rect(self, x, y, w, h, color3):
        """Fill a rectangle with a 3-byte RGB colour."""
        if w <= 0 or h <= 0:
            return
        self._set_window(x, y, x + w - 1, y + h - 1)
        self._cs(0)
        self._dc(0); self._spi.write(b'\x2C')
        self._dc(1)
        row = color3 * w
        for _ in range(h):
            self._spi.write(row)
        self._cs(1)

    def fill(self, color3):
        """Fill the entire screen."""
        self._set_window(0, 0, self.width - 1, self.height - 1)
        self._cs(0)
        self._dc(0); self._spi.write(b'\x2C')
        self._dc(1)
        chunk = color3 * self.width  # one row
        for _ in range(self.height):
            self._spi.write(chunk)
        self._cs(1)

    def fill_round_rect(self, x, y, w, h, r, color3):
        """Fill a rounded rectangle."""
        r = max(0, min(r, w // 2 - 1, h // 2 - 1))
        r2 = r * r
        for row in range(h):
            if row < r:
                dy = r - row
                dx = int((r2 - dy * dy) ** 0.5)
                x0, x1 = x + r - dx, x + w - r + dx - 1
            elif row >= h - r:
                dy = row - (h - r)
                dx = int((r2 - dy * dy) ** 0.5)
                x0, x1 = x + r - dx, x + w - r + dx - 1
            else:
                x0, x1 = x, x + w - 1
            x0 = max(0, x0); x1 = min(self.width - 1, x1)
            actual_y = y + row
            if 0 <= actual_y < self.height and x1 >= x0:
                self.fill_rect(x0, actual_y, x1 - x0 + 1, 1, color3)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color3):
        """Fill a triangle using scanlines."""
        pts = sorted([(y0,x0),(y1,x1),(y2,x2)])
        (ya,xa),(yb,xb),(yc,xc) = pts

        def interp(y, ay, ax, by, bx):
            return ax if by == ay else ax + (bx-ax)*(y-ay)//(by-ay)

        for y in range(max(0, ya), min(self.height - 1, yc) + 1):
            ax = interp(y,ya,xa,yb,xb) if y<=yb else interp(y,yb,xb,yc,xc)
            bx = interp(y,ya,xa,yc,xc)
            if ax > bx: ax, bx = bx, ax
            ax = max(0, ax); bx = min(self.width-1, bx)
            if bx >= ax:
                self.fill_rect(ax, y, bx-ax+1, 1, color3)

    @staticmethod
    def rgb(r, g, b):
        """Convert 0-255 RGB to 3-byte colour tuple for this driver."""
        return bytes([r, g, b])
