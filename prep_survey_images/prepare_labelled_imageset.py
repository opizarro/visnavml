# takes a set of images and labels and prepares a structure that can be fed into
# inception v3 (which can handle imagenet 2012 inputs)
# this involves
# finding the coordinates of labelled points and the corresponding image
#  cropping at most 299 x 299 pixels around each labeled point.
# storing each cropped image in directories named after the type of label


#import pyexcel as pe
import pandas as pd

survey_sheet = '/Users/opizarro/max-woodside/QN01/MSA157-40_QN01.xls'

df = pd.read_excel(survey_sheet)
print df.head()
