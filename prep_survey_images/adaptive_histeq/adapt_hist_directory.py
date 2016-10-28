# adaptive histogram equalisation (CLAHE) for all images in a folder
# inputs: 
#   folder with images
#   name of output folder
# output: folder with 'corrected images'

import numpy as np
import cv2
import glob
import os

inputdir = '/media/water/2016/PROCESSED_DATA/Jamaica201607/r20160709_151200_pr16_region3_dense_ns/i20160709_151200_cv'
inputext = 'png'
outputdir = '/media/water/2016/PROCESSED_DATA/Jamaica201607/r20160709_151200_pr16_region3_dense_ns/i20160709_151200_clahe'

def maybe_makedir(dirname, force=False):
  if os.path.isdir(dirname) and not force:
    # You may override by setting force=True.
    print('%s already present - Skipping making dir' % (dirname))
  else:
    print('Making dir %s.' % dirname)
    os.makedirs(dirname)
  return

maybe_makedir(outputdir)

# for each image in the input folder
# read image, run CLAHE and then save with same name in output folder

inputpath = os.path.join(inputdir,'*.' + inputext)
print inputdir
print inputpath

clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

for file in glob.glob(inputpath):
    img = cv2.imread(file,1) # assumes colour image
    cv2.imshow("img",img)

    # convert image to LAB
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    cv2.imshow("lab",lab)

    # split into channels
    l,a,b = cv2.split(lab)
    cv2.imshow('l_channel', l)
    cv2.imshow('a_channel', a)
    cv2.imshow('b_channel', b)

    # apply CLAHE to L channel

    cl = clahe.apply(l)
    cv2.imshow('CLAHE output', cl)

    # merge channels
    limg = cv2.merge((cl,a,b))
    cv2.imshow('limg', limg)

    #convert back to BGR
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    cv2.imshow('final', final)

    cv2.imwrite(os.path.join(outputdir,os.path.basename(file)),final)


