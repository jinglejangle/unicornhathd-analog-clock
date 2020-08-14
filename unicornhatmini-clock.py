#!/usr/bin/env python3
""" Analog clock for unicornhatmini """ 
import time
import sys
import subprocess 

from gpiozero import Button
from signal import pause

from colorsys import hsv_to_rgb
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini

import PIL
import PIL.Image as Image ,PIL.ImageDraw as ImageDraw


clockMode="analog"
analogClockStyleToggle=0

def getClockContent(): 
    global clockMode
    if clockMode == "clock": 
        now = datetime.now()
        ttext = now.strftime("%-I:%M") 

    if clockMode == "pihole": 
        #for line in runProcess('tail  /var/log/pihole.log '.split()):
        for line in runProcess('tail  /var/log/messages '.split()):
            tttext = str(line.decode('utf-8'))
            if(tttext != ""):
                    ttext=tttext; 

    if clockMode == "analog": 
        ttext=""

    if clockMode == "blank": 
        ttext=""

    return ttext

def pressed(button):
    global clockMode, analogClockStyleToggle
    button_name = button_map[button.pin.number]
    print(f"Button {button_name} pressed!")
    if button_name == "A" :
        print(f"clock mode")
        clockMode="clock"   
    if button_name == "B" : 
        print(f"pihole mode")
        clockMode="pihole"
        text = getClockContent()

    if button_name == "X" : 
        print(f"analog mode")
        clockMode="analog"
        text = getClockContent()
    
    if button_name == "Y" : 
        if clockMode == "analog" : 
            analogClockStyleToggle = not analogClockStyleToggle
        else: 
            print(f"blank mode")
            clockMode="blank"
            text = "" # getClockContent()


button_map = {5: "A",
              6: "B",
              16: "X",
              24: "Y"}

button_a = Button(5)
button_b = Button(6)
button_x = Button(16)
button_y = Button(24)

try:
    button_a.when_pressed = pressed
    button_b.when_pressed = pressed
    button_x.when_pressed = pressed
    button_y.when_pressed = pressed


except KeyboardInterrupt:
    button_a.close()
    button_b.close()
    button_x.close()
    button_y.close()



text = ""

