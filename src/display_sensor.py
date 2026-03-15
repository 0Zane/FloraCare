"""
Display sensor data (DHT11 temp/humidity + soil moisture) on the 170x320 SPI screen.
Panel is always used HORIZONTAL (landscape): 320 pixels wide x 170 pixels tall.
"""
import time
import dht
from machine import Pin, SPI, ADC
import st7789

# --- 170x320 panel: physical size 170 x 320; we use it HORIZONTAL (landscape) ---
# Rotation 1 = landscape -> logical size 320 (width) x 170 (height)
DISPLAY_PHYS_W = 170
DISPLAY_PHYS_H = 320
ROTATION_LANDSCAPE = 1  # horizontal: long side (320) is width

# Full usable area in landscape (320 x 170)
CONTENT_W = 320
CONTENT_H = 170

# --- Display pins: CS 10, DC 14, MOSI/SDA 11, SCK 12, BLK 13 (not 21/22) ---
SCK = 12
MOSI = 11
DC = 14
CS = 10
RES = 9
BLK = 13
# Sensors
DHT_PIN = 15
SOIL_PIN = 18
# Onboard LED (GPIO 2 on most ESP32-S3 dev boards; 1 = off if active-low)
LED_ONBOARD_PIN = 2

# --- Minimal 8x8 font: space, 0-9, . : ° % C T e m p H u S o i l (8 bytes per char) ---
_FONT_8x8 = {
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    "0": (0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C, 0x00),
    "1": (0x08, 0x18, 0x08, 0x08, 0x08, 0x08, 0x1C, 0x00),
    "2": (0x3C, 0x42, 0x02, 0x0C, 0x30, 0x40, 0x7E, 0x00),
    "3": (0x3C, 0x42, 0x02, 0x1C, 0x02, 0x42, 0x3C, 0x00),
    "4": (0x04, 0x0C, 0x14, 0x24, 0x7E, 0x04, 0x04, 0x00),
    "5": (0x7E, 0x40, 0x7C, 0x02, 0x02, 0x42, 0x3C, 0x00),
    "6": (0x3C, 0x40, 0x7C, 0x42, 0x42, 0x42, 0x3C, 0x00),
    "7": (0x7E, 0x02, 0x04, 0x08, 0x10, 0x10, 0x10, 0x00),
    "8": (0x3C, 0x42, 0x42, 0x3C, 0x42, 0x42, 0x3C, 0x00),
    "9": (0x3C, 0x42, 0x42, 0x42, 0x3E, 0x02, 0x3C, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18, 0x00),
    ":": (0x00, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00, 0x00),
    "\xb0": (0x38, 0x44, 0x44, 0x38, 0x00, 0x00, 0x00, 0x00),  # degree
    "%": (0x62, 0x92, 0x64, 0x08, 0x13, 0x23, 0x00, 0x00),
    "C": (0x3C, 0x42, 0x40, 0x40, 0x40, 0x42, 0x3C, 0x00),
    "T": (0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00),
    "e": (0x00, 0x3C, 0x42, 0x7E, 0x40, 0x42, 0x3C, 0x00),
    "m": (0x00, 0x76, 0x49, 0x49, 0x49, 0x41, 0x00, 0x00),
    "p": (0x00, 0x7C, 0x42, 0x42, 0x7C, 0x40, 0x40, 0x00),
    "H": (0x42, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x42, 0x00),
    "u": (0x00, 0x42, 0x42, 0x42, 0x46, 0x3A, 0x00, 0x00),
    "S": (0x3C, 0x42, 0x40, 0x3C, 0x02, 0x42, 0x3C, 0x00),
    "o": (0x00, 0x3C, 0x42, 0x42, 0x42, 0x42, 0x3C, 0x00),
    "i": (0x00, 0x08, 0x00, 0x08, 0x08, 0x08, 0x1C, 0x00),
    "l": (0x00, 0x18, 0x08, 0x08, 0x08, 0x08, 0x1C, 0x00),
}


