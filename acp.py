import argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import threading

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1331
from datetime import datetime, timedelta
from datetime import time as dtTime
from PIL import Image, ImageDraw, ImageFont
import adafruit_tsl2591
import re
import time
import busio
import board
import neopixel_spi as neopixel
import random
import json
import spectra
import sys
import asyncio
import urllib

global httpd
httpd = None
global alarmTime
alarmTime = dtTime.fromisoformat("07:00:00")


#######################################################################################
# LCD INITIALIZATION
##########################################################
# 1. Initialize the SPI interface
# Adjust gpio_DC and gpio_RST pins if you are using custom wiring
serial = spi(device=0, port=0, gpio_DC=24, gpio_RST=25)

# 2. Initialize the SSD1331 display device (Default: 96x64)
device = ssd1331(serial, width=96, height=64, rotate=0)


#######################################################################################
# LED INITIALIZATION
##########################################################
TOTAL_LEDS = 40  # Total number of LEDs to control
spi_bus = busio.SPI(board.SCK_1, MISO=board.MISO_1)
pixels = neopixel.NeoPixel_SPI(spi_bus, TOTAL_LEDS, pixel_order=neopixel.GRB, auto_write=False)


#######################################################################################
# LIGHT SENSOR INITIALIZATION
##########################################################
i2c = board.I2C()
sensor = adafruit_tsl2591.TSL2591(i2c)

class AlarmCLockRequestHandler(BaseHTTPRequestHandler):


    def do_POST(self):
        global alarmTime
        # 1. Determine the size of the incoming data
        content_length = int(self.headers.get('Content-Length', 0))
        
        # 2. Read the body of the request
        post_data = self.rfile.read(content_length)
        
        # 3. Decode the data (assuming utf-8)
        decoded_data = post_data.decode('utf-8')

        # 4. Parse the form encoded data into a dictionary
        # parse_qs converts "name=John&age=30" into {'name': ['John'], 'age': ['30']}
        form_data = urllib.parse.parse_qs(decoded_data)
        print(f"form_data: {form_data}")

        if 'new-time' in form_data:
            newTimeInputString = form_data['new-time'][0]
            regex = r'(?P<HOUR>\d{2}):(?P<MINUTE>\d{2})(?::(?P<SECOND>\d{2}))?'
            match = re.match(regex, newTimeInputString)
            if match is not None:
                hour = int(match.groupdict()['HOUR'])
                minute = int(match.groupdict()['MINUTE'])
                alarmTime = dtTime(hour=hour, minute=minute)
                print(f"new alarm time set to: {alarmTime}")

        # print(f"Received POST request to {self.path}")
        # print(f"Headers:\n{self.headers}")
        # print(f"Body Data:\n{decoded_data}")
        
        # # --- Attempt to parse as JSON if needed ---
        # try:
        #     json_data = json.loads(decoded_data)
        #     response_message = {"status": "success", "received": json_data}
        #     content_type = "application/json"
        #     response_bytes = json.dumps(response_message).encode('utf-8')
        # except json.JSONDecodeError:
        #     # Fallback if it's plain text or form-encoded data
        #     content_type = "text/plain"
        #     response_bytes = f"Received text data: {decoded_data}".encode('utf-8')

        # 4. Send the HTTP response headers
        # 301 = Permanent Redirect, 302 = Temporary Redirect
        self.send_response(301) 
        self.send_header('Location', "/")
        self.end_headers()
        


    def do_GET(self):
        global alarmTime


        # 1. Send the response status code
        self.send_response(200)
        
        # 2. Set headers
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        
        
        # 4. Write the body response
        response_message = '''
        <html>
        <head>
        <title>Alarm Clock Pi</title>
        <style>
        input[type="time"] {
            font-size: 5.5rem; /* Adjust size as needed */
            padding: 0.5rem;
            width: 100%%;
            box-sizing: border-box;
        }
        button[type="submit"] {
            font-size: 5.5rem; /* Adjust size as needed */
            padding: 0.5rem;
            width: 100%%;
            box-sizing: border-box;
        }
        </style>
        </head>
        <body>
        <form action="/change-alarm" method="POST">
        <label for="new-time">Choose Alarm Time:</label>
        <input type="time" id="new-time" name="new-time" value="%s">

        <button type="submit">Submit</button>
        </form>
        </body>
        </html>
        ''' % alarmTime.isoformat()
        self.wfile.write(response_message.encode("utf-8"))


