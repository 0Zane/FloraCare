"""Animated robot face on ILI9488 480x320 SPI display (ESP32-S3).

Raw SPI driver + two blinking eyes (no pupils).
Standard MicroPython only — no LVGL, no external libraries.
"""

import machine
import time
import math
import framebuf  # MicroPython built-in
from drivers.display.anims.idle import IdleAnim

# --- Pins ---
_RES  = 9
_CS   = 10
_MOSI = 11
_SCLK = 12
_LED  = 13
_DC   = 14
_MISO = 14

# --- Screen ---
W, H = 480, 320

# --- RGB666 colors (3 bytes per pixel, lower 2 bits of each byte ignored) ---
BG   = b'\x04\x08\x18'  # ~#040818 deep black-navy
BLUE = b'\x00\xFC\xFC'  # max brightness cyan
DIM  = b'\x00\x60\x70'  # dimmed cyan for labels (~38% brightness)
RED  = b'\xFC\x00\x00'  # alert red for out-of-range values

# --- Sensor bar layout (bottom of screen) ---
_SEP_Y  = 260          # separator line y (mouth ends at 215+38=253)
_BAR_Y  = 262          # bar background start
_LBL_Y  = 270          # label row y  (scale=1 → 8px high)
_VAL_Y  = 282          # value row y  (scale=2 → 16px high, ends at 298)
_COL_CX = (60, 180, 300, 420)   # column centers
_COL_XS = (0, 120, 240, 360)    # column left edges
_COL_W  = 120


class Display:
    """ILI9488 raw SPI driver, RGB666 mode, 480x320 landscape."""

    def __init__(self):
        self.spi = machine.SoftSPI(
            baudrate=40_000_000, polarity=0, phase=0,
            sck=machine.Pin(_SCLK), mosi=machine.Pin(_MOSI),
            miso=machine.Pin(_MISO),
        )
        self.cs = machine.Pin(_CS, machine.Pin.OUT, value=1)
        self.dc = machine.Pin(_DC, machine.Pin.OUT, value=1)
        self.rst = machine.Pin(_RES, machine.Pin.OUT, value=1)
        self.led = machine.Pin(_LED, machine.Pin.OUT, value=0)
        self._init_hw()
        self.led.value(1)

    def _cmd(self, c, d=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([c]))
        if d is not None:
            self.dc.value(1)
            self.spi.write(d if isinstance(d, (bytes, bytearray)) else bytes(d))
        self.cs.value(1)

    def _init_hw(self):
        self.rst.value(0)
        time.sleep_ms(20)
        self.rst.value(1)
        time.sleep_ms(120)
        self._cmd(0x01)  # Software reset
        time.sleep_ms(120)
        self._cmd(0x11)  # Sleep out
        time.sleep_ms(120)

        # Gamma
        self._cmd(0xE0, b'\x00\x03\x09\x08\x16\x0A\x3F\x78'
                        b'\x4C\x09\x0A\x08\x16\x1A\x0F')
        self._cmd(0xE1, b'\x00\x16\x19\x03\x0F\x05\x32\x45'
                        b'\x46\x04\x0E\x0D\x35\x37\x0F')
        # Power
        self._cmd(0xC0, b'\x17\x15')
        self._cmd(0xC1, b'\x41')
        self._cmd(0xC5, b'\x00\x12\x80')
        # Display
        self._cmd(0x36, b'\x28')  # MADCTL: landscape rotated 180 + BGR (MY=0, MX=0, MV=1, BGR=1)
        self._cmd(0x3A, b'\x66')  # 18-bit RGB666
        self._cmd(0xB0, b'\x00')  # Interface mode control
        self._cmd(0xB1, b'\xA0')  # Frame rate 60 Hz
        self._cmd(0xB4, b'\x02')  # Display inversion
        self._cmd(0xB6, b'\x02\x02')  # Display function control
        self._cmd(0xE9, b'\x00')  # Set image function
        self._cmd(0xF7, b'\xA9\x51\x2C\x82')  # Adjust control 3
        self._cmd(0x29)  # Display ON
        time.sleep_ms(50)

    def window(self, x, y, w, h):
        """Set the drawing window (CASET + RASET)."""
        xe, ye = x + w - 1, y + h - 1
        self._cmd(0x2A, bytes([x >> 8, x & 0xFF, xe >> 8, xe & 0xFF]))
        self._cmd(0x2B, bytes([y >> 8, y & 0xFF, ye >> 8, ye & 0xFF]))

    def start(self):
        """Begin RAMWR and hold CS low for pixel streaming."""
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(b'\x2C')
        self.dc.value(1)

    def stop(self):
        self.cs.value(1)

    def restore_dc(self):
        """Re-assert DC pin as output. Call after any code that may have disturbed GPIO."""
        self.dc = machine.Pin(_DC, machine.Pin.OUT, value=1)

    def fill(self, x, y, w, h, color):
        """Fill a rectangle with a solid RGB666 color."""
        self.window(x, y, w, h)
        row = color * w
        self.start()
        for _ in range(h):
            self.spi.write(row)
        self.stop()


