#!/usr/bin/env python

import cv2

img1 = cv2.imread('/home/34.5/Pictures/weird_traditions.jpg', 1) # load image using OpenCV
cv2.imshow('image', img1) # display image using opencv
cv2.waitKey(0) # wait for keypress
cv2.destroyAllWindows() # close image window

img2 = cv2.imread('/home/34.5/Pictures/IC_bite.JPG', 1) # load image using OpenCV
img2 = img2[:, :, : :-1] # change RGB ordering for matplotlib
plt.imshow(img2, cmap = 'gnuplot2', interpolation = 'bicubic') # image settings?
plt.xticks([]), plt.yticks([]) # remove ticks on axes
plt.show() # display image using matplotlib
