import argparse
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1331
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

import time
import busio
import board
import neopixel_spi as neopixel
import random
import spectra
import sys
import asyncio




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




async def lcd_loop(task_id: int, delay: float):
    while True:
        for i in range(0,255):
            # 3. Use canvas context manager to draw shapes and text
            with canvas(device) as draw:
                # Draw a dark blue background rectangle spanning the bounding box
                #draw.rectangle(device.bounding_box, outline="black", fill=(0, 0, 50))
                
                # Draw a red rectangle frame
                #draw.rectangle((5, 5, 90, 58), outline="red", fill=None)
                
                # Draw a solid yellow circle
                #draw.ellipse((10, 15, 30, 35), fill="yellow", outline="orange")
                
                # Write white text 
                #draw.text((40, 25), "Hello!", fill=(10, 10, 10))
                #draw.text((40, 25), "Hello!", fill=(255, 255, 255))

                whiteMin = 7
                whiteColor = (max(i,whiteMin), max(i,whiteMin), max(i,whiteMin))

                redMin = 14
                redColor = (max(i,redMin), 0, 0)

                blueMin = 14
                blueColor = (0, 0, max(i,blueMin))

                date_string = "2026-12-03 00:45:30"
                format_string = "%Y-%m-%d %H:%M:%S"

                alarm_string = "2026-12-03 00:45:30"
                format_string = "%Y-%m-%d %H:%M:%S"


                currentDateTime = datetime.strptime(date_string, format_string)
                timeFont = ImageFont.truetype("arial.ttf", 30)
                ampmFont = ImageFont.truetype("arial.ttf", 10)
                dateFont = ImageFont.truetype("arial.ttf", 14)
                alarmFont = ImageFont.truetype("arial.ttf", 12)
                debugFont = ImageFont.truetype("arial.ttf", 12)


                draw.text((0, 25), currentDateTime.strftime("%I:%M"), font=timeFont, fill=whiteColor) # put the text on the image
                draw.text((80, 43), currentDateTime.strftime("%p"), font=ampmFont, fill=whiteColor) # put the text on the image
                draw.text((0, 0), currentDateTime.strftime("%B %m, %Y"), font=ampmFont, fill=blueColor) # put the text on the image
                draw.text((0, 15), currentDateTime.strftime("Alarm %I:%M %p"), font=alarmFont, fill=redColor) # put the text on the image

                draw.text((0, 25), "%s" % i, font=debugFont, fill=whiteColor) # put the text on the image

                await asyncio.sleep(1)



async def led_loop(task_id: int, delay: float):

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

    # Having computed all of the steps, just go through and do them.
    while True:
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






async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(lcd_loop(1, 1.0))
            t2 = tg.create_task(led_loop(2, 0.5))
        print(f"Results: {t1.result()}, {t2.result()}")

    except asyncio.CancelledError as ex:
        print("Process Cancelled (Likely sigint, sigterm, or sigkill)")
        for pixel in  range(TOTAL_LEDS):
            pixels[pixel] = (0, 0, 0)
        pixels.show()








if __name__ == "__main__":
    asyncio.run(main())