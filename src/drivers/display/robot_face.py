"""Animated robot face on ILI9488 480x320 SPI display (ESP32-S3).

Raw SPI driver + two blinking eyes with drifting pupils.
Standard MicroPython only — no LVGL, no external libraries.
"""

import machine
import time
import math
import random

# --- Pins ---
_RES = 9
_CS = 10
_MOSI = 11
_SCLK = 12
_LED = 13
_DC = 15

# --- Screen ---
W, H = 480, 320

# --- RGB666 colors (3 bytes per pixel, lower 2 bits of each byte ignored) ---
BG = b'\x08\x14\x28'  # ~#0A1628
WHITE = b'\xFC\xFC\xFC'
BLACK = b'\x00\x00\x00'


class Display:
    """ILI9488 raw SPI driver, RGB666 mode, 480x320 landscape."""

    def __init__(self):
        self.spi = machine.SoftSPI(
            baudrate=20_000_000, polarity=0, phase=0,
            sck=machine.Pin(_SCLK), mosi=machine.Pin(_MOSI),
            miso=machine.Pin(14),  # MISO unused, just needs a different pin than MOSI
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
        self._cmd(0x36, b'\x68')  # MADCTL: landscape + BGR
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

    def fill(self, x, y, w, h, color):
        """Fill a rectangle with a solid RGB666 color."""
        self.window(x, y, w, h)
        row = color * w
        self.start()
        for _ in range(h):
            self.spi.write(row)
        self.stop()


class Face:
    """Animated robot face: two round-rect eyes with drifting pupils and blinks."""

    # Eye layout
    EW, EH, ER = 150, 110, 30  # width, height, corner radius
    LX, RX, EY = 65, 265, 105  # left-eye x, right-eye x, eyes top-y
    PR, PM = 22, 35             # pupil radius, pupil margin from eye edge

    def __init__(self, lcd):
        self.lcd = lcd

        # Pre-compute horizontal corner inset for each row of the eye
        r = self.ER
        eh = self.EH
        self._ins = [0] * eh
        for y in range(r):
            d = r - y - 1
            s = r * r - d * d
            v = r - int(math.sqrt(s)) if s > 0 else r
            self._ins[y] = v
            self._ins[eh - 1 - y] = v

        # Pre-allocated color blocks for fast slice fills
        self._wrow = WHITE * self.EW
        self._bgb = BG * (r + 5)
        self._blk = BLACK * (self.PR * 2 + 4)
        self._buf = bytearray(self.EW * 3)

        # Pupil state — float for smooth lerp, int for last-drawn position
        lcx = self.LX + self.EW // 2
        rcx = self.RX + self.EW // 2
        ecy = self.EY + self.EH // 2
        self.lp = [float(lcx), float(ecy)]
        self.rp = [float(rcx), float(ecy)]
        self.lt = [lcx, ecy]
        self.rt = [rcx, ecy]
        self.li = [lcx, ecy]
        self.ri = [rcx, ecy]

        # Blink: bh = eyelid height in pixels, bd = direction (0/1/-1)
        self.bh = 0
        self.bd = 0
        now = time.ticks_ms()
        self.b_at = now + random.randint(3000, 5000)
        self.r_at = now + random.randint(1000, 3000)

    # --- Rendering primitives ---

    def _band(self, ex, y0, y1, pcx, pcy):
        """Draw rows y0..y1 (screen coords) of one eye as a single SPI stream."""
        if y1 < y0:
            return
        lcd = self.lcd
        buf = self._buf
        wrow = self._wrow
        bgb = self._bgb
        blk = self._blk
        ins = self._ins
        pr2 = self.PR * self.PR
        ew = self.EW
        ew3 = ew * 3
        ey = self.EY

        lcd.window(ex, y0, ew, y1 - y0 + 1)
        lcd.start()
        for sy in range(y0, y1 + 1):
            buf[:ew3] = wrow[:ew3]
            inset = ins[sy - ey]
            if inset:
                n = inset * 3
                buf[:n] = bgb[:n]
                buf[ew3 - n:ew3] = bgb[:n]
            dy = sy - pcy
            rem = pr2 - dy * dy
            if rem >= 0:
                dx = int(math.sqrt(rem))
                sl = max(pcx - dx - ex, inset)
                sr = min(pcx + dx - ex, ew - 1 - inset)
                if sl <= sr:
                    n3 = (sr - sl + 1) * 3
                    buf[sl * 3:sl * 3 + n3] = blk[:n3]
            lcd.spi.write(memoryview(buf)[:ew3])
        lcd.stop()

    def _eye(self, ex, pcx, pcy):
        """Draw a complete eye."""
        self._band(ex, self.EY, self.EY + self.EH - 1, pcx, pcy)

    def _pupil(self, ex, ox, oy, nx, ny):
        """Redraw only the dirty rectangle around a moving pupil."""
        pr = self.PR
        x0 = max(min(ox, nx) - pr - 2, ex)
        x1 = min(max(ox, nx) + pr + 2, ex + self.EW - 1)
        y0 = max(min(oy, ny) - pr - 2, self.EY)
        y1 = min(max(oy, ny) + pr + 2, self.EY + self.EH - 1)
        rw = x1 - x0 + 1
        if rw <= 0 or y1 < y0:
            return

        lcd = self.lcd
        buf = self._buf
        wrow = self._wrow
        bgb = self._bgb
        blk = self._blk
        ins = self._ins
        pr2 = pr * pr
        ew = self.EW
        ey = self.EY
        rw3 = rw * 3

        lcd.window(x0, y0, rw, y1 - y0 + 1)
        lcd.start()
        for sy in range(y0, y1 + 1):
            inset = ins[sy - ey]
            el = ex + inset
            er = ex + ew - 1 - inset

            buf[:rw3] = wrow[:rw3]

            # Fill background where corners intrude into dirty rect
            if x0 < el:
                n = min(el - x0, rw) * 3
                buf[:n] = bgb[:n]
            if x1 > er:
                s = max(er + 1 - x0, 0)
                n = (rw - s) * 3
                if n > 0:
                    buf[s * 3:s * 3 + n] = bgb[:n]

            # Pupil circle span
            dy = sy - ny
            rem = pr2 - dy * dy
            if rem >= 0:
                dx = int(math.sqrt(rem))
                sl = max(nx - dx, el) - x0
                sr = min(nx + dx, er) - x0
                if 0 <= sl <= sr < rw:
                    n = (sr - sl + 1) * 3
                    buf[sl * 3:sl * 3 + n] = blk[:n]

            lcd.spi.write(memoryview(buf)[:rw3])
        lcd.stop()

    # --- High-level API ---

    def draw(self):
        """Full-screen initial render — background first, then eyes."""
        self.lcd.fill(0, 0, W, H, BG)
        self._eye(self.LX, self.li[0], self.li[1])
        self._eye(self.RX, self.ri[0], self.ri[1])

    def _tgt(self, ex):
        """Random pupil target within eye bounds."""
        m = self.PM
        return [random.randint(ex + m, ex + self.EW - m),
                random.randint(self.EY + m, self.EY + self.EH - m)]

    def update(self):
        """Advance one animation frame. Call in a tight loop."""
        now = time.ticks_ms()

        # Retarget pupils periodically (same offset for both eyes)
        if time.ticks_diff(now, self.r_at) >= 0:
            m = self.PM
            dx = random.randint(-self.EW // 2 + m, self.EW // 2 - m)
            dy = random.randint(-self.EH // 2 + m, self.EH // 2 - m)
            lcx = self.LX + self.EW // 2
            rcx = self.RX + self.EW // 2
            ecy = self.EY + self.EH // 2
            self.lt = [lcx + dx, ecy + dy]
            self.rt = [rcx + dx, ecy + dy]
            self.r_at = now + random.randint(1500, 4000)

        # Exponential lerp toward target
        t = 0.08
        self.lp[0] += (self.lt[0] - self.lp[0]) * t
        self.lp[1] += (self.lt[1] - self.lp[1]) * t
        self.rp[0] += (self.rt[0] - self.rp[0]) * t
        self.rp[1] += (self.rt[1] - self.rp[1]) * t

        li = [int(self.lp[0] + 0.5), int(self.lp[1] + 0.5)]
        ri = [int(self.rp[0] + 0.5), int(self.rp[1] + 0.5)]

        # Redraw pupils only when integer position changed and not mid-blink
        if self.bd == 0:
            if li != self.li:
                self._pupil(self.LX, self.li[0], self.li[1], li[0], li[1])
                self.li = li
            if ri != self.ri:
                self._pupil(self.RX, self.ri[0], self.ri[1], ri[0], ri[1])
                self.ri = ri
            # Trigger blink
            if time.ticks_diff(now, self.b_at) >= 0:
                self.bd = 1

        # Blink: closing
        if self.bd == 1:
            oh = self.bh
            self.bh = min(self.bh + 5, self.EH // 2)
            ey, eh, ew = self.EY, self.EH, self.EW
            strip_h = self.bh - oh
            if strip_h > 0:
                for ex in (self.LX, self.RX):
                    # Top eyelid grows down
                    self.lcd.fill(ex, ey + oh, ew, strip_h, BG)
                    # Bottom eyelid grows up
                    self.lcd.fill(ex, ey + eh - self.bh, ew, strip_h, BG)
            if self.bh >= self.EH // 2:
                self.bd = -1

        # Blink: opening
        elif self.bd == -1:
            oh = self.bh
            self.bh = max(self.bh - 6, 0)
            # Snap pupil int positions to current float values
            self.li = [int(self.lp[0] + 0.5), int(self.lp[1] + 0.5)]
            self.ri = [int(self.rp[0] + 0.5), int(self.rp[1] + 0.5)]

            if self.bh <= 0:
                # Fully open — restore both eyes completely
                self.bd = 0
                self.b_at = now + random.randint(3000, 5000)
                self._eye(self.LX, self.li[0], self.li[1])
                self._eye(self.RX, self.ri[0], self.ri[1])
            else:
                # Reveal strips progressively
                ey, eh = self.EY, self.EH
                for ex, pi in ((self.LX, self.li), (self.RX, self.ri)):
                    self._band(ex, ey + self.bh, ey + oh - 1, pi[0], pi[1])
                    self._band(ex, ey + eh - oh, ey + eh - 1 - self.bh, pi[0], pi[1])

        time.sleep_ms(16)


def main():
    face = Face(Display())
    face.draw()
    while True:
        face.update()


if __name__ == '__main__':
    main()
