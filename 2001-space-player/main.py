#!/usr/bin/python
# -*- coding:utf-8 -*-

import epd7in5
import datetime
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import os

try:
    print("Start playing movie: 2001 A Space Odyssey")
    epd = epd7in5.EPD()
    epd.init()
    print("Clear")
    epd.Clear(0xFF)
    
    while os.path.exists(".\\2001-frames\\frame%d.jpg" % framecount):
        print ("Loading frame%d.jpg bmp file" % framecount)
		print (datetime.datetime.now())
        Frame = Image.open(".\\2001-frames\\frame%d.jpg" % framecount)
        epd.display(epd.getbuffer(Frame))
		framecount += 1
        epd.sleep()
		time.sleep(30)
		epd.init()
		
    
        
except:
    print 'traceback.format_exc():\n%s' % traceback.format_exc()
	epd.sleep()
    exit()