def _pack_8x8_to_r565(glyph, fg, bg):
    """Turn 8x8 1bpp glyph (8 bytes) into 8*8*2 bytes RGB565 for blit_buffer."""
    buf = bytearray(8 * 8 * 2)
    fg_hi, fg_lo = fg >> 8, fg & 0xFF
    bg_hi, bg_lo = bg >> 8, bg & 0xFF
    i = 0
    for row in glyph:
        for bit in range(7, -1, -1):
            if (row >> bit) & 1:
                buf[i], buf[i + 1] = fg_hi, fg_lo
            else:
                buf[i], buf[i + 1] = bg_hi, bg_lo
            i += 2
    return buf


def draw_string(display, x, y, s, fg=st7789.WHITE, bg=st7789.BLACK):
    """Draw string at (x,y) using 8x8 font. Clips to content area."""
    for c in s:
        if x + 8 > CONTENT_W or y + 8 > CONTENT_H:
            break
        glyph = _FONT_8x8.get(c, _FONT_8x8[" "])
        buf = _pack_8x8_to_r565(glyph, fg, bg)
        display.blit_buffer(buf, x, y, 8, 8)
        x += 8


def _draw_card_static(display, x, y, w, h, label, border_c, fill_c):
    """Draw card frame and label only (call once)."""
    if y + h > CONTENT_H or w <= 0 or h <= 0:
        return
    display.rect(x, y, w, h, border_c)
    display.fill_rect(x + 1, y + 1, w - 2, h - 2, fill_c)
    draw_string(display, x + 4, y + 4, label + ":", st7789.color565(180, 180, 180), fill_c)


def _update_value(display, x, y, w_px, h_px, s, fg, bg):
    """Clear a value region and draw string (w_px = max width in pixels, 8px per char)."""
    display.fill_rect(x, y, w_px, h_px, bg)
    draw_string(display, x, y, s, fg, bg)


