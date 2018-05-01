'''
Created on 02/04/2012

This toolbox aims to simplify the process of getting a CPCe file (.cpce), and
using it in the context of machine learning algorithms on AUV image data.

@author: Michael Bewley
'''
import os
import subprocess
import csv
import shutil

import numpy as np
#import Image
import pp


USER = 'opizarro'
HOST = 'fjord'

# Some string constants to act as headings in the output data table.
IMAGEFILENAME = 'image_filename'
CPCFOLDER = 'cpc_foldername'
PATCHNUM = 'patch_number'

LOCALIMAGEDIR = '/Volumes/LZD1601/ziggyimages' # Where to put the retrieved images
PROCESSED_DATA_ROOT = '/media/iscsi_processed/PROCESSED_DATA'

class PatchSizeException(Exception):
    pass

class CPCeFileReader:
    def __init__(self, filePath):
        '''
        This class does the direct parsing of individual .cpc files. It was
        written to work with CPCe 3.6.

        filePath: The file path of the CPC file.
        '''
        self.filePath = filePath
        self.folder, self.fileName = os.path.split(filePath)

    def getData(self):
        '''
        Returns a numpy recarray with fields image filename, coords (<hFrac,
        vFrac> with origin at top left of image, and fraction towards bottom
        right as hFrac and vFrac), and class code.
        '''
        r = csv.reader(open(self.filePath, 'r'))
        lines = [line for line in r]

        # Get the header data
        pathList = lines[0][1].split('\\')
        filename = pathList[-1]
        print filename
        # Usually a jpg file is referred to, where we want a png. Simply take
        # without the extension
        filename = os.path.splitext(filename)[0]
        numPoints = int(lines[5][0])
        # This includes things that aren't actually points, like rugosity, etc.
        hScale, vScale = (float(l) for l in lines[0][2:4])

        OFFSET = 5
        HEADERLINES = 6

        # Get the coordinates of the random points that were hand labelled
        pointCoords = np.array(lines[HEADERLINES:HEADERLINES+numPoints], dtype=float)
        pointCoords[:,0] /= hScale
        pointCoords[:,1] /= vScale

        metaData = np.array(lines[HEADERLINES+numPoints:HEADERLINES+2*numPoints])
        fullArray = np.concatenate((pointCoords, metaData), axis=1)
        validData = fullArray[OFFSET:]
        print validData
        headings = [(CPCFOLDER, 'S128'),
                    (IMAGEFILENAME, 'S32'),
                    (PATCHNUM, int),
                    ('hFrac', float),
                    ('vFrac', float),
                    ('class', 'S32'),
                    ('id', int),
                    ('rug', int),
                    ('sub', int),
                    ('slope', int),
                    ('size', int),
                    ]
        data = np.recarray(len(validData), dtype=headings)
        #data[CPCFOLDER] = os.path.split(self.folder)[-1]
        #print filename
        #data[IMAGEFILENAME] = filename
        #print len(validData)
        #data[PATCHNUM] = validData[:,2]
        data['hFrac'] = validData[:,0].astype(float)
        data['vFrac'] = validData[:,1].astype(float)
        data['class'] = validData[:,3]
        data['id'] = metaData[0,-1]
        data['rug'] = metaData[1,-1]
        data['sub'] = metaData[2,-1]
        data['slope'] = metaData[3,-1]
        data['size'] = metaData[4,-1]
        return data

