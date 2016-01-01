#!/usr/bin/env python

import time
import picamera
import numpy as np
import cv2
import os
import sys
import traceback
from pylepton import Lepton

def main(flip_v = False, alpha = 128, device = "/dev/spidev0.0", numpics = 1, freq = 1):
  # Create an array representing a 1280x720 image of
  # a cross through the center of the display. The shape of
  # the array must be of the form (height, width, color)
  a = np.zeros((240, 320, 3), dtype=np.uint8)
  lepton_buf = np.zeros((60, 80, 1), dtype=np.uint16)

  with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.framerate = 24
    camera.vflip = flip_v
    camera.start_preview()
    camera.fullscreen = True
    # Add the overlay directly into layer 3 with transparency;
    # we can omit the size parameter of add_overlay as the
    # size is the same as the camera's resolution
    o = camera.add_overlay(np.getbuffer(a), size=(320,240), layer=3, alpha=int(alpha), crop=(0,0,80,60), vflip=flip_v)
    try:
      start = time.time()
      time.sleep(0.2) # give the overlay buffers a chance to initialize
      for i in range(1,numpics+1):
      	with Lepton(device) as l:
        	frame_ushort,frame_id = l.capture(lepton_buf)
      
      	cv2.normalize(lepton_buf, lepton_buf, 0, 65535, cv2.NORM_MINMAX)
      	np.right_shift(lepton_buf, 8, lepton_buf)
      	a[:lepton_buf.shape[0], :lepton_buf.shape[1], :] = lepton_buf  
      	o.update(np.getbuffer(a))
     	filename = "output_" + str(i) + ".jpg"
    	cv2.imwrite(filename, lepton_buf)
	time.sleep(1/freq)
#	print filename
    except Exception:
      traceback.print_exc()
    finally:
      time_spent = time.time() - start
      print "\n\tSUMMARY"
      print "================================"
      print "Time spent:\t\t" + str(time_spent)
      print "Photos taken:\t\t" + str(numpics)
      print "Adjusted frequency:\t" + str(float(numpics/time_spent))
      print "\n"
      camera.remove_overlay(o)

if __name__ == '__main__':
  from optparse import OptionParser

  usage = "usage: %prog [options] output_file[.format]"
  parser = OptionParser(usage=usage)

  parser.add_option("-f", "--flip-vertical",
                    action="store_true", dest="flip_v", default=False,
                    help="flip the output images vertically")

  parser.add_option("-a", "--alpha",
                    dest="alpha", default=128,
                    help="set lepton overlay opacity")

  parser.add_option("-d", "--device",
                    dest="device", default="/dev/spidev0.0",
                    help="specify the spi device node (might be /dev/spidev0.1 on a newer device)")
  
  parser.add_option("-n", "--numpics",
		    dest="numpics", default=1,
		    help="specify number of frames to capture")
  
  parser.add_option("--fr", "--freq",
		    dest="freq", default=1,
		    help="specify frequency of photo capture")

  (options, args) = parser.parse_args()

  output_folder = raw_input("Enter output folder name: ")
  if( not os.path.exists(os.getcwd() + os.sep + output_folder) and len(output_folder) > 0):
	check = raw_input("Folder does not exist. Would you like to make it? (y/n): ")
	if check == 'y':
		make_folder = "mkdir " + output_folder
		os.system(make_folder)
	else:
		print "Not sure what to do. Exiting... "
		sys.exit()
 
  main(flip_v = options.flip_v, alpha = options.alpha, device = options.device, numpics = int(options.numpics), freq = float(options.freq))
  if len(output_folder) != 0:
  	move_command = "mv *.jpg " + output_folder
	os.system(move_command) 
	print "Photo's moved into folder " + os.getcwd() + os.sep + output_folder
  else: 
	print "Pictures saved to current working directory."