class StatusBar:
    """Sensor data strip at the bottom of the screen."""

    _LABELS = ("TEMP", "HUM", "SOIL", "LUX")

    def __init__(self, lcd):
        self.lcd = lcd
        self._strs = [""] * 4
        self._states = [0] * 4  # 0 = normal, != 0 = out of range

    def draw_static(self):
        """Draw separator line, background and static labels. Call after full screen fill."""
        lcd = self.lcd
        lcd.fill(0, _SEP_Y, W, 2, BLUE)                 # neon separator
        lcd.fill(0, _BAR_Y, W, H - _BAR_Y, BG)          # bar background
        # Subtle column dividers
        for sx in (120, 240, 360):
            lcd.fill(sx, _SEP_Y + 2, 1, H - _SEP_Y - 2, DIM)
        # Labels
        for lbl, cx in zip(self._LABELS, _COL_CX):
            lx = cx - len(lbl) * 4   # scale=1: 8px/char, center
            self._draw_text(lx, _LBL_Y, lbl, scale=1, color=DIM)
        self._strs = [""] * 4        # force value redraw on next update()
        self._states = [0] * 4

    def _draw_text(self, x, y, text, scale=2, color=BLUE):
        n = len(text)
        if n == 0:
            return
        w8     = n * 8
        stride = (w8 + 7) // 8
        mono   = bytearray(stride * 8)
        fb     = framebuf.FrameBuffer(mono, w8, 8, framebuf.MONO_HMSB)
        fb.fill(0)
        fb.text(text, 0, 0, 1)
        sw      = w8 * scale
        row_buf = bytearray(sw * 3)
        mv      = memoryview(row_buf)
        lcd     = self.lcd
        spi     = lcd.spi
        lcd.window(x, y, sw, 8 * scale)
        lcd.start()
        for sy in range(8):
            off = 0
            for sx in range(w8):
                bit = (mono[sy * stride + sx // 8] >> (sx % 8)) & 1
                px  = color if bit else BG
                for _ in range(scale):
                    row_buf[off:off + 3] = px
                    off += 3
            for _ in range(scale):
                spi.write(mv)
        lcd.stop()

    def update(self, temp, humi, soil, lux, states=None):
        """Redraw only columns whose value or alert state has changed."""
        if states is None:
            states = [0, 0, 0, 0]
        strs = [
            "{:.1f}C".format(temp) if temp >= 0 else "--.-C",
            "{}%".format(int(round(humi))) if humi >= 0 else "--%",
            "{}%".format(int(round(soil))) if soil >= 0 else "--%",
            "{}".format(int(lux))          if lux  >= 0 else "----",
        ]
        for i, (s, cx, col_x) in enumerate(zip(strs, _COL_CX, _COL_XS)):
            if s != self._strs[i] or states[i] != self._states[i]:
                color = RED if states[i] != 0 else BLUE
                self.lcd.fill(col_x + 1, _VAL_Y, _COL_W - 2, 16, BG)
                vx = cx - len(s) * 8   # scale=2: 16px/char, center
                self._draw_text(vx, _VAL_Y, s, scale=2, color=color)
        self._strs = strs
        self._states = states


class Face:
    """Animated robot face: two solid blue round-rect eyes with blinks."""

    EW, EH, ER = 130, 90, 25   # width, height, corner radius
    LX, RX, EY = 75, 275, 70   # left-eye x, right-eye x, eyes top-y

    MW, MH, MR = 160, 34, 16   # mouth width, height, corner radius
    MX = (W - 160) // 2        # mouth left-x (centered)
    MY = 187                    # mouth top-y

    BG   = BG
    BLUE = BLUE

    def __init__(self, lcd):
        self.lcd = lcd
        self.bar = StatusBar(lcd)
        r = self.ER
        eh = self.EH

        # Pre-compute horizontal corner inset per row
        self._ins = [0] * eh
        for y in range(r):
            d = r - y - 1
            s = r * r - d * d
            v = r - int(math.sqrt(s)) if s > 0 else r
            self._ins[y] = v
            self._ins[eh - 1 - y] = v

        # Pre-allocated row buffers (full BLUE row + BG block for corners)
        ew = self.EW
        self._erow = BLUE * ew          # full eye-color row
        self._bgb  = BG * (r + 5)      # corner fill
        self._buf  = bytearray(ew * 3)
        # Batch buffer: 8 rows at a time for fewer SPI transactions
        self._BATCH = 8
        self._batch_buf = bytearray(ew * 3 * self._BATCH)

        self._anim = IdleAnim()

    # --- Rendering ---

    def _band(self, ex, y0, y1):
        """Draw rows y0..y1 (screen coords) of one eye, batched for speed."""
        if y1 < y0:
            return
        lcd       = self.lcd
        buf       = self._buf
        bbuf      = self._batch_buf
        erow      = self._erow
        bgb       = self._bgb
        ins       = self._ins
        ew        = self.EW
        ew3       = ew * 3
        ey        = self.EY
        BATCH     = self._BATCH

        lcd.window(ex, y0, ew, y1 - y0 + 1)
        lcd.start()
        mv   = memoryview(bbuf)
        sy   = y0
        spi  = lcd.spi
        while sy <= y1:
            chunk = min(BATCH, y1 - sy + 1)
            off = 0
            for row in range(sy, sy + chunk):
                buf[:ew3] = erow[:ew3]
                inset = ins[row - ey]
                if inset:
                    n = inset * 3
                    buf[:n] = bgb[:n]
                    buf[ew3 - n:ew3] = bgb[:n]
                bbuf[off:off + ew3] = buf[:ew3]
                off += ew3
            spi.write(mv[:off])
            sy += chunk
        lcd.stop()

    def _eye(self, ex):
        self._band(ex, self.EY, self.EY + self.EH - 1)

    def _draw_rrect(self, x, y, w, h, r):
        """Draw a filled rounded rectangle (used for static elements like mouth)."""
        ins = [0] * h
        for i in range(r):
            d = r - i - 1
            s = r * r - d * d
            ins[i] = r - int(math.sqrt(s)) if s > 0 else r
            ins[h - 1 - i] = ins[i]

        w3   = w * 3
        erow = BLUE * w
        bgb  = BG * (r + 5)
        buf  = bytearray(w3)
        lcd  = self.lcd
        lcd.window(x, y, w, h)
        lcd.start()
        for row in range(h):
            buf[:w3] = erow[:w3]
            inset = ins[row]
            if inset:
                n = inset * 3
                buf[:n] = bgb[:n]
                buf[w3 - n:w3] = bgb[:n]
            lcd.spi.write(buf)
        lcd.stop()

    def _mouth(self):
        self._draw_rrect(self.MX, self.MY, self.MW, self.MH, self.MR)

    # --- High-level API ---

    def draw(self):
        """Full-screen initial render."""
        self.lcd.fill(0, 0, W, H, BG)
        self._eye(self.LX)
        self._eye(self.RX)
        self._mouth()
        self.bar.draw_static()

    def set_sensors(self, temp, humi, soil, lux, states=None):
        """Push new sensor readings to the status bar."""
        self.bar.update(temp, humi, soil, lux, states)

    def set_anim(self, anim):
        """Switch to a new animation. Redraws the full screen immediately."""
        self._anim = anim
        anim.draw(self)

    def update(self):
        """Advance one animation frame. Call in a tight loop."""
        self._anim.tick(self)


def main():
    face = Face(Display())
    face.draw()
    while True:
        face.update()


if __name__ == '__main__':
    main()
