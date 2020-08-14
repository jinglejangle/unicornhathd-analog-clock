#!/usr/bin/env python3
import time
import math
import sys
import subprocess 
import threading

from signal import pause

from colorsys import hsv_to_rgb
from datetime import datetime
import numpy
import itertools

from PIL import Image, ImageDraw, ImageFont, ImageOps
import unicornhathd 

import PIL
import PIL.Image as Image ,PIL.ImageDraw as ImageDraw


try:

    class ThreadJob(threading.Thread):
        def __init__(self,callback,event,interval):
            try:
                self.callback = callback
                self.event = event
                self.interval = interval
                super(ThreadJob,self).__init__()
            except KeyboardInterrupt:
                pass

        def run(self):
                while not self.event.wait(self.interval):
                    self.callback()


    class unicornClock:

        clockStyle=0
        clockWidth=16
        clockHeight=16
        image = 0 
        draw = 0 
        clockface = None 
        hourhand=None
        minhand=None
        sechand=None

        rising = range(1, 400, 1)    # [1...9]
        falling = range(400, 0, -1)  # [10...1]
        # Join the ranges together
        pattern = (rising,  falling)
        brightness_levels = list(itertools.chain.from_iterable(pattern))
        brightness_delay=0.005

        def __init__(self,  clockWidth=16, clockHeight=16, clockStyle=0, pulseBrightness=1): 
            self.image = Image.new('RGBA', (self.clockWidth, self.clockHeight)) 
            self.clockWidth = clockWidth
            self.clockHeight = clockHeight
            self.clockStyle = clockStyle

            #handle brightness
            self.brightness = self.brightness_levels.pop()
            self.brightness_levels = [self.brightness] + self.brightness_levels
            if pulseBrightness == 0: 
                self.brightness=10
                self.brightness_levels = [self.brightness]
            else:
                try: 
                    event = threading.Event()
                    k = ThreadJob(self.pulse,event,self.brightness_delay)
                    k.start()
                except KeyboardInterrupt:
                    pass
                    
 
        def pulse(self): 
            self.brightness_levels = [self.brightness*10] + self.brightness_levels
            self.brightness = self.brightness_levels.pop()/10


                

        def runClock(self):
           self.createHourHand()    
           self.createMinHand()    
           self.createSecondHand()    
           self.sendToUnicornHat()    
           self.compositeClock()    

        def set_interval(self,func,time):
            e = threading.Event()
            while not e.wait(time):
                self.pulse()


        def getTime(self): 
            self.h = int(time.strftime("%I"))
            self.m = int(time.strftime("%M"))
            self.s = int(time.strftime("%s"))

        def getHandAngle(self,h,i): 

            self.angle = (h/12) * 360
            if m > 15 :
                angle +=5
            if m > 30 :
                angle +=5
            if m > 45 :
                angle +=5



        def createClockFace(self): 

            # outer ring 
            image = Image.new('RGBA', (self.clockWidth, self.clockHeight)) 
            draw = ImageDraw.Draw(image) 
            
            draw.ellipse((0,0,self.clockWidth,self.clockHeight), fill = 'white' , outline='black' )

            # inner ring 
            innerimage = Image.new('RGBA', (self.clockWidth, self.clockHeight)) 
            innerdraw = ImageDraw.Draw(innerimage) 

            # Fat outter ring
            innerdraw.ellipse((0,0,math.ceil(self.clockWidth-4),math.ceil(self.clockHeight-4)), fill = 'black' , outline='white' )

            # Thin outter ring
            innerdraw.ellipse((4,4,math.floor(self.clockWidth-8),math.floor(self.clockHeight-8)), fill = 'white' , outline='white' )

            # merge outer and inner rings 
            image.paste(innerimage,(2,2),innerimage)

            # center point
            draw.point((int(self.clockWidth/2), int(self.clockHeight/2)), fill="white") 

            self.image = image;
            self.clockface = self.image 

            h = int(time.strftime("%I"))
            m = int(time.strftime("%M"))
            s = int(time.strftime("%s"))




        def createHourHand(self): 

            innerimage = Image.new('RGBA', (self.clockWidth, self.clockHeight)) 
            innerdraw = ImageDraw.Draw(innerimage) 
            innerdraw.rectangle( (int(self.clockWidth/2), int(self.clockHeight/2), int(self.clockWidth/1.3), int(self.clockHeight/2)), fill="blue", outline=None) 

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

            innerimage = innerimage.rotate(angle, PIL.Image.NEAREST, expand=0)
            self.hourhand = innerimage

        def createMinHand(self): 

            innerimage = Image.new('RGBA', (self.clockWidth, self.clockHeight)) 
            innerdraw = ImageDraw.Draw(innerimage) 
            innerdraw.rectangle( (int(self.clockWidth/2), math.ceil(int(self.clockHeight/2)), int(self.clockWidth/1.09), int(self.clockHeight/2)), fill="red", outline=None) 

            h = int(time.strftime("%I"))
            m = int(time.strftime("%M"))
            s = int(time.strftime("%s"))

            angle = (m/60) * 360
            if m > 15 :
                angle +=5
            if m > 30 :
                angle +=5
            if m > 45 :
                angle +=5

            innerimage = innerimage.rotate(angle, PIL.Image.NEAREST, expand=0)
            self.minhand = innerimage


        def createSecondHand(self): 
            innerimage = None 
            innerimage = Image.new('RGBA', (self.clockWidth, self.clockHeight)) 
            innerdraw = ImageDraw.Draw(innerimage) 
            innerdraw.rectangle( (int(self.clockWidth/2), int(self.clockHeight/2), int(self.clockWidth/1.2), int(self.clockHeight/2)), fill="yellow", outline=None) 

            h = int(time.strftime("%I"))
            m = int(time.strftime("%M"))
            s = int(time.strftime("%s"))

            angle = (s/60) * 360
            if m > 15 :
                angle +=5
            if m > 30 :
                angle +=5
            if m > 45 :
                angle +=5

            innerimage = innerimage.rotate(angle, PIL.Image.NEAREST, expand=0)
            self.sechand = innerimage 



        def compositeClock(self): 
            self.image = Image.new('RGBA', (self.clockWidth, self.clockHeight)) 
            self.draw = ImageDraw.Draw(self.image) 
            self.image.paste(self.clockface,(0,0),self.clockface)
            self.image.paste(self.sechand,(0,0),self.sechand)
            self.image.paste(self.minhand,(0,0),self.minhand)
            self.image.paste(self.hourhand,(0,0),self.hourhand)
            self.draw.point((int(self.clockWidth/2), int(self.clockHeight/2)), fill="yellow") 
            

       

        def sendToUnicornHat(self):
                offset_x = 0
                image = self.image 
                display_width,display_height = image.size
                for y in range(display_height):
                    for x in range(display_width):
                        hue = ((time.time() / 10.0) + (x / float(display_width * 2)))
                        r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1, self.brightness/20)]
                        try: 
                            xc = image.getpixel((x + offset_x, y)) 
                            xr =int(xc[0])
                            xg =int(xc[1])
                            xb =int(xc[2])
            
                            #This strangeness allows me to know the clockface/min/hour/sec hands on the image by color, and then i can apply different pixel effects to each with no regard to what they were before. 
                            if xr == 0  and xg == 0 and xb == 0 :
                                unicornhathd.set_pixel(x, y, 0, 0, 0)

                            elif xb > 0  and xr < 255:
                                # hour hand
                               unicornhathd.set_pixel(x, y, 0, 255, 155)

                            elif xr == 255  and xg == 255 and xb == 255 :
                                # outside the clock  
                                unicornhathd.set_pixel(x, y, r, g, b)

                            else:
                                # second hand and all remaining non black or white color   
                                unicornhathd.set_pixel(x, y, xr, xg, xb)

                        except IndexError:
                            offset_x = 0

                offset_x += 1

                if offset_x + display_width > image.size[0]:
                    offset_x = 0

                unicornhathd.show()





    rotation = 0 
    if len(sys.argv) > 1:
        try:
            rotation = int(sys.argv[1])
        except ValueError:
            print("Usage: {} <rotation>".format(sys.argv[0]))
            sys.exit(1)

    unicornhathd.rotation(rotation)
    unicornClock = unicornClock()
    unicornClock.createClockFace()    

    while True: 
           unicornClock.runClock()    
           time.sleep(0.005)


except KeyboardInterrupt:
    unicornhathd.off()
       