def _update_bar(display, x, y, w, h, pct, bg_c, fill_c):
    """Draw bar 0..100% (only the bar area)."""
    if y + h > CONTENT_H or w <= 0:
        return
    display.fill_rect(x, y, w, h, bg_c)
    fill_w = max(0, min(w, (w * pct) // 100))
    if fill_w > 0:
        display.fill_rect(x, y, fill_w, h, fill_c)


def get_sensor_data():
    """Read DHT11 on DHT_PIN; return (temp, humidity) or (None, None) on error."""
    try:
        sensor = dht.DHT11(Pin(DHT_PIN))
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        if t is not None and h is not None:
            return (t, h)
    except Exception:
        pass
    return (None, None)


def read_soil():
    """Read soil moisture from ADC on SOIL_PIN; return (raw, moisture_pct)."""
    try:
        adc = ADC(Pin(SOIL_PIN))
        adc.atten(ADC.ATTN_11DB)
        raw = adc.read_u16()
        moisture_pct = max(0, min(100, 100 - (raw * 100 // 65535)))
        return (raw, moisture_pct)
    except Exception:
        return (None, None)


def main():
    # Turn off onboard LED (active-low: 1 = off)
    try:
        led = Pin(LED_ONBOARD_PIN, Pin.OUT, value=1)
    except Exception:
        pass
    spi = SPI(1, baudrate=40_000_000, mosi=Pin(MOSI), sck=Pin(SCK))
    dc = Pin(DC, Pin.OUT)
    rst = Pin(RES, Pin.OUT) if RES >= 0 else None
    cs = Pin(CS, Pin.OUT) if CS >= 0 else None
    bl = Pin(BLK, Pin.OUT) if BLK >= 0 else None

    # Driver has built-in 170x320 with xstart/ystart offsets to avoid left/bottom garbage
    display = st7789.ST7789(
        spi,
        width=DISPLAY_PHYS_W,
        height=DISPLAY_PHYS_H,
        dc=dc,
        reset=rst,
        cs=cs,
        backlight=bl,
        rotation=ROTATION_LANDSCAPE,
    )

    w, h = display.width, display.height
    if bl:
        bl.value(1)

    # Colors (driver has color565 for custom)
    bg = st7789.BLACK
    panel_bg = st7789.color565(28, 32, 40)
    border = st7789.color565(60, 68, 80)
    temp_color = st7789.CYAN
    hum_color = st7789.GREEN
    soil_color = st7789.YELLOW
    bar_bg = st7789.color565(40, 44, 52)
    bar_fill = st7789.color565(0, 180, 120)

    # Layout
    pad = 8
    card_w = CONTENT_W - 2 * pad
    card_h = 36
    title_h = 22
    value_x = pad + 10
    value_y_off = 14
    bar_y_off = 26
    bar_w = card_w - 20
    bar_h = 6
    value_w_px = 10 * 8   # max 10 chars for value (e.g. "--- \xb0C" / "100 %")
    value_h_px = 8

    card1_y = pad + title_h
    card2_y = card1_y + card_h + pad
    card3_y = card2_y + card_h + pad

    # One-time: clear screen and draw static UI (title + card frames + labels)
    display.fill(bg)
    display.fill_rect(0, 0, CONTENT_W, title_h + pad, border)
    display.fill_rect(2, 2, CONTENT_W - 4, title_h + pad - 4, panel_bg)
    draw_string(display, pad, 6, "TNSI Sensors", st7789.WHITE, panel_bg)
    _draw_card_static(display, pad, card1_y, card_w, card_h, "Temp", border, panel_bg)
    _draw_card_static(display, pad, card2_y, card_w, card_h, "Hum", border, panel_bg)
    _draw_card_static(display, pad, card3_y, card_w, card_h, "Soil", border, panel_bg)

    # Initial placeholders so value areas are not empty before first read
    _update_value(display, value_x, card1_y + value_y_off, value_w_px, value_h_px, "-- \xb0C", temp_color, panel_bg)
    _update_value(display, value_x, card2_y + value_y_off, value_w_px, value_h_px, "-- %", hum_color, panel_bg)
    _update_value(display, value_x, card3_y + value_y_off, value_w_px, value_h_px, "-- %", soil_color, panel_bg)
    _update_bar(display, value_x, card2_y + bar_y_off, bar_w, bar_h, 0, bar_bg, bar_fill)
    _update_bar(display, value_x, card3_y + bar_y_off, bar_w, bar_h, 0, bar_bg, bar_fill)

    last_temp, last_hum, last_soil = None, None, None
    dht_interval_ms = 2000
    last_dht_ms = 0

    while True:
        t_ms = time.ticks_ms()
        if time.ticks_diff(t_ms, last_dht_ms) >= dht_interval_ms:
            temp, hum = get_sensor_data()
            last_dht_ms = t_ms
        else:
            temp, hum = last_temp, last_hum
        _, soil_pct = read_soil()

        if temp != last_temp:
            t_str = (str(temp) + " \xb0C") if temp is not None else "-- \xb0C"
            _update_value(display, value_x, card1_y + value_y_off, value_w_px, value_h_px, t_str, temp_color, panel_bg)
            last_temp = temp

        if hum != last_hum:
            h_str = (str(hum) + " %") if hum is not None else "-- %"
            _update_value(display, value_x, card2_y + value_y_off, value_w_px, value_h_px, h_str, hum_color, panel_bg)
            if hum is not None and 0 <= hum <= 100:
                _update_bar(display, value_x, card2_y + bar_y_off, bar_w, bar_h, hum, bar_bg, bar_fill)
            last_hum = hum

        if soil_pct != last_soil:
            s_str = (str(soil_pct) + " %") if soil_pct is not None else "-- %"
            _update_value(display, value_x, card3_y + value_y_off, value_w_px, value_h_px, s_str, soil_color, panel_bg)
            if soil_pct is not None and 0 <= soil_pct <= 100:
                _update_bar(display, value_x, card3_y + bar_y_off, bar_w, bar_h, soil_pct, bar_bg, bar_fill)
            last_soil = soil_pct

        time.sleep_ms(350)


if __name__ == "__main__":
    main()