def web_server_loop(port=8080):
    global httpd
    
    server_address = ('', port)
    # Using ThreadingHTTPServer handles each request in a separate thread
    httpd = ThreadingHTTPServer(server_address, AlarmCLockRequestHandler)
    print(f"Starting threaded HTTP server on port {port}...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down http server...")
    finally:
        print("Http Server stopped.")
        httpd.server_close()



async def lcd_loop(task_id: int, delay: float):
    global alarmTime
    timeFont = ImageFont.truetype("arial.ttf", 30)
    ampmFont = ImageFont.truetype("arial.ttf", 10)
    dateFont = ImageFont.truetype("arial.ttf", 14)
    alarmFont = ImageFont.truetype("arial.ttf", 12)
    debugFont = ImageFont.truetype("arial.ttf", 12)

    while True:
        for i in range(0,255):
            # 3. Use canvas context manager to draw shapes and text
            with canvas(device) as draw:

                lux = int(sensor.lux)
                print(f"lux: {lux}")
                # for now hardcoding brightness value
                #i = 60
                i = lux

                whiteMin = 7
                whiteColor = (max(i,whiteMin), max(i,whiteMin), max(i,whiteMin))

                redMin = 14
                redColor = (max(i,redMin), 0, 0)

                blueMin = 14
                blueColor = (0, 0, max(i,blueMin))




                currentDateTime = datetime.now()


                draw.text((0, 25), currentDateTime.strftime("%I:%M"), font=timeFont, fill=whiteColor) # put the text on the image
                draw.text((80, 43), currentDateTime.strftime("%p"), font=ampmFont, fill=whiteColor) # put the text on the image
                draw.text((0, 0), currentDateTime.strftime("%B %m, %Y"), font=ampmFont, fill=blueColor) # put the text on the image
                draw.text((0, 15), alarmTime.strftime("Alarm %I:%M %p"), font=alarmFont, fill=redColor) # put the text on the image

                #draw.text((0, 25), "%s" % i, font=debugFont, fill=whiteColor) # put the text on the image

                await asyncio.sleep(1)