class CPCeDataset:
    def __init__(self, dataFolders, campaignDir):
        '''
        This class creates an instance/attribute dataset based on a number of
        data folders. It grabs the .cpc files from all the folders, and then
        goes hunting for the images referenced by the first line of each
        .cpc file.

        dataFolders: A list of folders which contain cpc files, and
        possibly the related image files.
        '''
        #self.cpcFileReaders = []
        for dataFolder in dataFolders:
            files = os.listdir(dataFolder)
            cpcFileNames = [f for f in files if f.endswith('.cpc')]
            print cpcFileNames
            #self.cpcFileReaders.extend( [CPCeFileReader(os.path.join(dataFolder, f))
            #                       for f in cpcFileNames] )
        #self.cpcData = self._getCPCData()
        self.localImageDir = LOCALIMAGEDIR
        self.campaignDir = campaignDir

    def _getCPCData(self):

        #Get the image filenames, positions of test points within image, and
        #class for all the .cpc files.

        #@return: A numpy recarray object, sorted by folder, filename, hFrac,
        #vFrac and class.

        cpcData = np.concatenate([c.getData() for c in self.cpcFileReaders])
        cpcData = cpcData.view(np.recarray)
        cpcData.sort(order=[CPCFOLDER, IMAGEFILENAME, PATCHNUM, 'class'])
        return cpcData

    def getImages(self, diveDirs=[]):
        '''
        Gets the images that are referenced by the .cpc files, and copies them
        to a local directory.
        First tries the local image directory, then tries the folder the CPC
        file is in, then tries each of the dive directories in abyss.

        diveDir: The root directory of the dive data, relative to
        "PROCESSED_DATA/<self.campaignDir>" on archipelago.
        (e.g. 'r20110410_231304_rottnest_10_40m_north')

        '''
        if not os.path.exists(self.localImageDir):
            os.makedirs(self.localImageDir)

        jobServer = pp.Server(ppservers=())
        print "Starting pp with", jobServer.get_ncpus(), "workers"
        nChunks = 80
        cpcFileGroups = [self.cpcFileReaders[i:i+nChunks] for i in range(0, len(self.cpcFileReaders), nChunks)]
        for i,cpcFileGroup in enumerate(cpcFileGroups):
            jobs = [jobServer.submit(self._getImagesJob, (cpcFile, diveDirs)) for cpcFile in cpcFileGroup]
            [job() for job in jobs]
            print '%0.2f%%'%(100*i/float(len(cpcFileGroups)))
        code = jobServer.wait()
        print 'Finished retrieving images'
        return code

    def _getImagesJob(self, cpcFile, diveDirs):
        data = cpcFile.getData()
        imageFileNames = set(data['image_filename'])
        cpcFolder = cpcFile.folder
        imagesToGetRemotely = []

        # Check if we've already cached the image
        for im in imageFileNames:
            im += '.png'
            if not os.path.exists(os.path.join(self.localImageDir, im)):
                # If we haven't, try the same folder the cpc file was in.
                if os.path.exists(os.path.join(cpcFolder, im)):
                    shutil.copy(os.path.join(cpcFolder, im),
                                self.localImageDir)
                # If it isn't there, try abyss
                imagesToGetRemotely.append(im)

        imagesRemaining = imagesToGetRemotely[:]

        for diveDir in diveDirs:
            tempList = []
            for imageFileName in imagesRemaining:
                success = self._getRemoteImage(imageFileName, diveDir)
                if not success:
                    tempList.append(imageFileName)
            imagesRemaining = tempList
            if not imagesRemaining:
                break # All images collected successfully!
        if imagesRemaining:
            msg = "Couldn't get all images. Did you specify the right dive directory?"
            imgs = '\n'.join(imagesRemaining)
            raise Exception('\n'.join([msg, imgs]))
        else:
            return 0

    def _getRemoteImage(self, imageFileName, diveDir):
        '''
        Fetch an images from a particular dive from abyss.

        Return whether it was successful.
        '''
        grepImage = "'^i20.*[0-9]\{6\}_[0-9]\{6\}_cv'"
        remoteDir = os.path.join(PROCESSED_DATA_ROOT, self.campaignDir, diveDir)
        sshCommand = 'ssh %s@%s "ls %s | grep %s"'%(USER, HOST,
                                                    remoteDir, grepImage)

        # NB: You need to set up public/private key access to archipelago,
        # so you can access without a password.
        imageDirs = subprocess.Popen(sshCommand,shell=True,
                                       stdout=subprocess.PIPE).communicate()[0]
        imageDirs = imageDirs.strip()
        imageDirs = imageDirs.split('\n')
        imageDir = imageDirs[-1] #If there are multiple image dirs, take the last (e.g. _cv3)
        fullRemoteDir = os.path.join(remoteDir, imageDir)

        fromPath = os.path.join(fullRemoteDir, imageFileName)
        scpCommand = 'scp %s@%s:%s %s'%(USER, HOST, fromPath,
                                        self.localImageDir)
        subprocess.call(scpCommand, shell=True)
        toPath = os.path.join(self.localImageDir, imageFileName)
        if os.path.exists(toPath):
            return True
        else:
            return False

    def _getPatchFeatures(self, imageFileName, coords, featureModel,
                         patchSize, greyscale):
        '''
        Gets features from patches in an image, which are centred on a
        particular row/column (corresponding to a CPCe location).

        imageFileName: The filename of the image
        coords: An Nx2 array of <vFrac, hFrac> coordinates within the
        image for the patch centres.

        Returns a list of [patchSize x patchSize x nComponents] numpy arrays.

        '''
        fn, ext = os.path.splitext(imageFileName)
        if ext != '.png':
            imageFileName += '.png'
        imPath = os.path.join(self.localImageDir, imageFileName)
        im = np.asarray(Image.open(imPath))
        patches = []

        if patchSize%2 == 1:
            r = patchSize/2
        else:
            raise ValueError('Patch size has to be odd')

        if greyscale:
            im = im.mean(2) # Convert image to greyscale
        for coord in coords:
            vPixel = int(coord[0] * im.shape[0])
            hPixel = int(coord[1] * im.shape[1])
            i, j = (vPixel, hPixel)
            if greyscale:
                patch = im[i-r:i+r+1, j-r:j+r+1 ]
            else:
                patch = im[i-r:i+r+1, j-r:j+r+1, :]

            if patch.shape[0] != patchSize or patch.shape[1] != patchSize:
                patchFeatures = None
            else:
                patchFeatures = featureModel.transform(patch)
            patches.append(patchFeatures)
        return patches

    def getFullImage(self, imageFileName):
        im = np.asarray(Image.open(os.path.join(LOCALIMAGEDIR, imageFileName)))
        return im

    def getFeatures(self, featureModel, patchSize, greyscale):
        '''
        Get features from all labelled image points in the CPCe files.

        featureModel: An instance of a FeatureModel type class, which returns
        a feature vector when called with featureModel.transform(patch)

        patchSize: The height/width of each image patch. This must be
        odd (to ensure it is centred). Be careful of edge effects with large
        patches ('None' is returned where the patch boundary would exceed the
        boundary of the image).

        greyscale: Boolean for whether to use only greyscale, or RGB
        information.

        Return a tuple of [outCPCData, featureArray].  featureArray is an
        NxM numpy array of values, with rows corresponding to labelled image
        points from the CPCe, and columns corresponding to features. Both
        outputs discard test points where the patch would extend over the
        image boundary.

        '''
        featureArray = []
        newImage = False
        tempCoords = []

        self.getImages()

        # All patches from an images get loaded into RAM before processing.
        # This should be modified if memory constraints become an issue.
        for i,obs in enumerate(self.cpcData):
            coord = (obs['vFrac'], obs['hFrac'])
            if i < len(self.cpcData)-1:
                if (self.cpcData[i+1][IMAGEFILENAME] != self.cpcData[i][IMAGEFILENAME]):
                    newImage = True
                else:
                    newImage = False
            else:
                newImage = True
            if newImage:
                tempCoords.append(coord)
                # Get dictionary of patches, and put in image dictionary
                patches = self._getPatchFeatures(imageFileName=obs[IMAGEFILENAME],
                                                  coords=tempCoords,
                                                  featureModel=featureModel,
                                                  patchSize=patchSize,
                                                  greyscale=greyscale)
                featureArray.extend(patches)

                # Reset for next image
                tempCoords = []
            else:
                tempCoords.append(coord)
        num = len(featureArray)
        keepInds = [i for i in xrange(num) if (featureArray[i] is not None)]
        featureArray = [featureArray[i] for i in keepInds]

        outCPCData = self.cpcData[keepInds]
        featureArray = np.array(featureArray)
        return (outCPCData, featureArray)
