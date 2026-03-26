import time
import random


class IdleAnim:
    """Idle animation: random-interval eye blink."""

    _BSTEP_MS = 22   # ms between blink frames (7 frames × 22ms ≈ 154ms per half)

    def __init__(self):
        now = time.ticks_ms()
        self.bh = 0   # eyelid height in pixels
        self.bd = 0   # direction: 0=idle, 1=closing, -1=opening
        self.b_at      = now + random.randint(3000, 5000)
        self._bstep_at = 0

    def draw(self, face):
        """Full initial draw of the idle face."""
        face.lcd.fill(0, 0, 480, 320, b'\x04\x08\x18')
        face._eye(face.LX)
        face._eye(face.RX)
        face._mouth()
        face.bar.draw_static()

    def tick(self, face):
        now = time.ticks_ms()

        if self.bd == 0:
            if time.ticks_diff(now, self.b_at) >= 0:
                self.bd = 1
            return

        if time.ticks_diff(now, self._bstep_at) < 0:
            return
        self._bstep_at = now + self._BSTEP_MS

        if self.bd == 1:
            oh = self.bh
            self.bh = min(self.bh + 6, face.EH // 2)
            ey, eh, ew = face.EY, face.EH, face.EW
            strip_h = self.bh - oh
            if strip_h > 0:
                for ex in (face.LX, face.RX):
                    face.lcd.fill(ex, ey + oh, ew, strip_h, face.BG)
                    face.lcd.fill(ex, ey + eh - self.bh, ew, strip_h, face.BG)
            if self.bh >= face.EH // 2:
                self.bd = -1

        elif self.bd == -1:
            oh = self.bh
            self.bh = max(self.bh - 6, 0)
            ey, eh = face.EY, face.EH
            for ex in (face.LX, face.RX):
                face._band(ex, ey + self.bh, ey + oh - 1)
                face._band(ex, ey + eh - oh, ey + eh - 1 - self.bh)
            if self.bh <= 0:
                self.bd = 0
                self.b_at = now + random.randint(3000, 5000)
