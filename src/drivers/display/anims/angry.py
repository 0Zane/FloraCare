import math

# RGB666 colors for angry mode
_RED = b'\xFC\x00\x00'
_BG  = b'\x04\x08\x18'


class AngryAnim:
    """Angry animation: red eyes with diagonal brow cut, sad mouth, random blinks."""

    _BSTEP_MS = 22

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _brow_cutoff(col, ew, eh, side):
        """Return how many pixels from the TOP are cut by the brow diagonal.

        Deep cut at the OUTER corner, shallow cut at the INNER corner —
        so the brows slope downward toward the center (angry look).

        side: 'L' = left eye (outer edge is LEFT  → col=0),
              'R' = right eye (outer edge is RIGHT → col=ew-1).
        """
        max_cut = eh // 3       # deepest cut at inner corner
        min_cut = max_cut // 5  # shallowest cut at outer corner

        t = col / (ew - 1)      # 0.0 … 1.0

        if side == 'L':
            inner_t = 1.0   # inner corner is on the right
        else:
            inner_t = 0.0   # inner corner is on the left

        cut = min_cut + (max_cut - min_cut) * (1.0 - abs(t - inner_t))
        return int(cut)

    def _draw_eye(self, face, ex, side, bh_top, bh_bot):
        ey   = face.EY
        eh   = face.EH
        ew   = face.EW
        ins  = face._ins
        lcd  = face.lcd
        spi  = lcd.spi

        ew3 = ew * 3
        buf = bytearray(ew3)

        lcd.window(ex, ey, ew, eh)
        lcd.start()

        for row in range(eh):
            if row < bh_top or row >= eh - bh_bot:
                buf[:ew3] = _BG * ew
            else:
                inset = ins[row]
                for px in range(ew):
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

    def _draw_sad_mouth(self, face):
        """Draw a sad (frowning) mouth — red rounded rect, corners cut from BOTTOM."""
        x, y = face.MX, face.MY
        w, h = face.MW, face.MH
        r    = face.MR

        # Corner insets — same math as Face._draw_rrect but applied to BOTTOM corners
        ins = [0] * h
        for i in range(r):
            d = r - i - 1
            s = r * r - d * d
            v = r - int(math.sqrt(s)) if s > 0 else r
            ins[h - 1 - i] = v   # only bottom corners rounded

        w3   = w * 3
        erow = _RED * w
        bgb  = _BG * (r + 5)
        buf  = bytearray(w3)
        lcd  = face.lcd

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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, face):
        face.lcd.fill(0, 0, 480, 320, _BG)
        self._draw_eye(face, face.LX, 'L', 0, 0)
        self._draw_eye(face, face.RX, 'R', 0, 0)
        self._draw_sad_mouth(face)
        face.bar.draw_static()

    def tick(self, face):
        pass  # no blinking in angry mode
