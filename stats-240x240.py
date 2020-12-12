# -*- coding: utf-8 -*-
# Import Python System Libraries
import time
import json
import subprocess

# Import Requests Library
import requests

#Import Blinka
import digitalio
import board

# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789

api_url = 'http://localhost/admin/api.php'

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max = 24mhz, Pi can do better!):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 180

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
disp.image(image, rotation)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding

# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 23)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()


# Add buttons as inputs
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


while True:
    
    if buttonA.value and buttonB.value:  # no buttons pressed
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        backlight.value = False  # turn off backlight
    else:
        # Shell scripts for system monitoring from here:
        # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = "IP: "+subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "hostname | tr -d \'\\n\'"
        HOST = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"%s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'" 
        # pylint: disable=line-too-long
        Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        
        # Pi Hole data!
        try:
            r = requests.get(api_url)
            data = json.loads(r.text)
            DNSQUERIES = data['dns_queries_today']
            ADSBLOCKED = data['ads_blocked_today']
            CLIENTS = data['unique_clients']
            STATUS = data['status'] 
        except KeyError:
            time.sleep(1)
            continue

    y = top
    
    
    if buttonA.value and not buttonB.value:  # just button B pressed
        draw.rectangle((0, 0, width, height), outline=0, fill=(15, 25, 40))
        backlight.value = True
        draw.text((x, y), IP, font=font, fill="#F4FCF8")
        y += font.getsize(IP)[1]
        draw.text((x, y), HOST, font=font, fill="#F4FCF8")
        y += font.getsize(HOST)[1]
        draw.text((x, y), CPU, font=font, fill="#F4FCF8")
        y += font.getsize(CPU)[1]
        draw.text((x, y), "Memory:", font=font, fill="#DEF8EB")
        y += font.getsize(MemUsage)[1]
        draw.text((x, y), MemUsage, font=font, fill="#B3EFD1")
        y += font.getsize(MemUsage)[1]
        draw.text((x, y), Disk, font=font, fill="#A8EDCB")
        y += font.getsize(Disk)[1]
        draw.text((x, y), Temp, font=font, fill="#93E9BE")
        y += font.getsize(Disk)[1]
        draw.text((x, y), "DNS Queries: {}".format(DNSQUERIES), font=font, fill="#93E9BE")
    
    elif buttonB.value and not buttonA.value:  # just button A pressed
        draw.rectangle((0, 0, width, height), outline=0, fill=(15, 25, 40))
        backlight.value = True
        draw.text((x, y), IP, font=font, fill="#CCEEF9")
        y += font.getsize(IP)[1]
        draw.text((x, y), HOST, font=font, fill="#CCEEF9")
        y += font.getsize(HOST)[1]
        draw.text((x, y), "Status: {}".format(str(STATUS)), font=font, fill="#B6E6F6")
        y += font.getsize(str(STATUS))[1]
        draw.text((x, y), "Ads Blocked: {}".format(str(ADSBLOCKED)), font=font, fill="#B6E6F6")
        y += font.getsize(str(ADSBLOCKED))[1]
        draw.text((x, y), "DNS Queries: {}".format(str(DNSQUERIES)), font=font, fill="#B6E6F2")
        y += font.getsize(str(DNSQUERIES))[1]
        draw.text((x, y), CPU, font=font, fill="#6FCEED")
        y += font.getsize(CPU)[1]
        draw.text((x, y), "Memory:", font=font, fill="#3FBEE7")
        y += font.getsize(MemUsage)[1]
        draw.text((x, y), MemUsage, font=font, fill="#0CADE1")
        y += font.getsize(MemUsage)[1]
        draw.text((x, y), Disk, font=font, fill="#009DD8")
        y += font.getsize(Disk)[1]
        draw.text((x, y), Temp, font=font, fill="#008ECE")

    elif not buttonB.value and not buttonA.value:  # both buttons pressed
        draw.rectangle((0, 0, width, height), outline=0, fill=(15, 25, 40))
        backlight.value = True
        draw.text((x, y), IP, font=font, fill="#DAF0FF")
        y += font.getsize(IP)[1]
        draw.text((x, y), HOST, font=font, fill="#B5E2FF")
        y += font.getsize(HOST)[1]
        draw.text((x, y), "Ads Blocked: {}".format(str(ADSBLOCKED)), font=font, fill="#8FD3FE")
        y += font.getsize(str(ADSBLOCKED))[1]
        draw.text((x, y), "Clients: {}".format(str(CLIENTS)), font=font, fill="#6AC5FE")
        y += font.getsize(str(CLIENTS))[1]
        draw.text((x, y), "DNS Queries: {}".format(str(DNSQUERIES)), font=font, fill="#45B6FE")
        y += font.getsize(str(DNSQUERIES))[1]
    
    else:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        backlight.value = False

    # Display image.
    disp.image(image, rotation)
    time.sleep(.1)