def runProcess(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            break


unicornhatmini = UnicornHATMini()

rotation = 180
if len(sys.argv) > 1:
    try:
        rotation = int(sys.argv[1])
    except ValueError:
        print("Usage: {} <rotation>".format(sys.argv[0]))
        sys.exit(1)

unicornhatmini.set_rotation(rotation)
display_width, display_height = unicornhatmini.get_shape()

# Do not look at unicornhatmini with remaining eye
unicornhatmini.set_brightness(0.9)

# Load a nice 5x7 pixel font
# Granted it's actually 5x8 for some reason :| but that doesn't matter
font = ImageFont.truetype("5x7.ttf", 8)

text = getClockContent()
text_width, text_height = font.getsize(text) 
# Measure the size of our text, we only really care about the width for the moment
# but we could do line-by-line scroll if we used the height
text_width, text_height = font.getsize(text)

# Create a new PIL image big enough to fit the text
image = Image.new('P', (text_width + display_width + display_width, display_height), 0)
draw = ImageDraw.Draw(image)

# Draw the text into the image
draw.text((display_width, -1), text, font=font, fill=255)

offset_x = 0



while True:

    text_width, text_height = font.getsize(text) 







    if clockMode == "analog" : 

        finalimage = Image.new('RGBA', (17, 7)) 

        image = Image.new('RGBA', (7, 7)) 
        draw = ImageDraw.Draw(image) 

        if analogClockStyleToggle: 
            draw.ellipse((0,0,7,7), fill = 'white' , outline='white' )
        else:
            draw.ellipse((0,0,7,7), fill = 'black' , outline='white' )

        draw.point((3,3), fill='white')


        h = int(time.strftime("%I"))
        m = int(time.strftime("%M"))
        s = int(time.strftime("%s"))


        angle = (h/12) * 360
        if m > 15 :
            angle +=5
        if m > 30 :
            angle +=5
        if m > 45 :
            angle +=5



        #print("h is hour angle is : " + str(angle)) 

        himage = Image.new('RGBA', (7, 7)) 
        hdraw = ImageDraw.Draw(himage) 
        hdraw.rectangle((3,3,5,3), fill='blue')
        himage = himage.rotate(-angle+90, PIL.Image.NEAREST, expand=0)

        angle = (m/60) * 360
        #fixme theres a better way this boosts itself when it shouldnt 
        if m > 15 :
            angle +=5
        if m > 30 :
            angle +=5
        if m > 45 :
            angle +=5



        mimage = Image.new('RGBA', (7, 7)) 
        mdraw = ImageDraw.Draw(mimage) 
        mdraw.rectangle((3,3,13,3), fill='red')
        mimage = mimage.rotate(-angle+90, PIL.Image.NEAREST, expand=0)


        #The display really is too small for a second hand to go around 
        angle = (s/60) * 360
        if s > 15 :
            angle +=5
        if s > 30 :
            angle +=5
        if s > 45 :
            angle +=5


        simage = Image.new('RGBA', (7, 7)) 
        sdraw = ImageDraw.Draw(simage) 
        sdraw.rectangle((3,3,11,3), fill='yellow')
        simage = simage.rotate(-angle+90, PIL.Image.NEAREST, expand=0)





        image.paste(simage, (0,0), simage)
        image.paste(mimage, (0,0), mimage)
        image.paste(himage, (0,0), himage)

        finalimage.paste(image, (5,0), image)
        image = finalimage

        now = datetime.now()
        text = now.strftime("%H%M") 
        text = now.strftime("%-I:%M") 
        seconds = now.strftime("%S")

        #draw = ImageDraw.Draw(image)
        display_width,display_height = image.size
        for y in range(display_height):
            for x in range(display_width):
                hue = (time.time() / 10.0) + (x / float(display_width * 2))
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                try: 
                    xc = image.getpixel((x + offset_x, y)) 
                    xr =int(xc[0])
                    xg =int(xc[1])
                    xb =int(xc[2])

                    #if xr < 255  and  xb < 255 and xg < 255:
                    if xr == 0  and xg == 0 and xb == 0 :
                        unicornhatmini.set_pixel(x, y, 0, 0, 0)

                    elif xb > 0  and xr < 255:
                        # hour hand
                        unicornhatmini.set_pixel(x, y, 0, 255, 155)

                    elif xr == 255  and xg == 255 and xb == 255 :
                        # outside the clock  
                        unicornhatmini.set_pixel(x, y, r, g, b)

                    else:
                        # second hand and all remaining non black or white color   
                        unicornhatmini.set_pixel(x, y, xr, xg, xb)

                except IndexError:
                    #unicornhatmini.set_pixel(x, y, 0, 0, 0)
                    offset_x = 0

        offset_x += 1

        if offset_x + display_width > image.size[0]:
            offset_x = 0

        unicornhatmini.show()



    else:
        # Create a new PIL image big enough to fit the text
        image = Image.new('P', (text_width + display_width + display_width, display_height), 0)
        draw = ImageDraw.Draw(image)

        # Draw the text into the image
        draw.text((display_width, -1), text, font=font, fill=255)

        

        now = datetime.now()
        seconds = now.strftime("%S")



        for y in range(display_height):
            for x in range(display_width):
                hue = (time.time() / 10.0) + (x / float(display_width * 2))
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                try: 
                    if image.getpixel((x + offset_x, y)) == 255:
                        unicornhatmini.set_pixel(x, y, r, g, b)
                    else:
                        unicornhatmini.set_pixel(x, y, 0, 0, 0)
                except IndexError:
                    unicornhatmini.set_pixel(x, y, 0, 0, 0)
                    offset_x = 0

                if clockMode == "clock" :
                    for k in range(int(int(seconds)/3.529)):
                        unicornhatmini.set_pixel(int(k), 6, r, g, b)

                    unicornhatmini.set_pixel(int(int(seconds)/3.529), 6, r, g, b)

        offset_x += 1

        if offset_x + display_width > image.size[0]:
            offset_x = 0
            text = getClockContent()

        text_width, text_height = font.getsize(text) 
        unicornhatmini.show()

        if clockMode == "clock" : 

            text = getClockContent()
            text_width, text_height = font.getsize(text) 
            time.sleep(0.08)
        if clockMode == "pihole" : 
            time.sleep(0.005)
        if clockMode == "analog" : 
            time.sleep(1)
        

wn.mainloop()
