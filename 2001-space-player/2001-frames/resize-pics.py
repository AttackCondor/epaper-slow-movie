import os
from PIL import Image
from resizeimage import resizeimage

def main():
	n=0
	while True:
		if os.path.exists("frame%d.jpg" % n): 
			print ("frame%d.jpg" % n)
			with open(("frame%d.jpg" % n), 'r+b') as f:
				with Image.open(f) as image:
					himg = resizeimage.resize_height(image, 384)
					img = resizeimage.resize_crop(image, [640,384])
					img.save(("frame%d.jpg" % n), img.format)
			n+=1
		else:
			print("End of files")
			exit()

if __name__ == '__main__':
    main()
