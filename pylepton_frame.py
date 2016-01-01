import numpy as np
import cv2
from pylepton import Lepton
with Lepton() as l:
	frame_ushort,frame_id = l.capture()

frame_byte = np.empty(frame_ushort.shape, np.uint8)

cv2.normalize(frame_ushort, frame_byte, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
cv2.imwrite("output.jpg", frame_byte)
