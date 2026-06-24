pico code
from machine import Pin, I2C
import network
import urequests
import framebuf
import time

# =========================
# OLED DRIVER
# =========================

class SSD1306_I2C:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr

        self.buffer = bytearray(self.height * self.width // 8)
        self.fb = framebuf.FrameBuffer(
            self.buffer,
            self.width,
            self.height,
            framebuf.MONO_VLSB
        )

        self.init_display()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x80, cmd]))

    def init_display(self):
        cmds = [
            0xAE,
            0x20, 0x00,
            0x40,
            0xA1,
            0xC8,
            0x81, 0xFF,
            0xA6,
            0xA8, 0x3F,
            0xD3, 0x00,
            0xD5, 0x80,
            0xD9, 0xF1,
            0xDA, 0x12,
            0xDB, 0x40,
            0x8D, 0x14,
            0xAF
        ]

        for c in cmds:
            self.write_cmd(c)

    def fill(self, color):
        self.fb.fill(color)

    def text(self, string, x, y):
        self.fb.text(string, x, y)

    def show(self):
        self.write_cmd(0x21)
        self.write_cmd(0)
        self.write_cmd(self.width - 1)

        self.write_cmd(0x22)
        self.write_cmd(0)
        self.write_cmd(self.height // 8 - 1)

        self.i2c.writeto(self.addr, b'\x40' + self.buffer)

# =========================
# WIFI
# =========================

SSID = "wifi name"
PASSWORD = "your password"

# =========================
# API
# =========================

API_URL = "your_url"

# =========================
# OLED
# SDA -> GP0
# SCL -> GP1
# =========================

i2c = I2C(
    0,
    scl=Pin(1),
    sda=Pin(0),
    freq=400000
)

oled = SSD1306_I2C(
    128,
    64,
    i2c
)

# =========================
# RELAY
# IN -> GP15
# =========================

relay = Pin(15, Pin.OUT)

# =========================
# DISPLAY
# =========================

def show_screen(status, ip):

    oled.fill(0)

    oled.text("Hi Welcome", 10, 0)

    oled.text("IP:", 0, 18)
    oled.text(ip, 0, 28)

    oled.text("Relay:", 0, 50)
    oled.text(status, 60, 50)

    oled.show()

# =========================
# STARTUP
# =========================

oled.fill(0)
oled.text("Hi Welcome", 10, 0)
oled.text("Connecting...", 0, 20)
oled.show()

# =========================
# CONNECT WIFI
# =========================

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    time.sleep(1)

ip = wifi.ifconfig()[0]

oled.fill(0)
oled.text("WiFi Connected", 0, 0)
oled.text(ip, 0, 20)
oled.show()

time.sleep(3)

# =========================
# LOOP
# =========================

while True:

    try:

        r = urequests.get(API_URL)
        data = r.json()
        r.close()

        relay_state = data.get("relay", "off")

        if relay_state == "on":
            relay.value(1)
            show_screen("ON", ip)

        else:
            relay.value(0)
            show_screen("OFF", ip)

    except Exception as e:

        print("ERROR:", e)

        relay.value(0)

        oled.fill(0)
        oled.text("Hi Welcome", 10, 0)
        oled.text("API ERROR", 0, 20)
        oled.text(ip, 0, 40)
        oled.show()

    time.sleep(2)




