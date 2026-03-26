import time
import random

# RGB666 colors for angry mode
_RED = b'\xFC\x00\x00'
_BG  = b'\x04\x08\x18'


class AngryAnim:
    """Angry animation: red eyes with top ~1/4 cut by a diagonal (furrowed brow), random blinks."""

    _BSTEP_MS = 22

    def __init__(self):
        now = time.ticks_ms()
        self.bh = 0
        self.bd = 0
        self.b_at      = now + random.randint(3000, 6000)
        self._bstep_at = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _brow_cutoff(col, ew, eh, side):
        """Return how many pixels from the TOP are hidden by the brow diagonal.

        The diagonal goes from the inner-top corner (higher cut) to the
        outer-top corner (lower cut), covering the top 1/4 of the eye height.

        side: 'L' = left eye (inner edge is the right side of the sprite),
              'R' = right eye (inner edge is the left side of the sprite).
        """
        max_cut = eh // 4        # deepest cut (inner corner): 1/4 of eye height
        min_cut = max_cut // 3   # shallowest cut (outer corner): ~1/12

        t = col / (ew - 1)       # 0.0 (left pixel) … 1.0 (right pixel)

        if side == 'L':
            # inner edge is on the RIGHT → t=1.0 is the inner corner
            inner_t = 1.0
        else:
            # inner edge is on the LEFT  → t=0.0 is the inner corner
            inner_t = 0.0

        # Linear blend: inner corner gets max_cut, outer corner gets min_cut
        cut = min_cut + (max_cut - min_cut) * abs(t - inner_t)
        return int(cut)

    def _draw_eye(self, face, ex, side, bh_top, bh_bot):
        """Redraw an angry eye with:
          - brow diagonal cut from the top
          - optional blink strips from top/bottom (bh_top / bh_bot pixels hidden)
        """
        ey   = face.EY
        eh   = face.EH
        ew   = face.EW
        ins  = face._ins       # corner insets (pre-computed in Face)
        lcd  = face.lcd
        spi  = lcd.spi

        ew3  = ew * 3
        buf  = bytearray(ew3)

        lcd.window(ex, ey, ew, eh)
        lcd.start()

        for row in range(eh):
            brow_row = False
            # top blink strip
            if row < bh_top:
                brow_row = True
            # bottom blink strip
            elif row >= eh - bh_bot:
                brow_row = True

            if brow_row:
                buf[:ew3] = _BG * ew
            else:
                # Build red row with rounded-rect corner masking
                inset = ins[row]
                for px in range(ew):
                    # brow diagonal: pixels above the diagonal line are BG
                    brow_cut = self._brow_cutoff(px, ew, eh, side)
                    if row < brow_cut:
                        c = _BG
                    elif inset and (px < inset or px >= ew - inset):
                        c = _BG
                    else:
                        c = _RED
                    off = px * 3
                    buf[off:off + 3] = c

            spi.write(buf)

        lcd.stop()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, face):
        """Full initial draw of the angry face (red eyes + background)."""
        lcd = face.lcd
        lcd.fill(0, 0, 480, 320, _BG)
        self._draw_eye(face, face.LX, 'L', 0, 0)
        self._draw_eye(face, face.RX, 'R', 0, 0)
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

        if self.bd == 1:   # closing
            self.bh = min(self.bh + 6, face.EH // 2)
            half = self.bh
            self._draw_eye(face, face.LX, 'L', half, half)
            self._draw_eye(face, face.RX, 'R', half, half)
            if self.bh >= face.EH // 2:
                self.bd = -1

        elif self.bd == -1:  # opening
            self.bh = max(self.bh - 6, 0)
            half = self.bh
            self._draw_eye(face, face.LX, 'L', half, half)
            self._draw_eye(face, face.RX, 'R', half, half)
            if self.bh <= 0:
                self.bd = 0
                self.b_at = now + random.randint(3000, 6000)
