# Name:    figure.py
# Purpose: Container of Figure class
# Authors:      Asuka Yamakawa, Anton Korosov, Knut-Frode Dagestad,
#               Morten W. Hansen, Alexander Myasoyedov,
#               Dmitry Petrenko, Evgeny Morozov
# Created:      29.06.2011
# Copyright:    (c) NERSC 2011 - 2013
# Licence:
# This file is part of NANSAT.
# NANSAT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# http://www.gnu.org/licenses/gpl-3.0.html
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
from PIL import ImageFont,ImageDraw,Image
import os
from math import floor,log10
from navtokml import jet
def frange(start, end=None, inc=None):
    "A range function, that does accept float increments..."

    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
    L.append(end)    
    return L

class MakeLegend():
    def __init__(self):
        self.d = {}
        self.d['cmin'] = [0.]
        self.d['cmax'] = [1.]
        self.d['gamma'] = 2.
        self.d['subsetArraySize'] = 100000
        self.d['numOfColor'] = 250
        self.d['cmapName'] = 'jet'
        self.d['ratio'] = 1.0
        self.d['numOfTicks'] = 5
        self.d['titleString'] = ''
        self.d['caption'] = ''
        self.d['fontSize'] = 12
        self.d['logarithm'] = False
        self.d['legend'] = False
        self.d['mask_array'] = None
        self.d['mask_lut'] = None

        self.d['logoFileName'] = None
        self.d['logoLocation'] = [0, 0]
        self.d['logoSize'] = None

        self.d['latGrid'] = None
        self.d['lonGrid'] = None
        self.d['nGridLines'] = 10
        self.d['latlonLabels'] = 0

        self.d['transparency'] = None

        self.d['LEGEND_HEIGHT'] = 0.1
        self.d['CBAR_HEIGHTMIN'] = 5
        self.d['CBAR_HEIGHT'] = 0.15
        self.d['CBAR_WIDTH'] = 0.8
        self.d['CBAR_LOCATION_X'] = 0.1
        self.d['CBAR_LOCATION_Y'] = 0.5
        self.d['CBAR_LOCATION_ADJUST_X'] = 5
        self.d['CBAR_LOCATION_ADJUST_Y'] = 3
        self.d['TEXT_LOCATION_X'] = 0.1
        self.d['TEXT_LOCATION_Y'] = 0.1
        self.d['NAME_LOCATION_X'] = 0.1
        self.d['NAME_LOCATION_Y'] = 0.3
        self.d['DEFAULT_EXTENSION'] = '.png'
        self.fontFileName = os.path.join(os.path.dirname(
                                         os.path.realpath(__file__)),
                                         'fonts/DejaVuSans.ttf')
        self.width=500
        self.height=500
    def linspace(self,a,b,nsteps):
        """returns list of simple linear steps from a to b in nsteps."""
        ssize = float(b-a)/(nsteps-1)
        return [a + i*ssize for i in range(nsteps)]
    def create_legend(self):

        # set fonts size for colorbar
        font = ImageFont.truetype(self.fontFileName, self.d['fontSize'])

        # create a pilImage for the legend
        self.pilImgLegend = Image.new('RGB', (self.width,
                                      int(self.height *
                                      self.d['LEGEND_HEIGHT'])), (255,255,255))
        draw = ImageDraw.Draw(self.pilImgLegend)

        # set black color
        #if self.array.shape[0] == 1:
        #    black = 254
        #else:
        black = (0, 0, 0)

        # if 1 band, draw the color bar
        if 1:#self.array.shape[0] == 1:
            # make an array for color bar
            #bar = np.outer(np.ones(max(int(self.pilImgLegend.size[1] *
            #               self.d['CBAR_HEIGHT']), self.d['CBAR_HEIGHTMIN'])),
            #               np.linspace(0, self.d['numOfColor'],
            #               int(self.pilImgLegend.size[0] *
            #               self.d['CBAR_WIDTH'])))
            # create a colorbar pil Image
            pilImgCbar = Image.new('RGB',(max(int(self.pilImgLegend.size[1] *                                                     self.d['CBAR_HEIGHT']), self.d['CBAR_HEIGHTMIN']),int(self.pilImgLegend.size[0]*self.d['CBAR_WIDTH'])),(255,255,255))
