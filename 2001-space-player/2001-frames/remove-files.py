#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
from PIL import Image
from resizeimage import resizeimage

def main():
	n=2
	while True:
		if os.path.exists("frame%d.jpg" % n): 
			os.remove("frame%d.jpg" % n)
			n+=1
		else:
			print("End of files")
			exit()

if __name__ == '__main__':
    main()