async def led_loop(task_id: int, delay: float):
    global alarmTime

    # start with everything off
    for i in  range(TOTAL_LEDS):
        pixels[i] = (0, 0, 0)
        pixels.show()
    await asyncio.sleep(1)  # Adjust the delay to control the speed


    # This is the defined time for individual steps
    stepTime = 0.1

    # When dim, we want to change one led at a time.  This is the time between individual LED changes
    individualLedTime = 0.5


    expectedMiscTime = 165
    expectedSleepCalls = 2340
    expectedLedSleepCalls = 2400

    expectedRunTime = (expectedSleepCalls*stepTime) + (expectedLedSleepCalls * (stepTime + individualLedTime)) + expectedMiscTime
    time_string = str(timedelta(seconds=expectedRunTime))
    print(f"Expected runtime: {time_string}")


    # This isa list of all of a list of the  r, g, b, sleep time tuples
    rgbTuples = []

    # we first build up the rgb tuples that we want to hit
    firstLightStartColor = spectra.rgb(1, 0, 0) # Deep red
    firstLightEndColor = spectra.rgb(60, 5, 0) # Horizon Glow
    theSunAppearsStartColor = spectra.rgb(120, 30, 0)
    theSunAppearsEndColor = spectra.rgb(255, 80, 10)
    risingSunStartColor = spectra.rgb(255, 150, 50)
    risingSunEndColor = spectra.rgb(255, 200, 100)
    fullSunStartColor = spectra.rgb(255, 240, 220)
    fullSunEndColor = spectra.rgb(255, 255, 255)
    my_scale = spectra.scale([firstLightStartColor, 
                            firstLightEndColor, 
                            theSunAppearsStartColor, 
                            theSunAppearsEndColor,
                            risingSunStartColor,
                            risingSunEndColor,
                            fullSunStartColor, 
                            fullSunEndColor,
                            ])
    my_range = my_scale.range(2400)

    ###############################
    ## DEBUG VALUES
    # stepTime = 0.001
    # my_range = my_scale.range(500)
    # individualLedTime = 0.01

    # next, for some of the dimmer transitions, we want to have it toggle individual leds to ensure a cleaner transition

    lastColor = spectra.rgb(0, 0, 0)
    for i, colorRGB in enumerate(my_range):
        lr, lg, lb = lastColor.rgb
        r, g, b = colorRGB.rgb
        #print("%s, %s" % (i, colorRGB.rgb))
        rgbs = []
        for pixel in  range(TOTAL_LEDS):
            sleepTime = 0
            if pixel == TOTAL_LEDS-1:
                sleepTime = stepTime
            if (lr < 20 and lr < int(r)) or \
                (lg < 20 and lg < int(g)) or \
                (lb < 20 and lb < int(b)):
                sleepTime = stepTime+individualLedTime

            rgbs.append((r, g, b, sleepTime))
        rgbTuples.append(rgbs)

        lastColor = spectra.rgb(int(r), int(g), int(b))

    # for i, rgbList in enumerate(rgbTuples):
    #     for j, (r,g,b,s) in enumerate(rgbList):
    #         print(f"{i}:{j}     r: {r}   g: {g}   b: {b}   s: {s}")


    #alarmTime = dtTime.fromisoformat("22:46:00")
    while True:
        now = datetime.now().time()
        if alarmTime.hour != now.hour or alarmTime.minute != now.minute:
            print(f"now: {now} is not the correct time to start")
            await asyncio.sleep(1)
        else:
            print(f"now: {now} is the correct time to start.  STarting Cycle")
            doneWithCycle = False
            # Having computed all of the steps, just go through and do them.
            while not doneWithCycle:
                cycleStartTime = datetime.now()
                standardStepCalls = 0
                ledStepCalls = 0
                standardSleepDuration = 0
                ledSleepDuration = 0
                for i, rgbList in enumerate(rgbTuples):
                    for j, (r,g,b,s) in enumerate(rgbList):
                        #print(f"{i}:{j}     r: {r}   g: {g}   b: {b}   s: {s}")
                        pixels[j] = (r, g, b)
                        pixels.show()
                        if s > 0:
                            await asyncio.sleep(s)  # Adjust the delay to control the speed
                            if s == stepTime:
                                standardStepCalls += 1
                                standardSleepDuration += s
                            elif s == stepTime+individualLedTime:
                                ledStepCalls += 1
                                ledSleepDuration += s
                cycleEndTime = datetime.now()
                cycleTimeDuration = cycleEndTime - cycleStartTime
                print(f"Sleep Calls: {standardStepCalls}")
                print(f"led Sleep Calls: {ledStepCalls}")
                print(f"Sleep Duration: {standardSleepDuration}")
                print(f"led Sleep Duration: {ledSleepDuration}")
                print(f"Cycle Duration (seconds): {cycleTimeDuration.total_seconds()}")

                while True:
                    td = datetime.now() - cycleEndTime
                    secondsToRemainAtFullBrightness = 60
                    if td.seconds < secondsToRemainAtFullBrightness:
                        # sleep until a button is pressed
                        await asyncio.sleep(1)
                    else:
                        doneWithCycle = True
                        for i in  range(TOTAL_LEDS):
                            pixels[i] = (0, 0, 0)
                            pixels.show()
                        break






async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(lcd_loop(1, 1.0))
            t2 = tg.create_task(led_loop(2, 0.5))
            t3 = tg.create_task(asyncio.to_thread(web_server_loop))
        print(f"Results: {t1.result()}, {t2.result()}, {t3.result()}")

    except asyncio.CancelledError as ex:
        print("Process Cancelled (Likely sigint, sigterm, or sigkill)")
        for pixel in  range(TOTAL_LEDS):
            pixels[pixel] = (0, 0, 0)
        pixels.show()
    finally:
        global httpd
        if httpd is not None:
            print("Http Server shutdown.")
            httpd.shutdown()
            httpd = None











if __name__ == "__main__":
    asyncio.run(main())