#'P',self.pilImgLegend.size[1] *
 #                          self.d['CBAR_HEIGHT']), self.d['CBAR_HEIGHTMIN'])),
  #                         np.linspace(0, self.d['numOfColor'],
   #                        int(self.pilImgLegend.size[0] *
    #                       self.d['CBAR_WIDTH'])
            # paste the colorbar pilImage on Legend pilImage
            self.pilImgLegend.paste(pilImgCbar,
                                    (int(self.pilImgLegend.size[0] *
                                     self.d['CBAR_LOCATION_X']),
                                     int(self.pilImgLegend.size[1] *
                                     self.d['CBAR_LOCATION_Y'])))
            # create a scale for the colorbar
            scaleLocation = frange(0, 1.0, 1.0/self.d['numOfTicks'])
            scaleArray = scaleLocation

            xstart=int(scaleLocation[0] *
                             self.pilImgLegend.size[0] *
                             self.d['CBAR_WIDTH'] +
                             int(self.pilImgLegend.size[0] *
                             self.d['CBAR_LOCATION_X']))
            yoffset=int(self.pilImgLegend.size[1] *
                           (self.d['CBAR_LOCATION_Y'] +
                            self.d['CBAR_HEIGHT']))-20
            for i in range(xstart,self.pilImgLegend.size[0]-xstart):
                for j in range(self.d['CBAR_LOCATION_ADJUST_Y'],yoffset):
                    pos=(float(i)/self.pilImgLegend.size[0])
                    self.pilImgLegend.putpixel((i,j),jet(pos))
#            if self.d['logarithm']:
#                scaleArray = (np.power(scaleArray, (1.0 / self.d['gamma'])))
#            scaleArray = (scaleArray * (self.d['cmax'][0] -
#                          self.d['cmin'][0]) + self.d['cmin'][0])
            scaleArray = map(self._round_number, scaleArray)
            # draw scales and lines on the legend pilImage
            for iTick in range(self.d['numOfTicks']+1):
                coordX = int(scaleLocation[iTick] *
                             self.pilImgLegend.size[0] *
                             self.d['CBAR_WIDTH'] +
                             int(self.pilImgLegend.size[0] *
                             self.d['CBAR_LOCATION_X']))

                box = (coordX, int(self.pilImgLegend.size[1] *
                                   self.d['CBAR_LOCATION_Y']),
                       coordX, int(self.pilImgLegend.size[1] *
                                  (self.d['CBAR_LOCATION_Y'] +
                                   self.d['CBAR_HEIGHT'])) - 1)
                draw.line(box, fill=black)
                box = (coordX - self.d['CBAR_LOCATION_ADJUST_X'],
                       int(self.pilImgLegend.size[1] *
                           (self.d['CBAR_LOCATION_Y'] +
                            self.d['CBAR_HEIGHT'])) +
                       self.d['CBAR_LOCATION_ADJUST_Y'])
                draw.text(box, scaleArray[iTick], fill=black, font=font)
        # draw longname and units
        box = (int(self.pilImgLegend.size[0] * self.d['NAME_LOCATION_X']),
               int(self.pilImgLegend.size[1] * self.d['NAME_LOCATION_Y']))
        draw.text(box, str(self.d['caption']), fill=black, font=font)

        # if titleString is given, draw it
        if self.d['titleString'] != '':
            # write text each line onto pilImgCanvas
            textHeight = int(self.pilImgLegend.size[1] *
                             self.d['TEXT_LOCATION_Y'])
            for line in self.d['titleString'].splitlines():
                draw.text((int(self.pilImgLegend.size[0] *
                               self.d['TEXT_LOCATION_X']),
                           textHeight), line, fill=black, font=font)
                text = draw.textsize(line, font=font)
                textHeight += text[1]
    def _round_number(self, val):
        '''Return writing format for scale on the colorbar

        Parameters
        ----------
        val : int / float / exponential

        Returns
        --------
        string

        '''
        frmts = {-2: '%.1f', -1: '%.1f', 0: '%.1f',
                 1: '%.1f', 2: '%d', 3: '%d'}
        if val == 0:
            frmt = '%d'
        else:
            digit = floor(log10(abs(val)))
            if digit in frmts:
                frmt = frmts[digit]
            else:
                frmt = '%4.2e'

        return str(frmt % val)
if __name__ == "__main__":
    ml=MakeLegend()
    ml.create_legend()
    ml.pilImgLegend.save('legend.png')
