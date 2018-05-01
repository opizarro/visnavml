'''
Created on 30/04/2012

Testing class for pycpce module.

@author: mbew7729
'''

import os
import shutil
import unittest

import Image
import numpy as np

import pycpce


TESTCPC = 'test.cpc'
class CPCeFileReaderTester(unittest.TestCase):
    def setUp(self):
        '''
        Set up an example based on a real CPCe 3.6 .cpc file.
        '''
        f = open(TESTCPC, 'wb')
        f.writelines('\n'.join([
                        '"R:\TAFI\Data\CERF\AUV\IMAGE_~1\CPCe36\CERF_A~3.TXT","r:\TAFI\Data\CERF\AUV\Tasmania200810\r20081006_231255_waterfall_05_transect\Waterfall_05_filecopy100\PR_20081006_232302_383_LC16.jpg",20400,15360,16337,12301',
                        '74.92196,15285.08',
                        '20325.08,15285.08',
                        '20325.08,74.92074',
                        '74.92196,74.92074',
                        '55',
                        '13060,4547',
                        '448,14582',
                        '20211,6856',
                        '8096,8438',
                        '11645,8256',
                        '10072,5606',
                        '4474,2446',
                        '3500,7354',
                        '18987,6722',
                        '11847,2446',
                        '17183,13557',
                        '5789,14654',
                        '11186,8137',
                        '19827,4233',
                        '8769,1713',
                        '1845,13834',
                        '19700,3516',
                        '18210,12298',
                        '10250,13841',
                        '15117,1799',
                        '19543,11928',
                        '11924,13974',
                        '1579,2502',
                        '13339,14069',
                        '7298,8584',
                        '6813,13290',
                        '754,2322',
                        '19132,3424',
                        '9672,1784',
                        '6927,6811',
                        '3381,4780',
                        '6179,4473',
                        '2330,10633',
                        '16086,9418',
                        '18953,14677',
                        '16287,4934',
                        '6511,3361',
                        '757,7194',
                        '3985,13515',
                        '6605,7740',
                        '13221,3025',
                        '11444,15080',
                        '10352,3081',
                        '3713,10515',
                        '16615,13000',
                        '18205,11706',
                        '18758,1233',
                        '7403,4884',
                        '11971,11371',
                        '425,3233',
                        '15727,13722',
                        '13471,3775',
                        '18528,4727',
                        '13445,13481',
                        '5463,14765',
                        '"1","ID","Notes","7"',
                        '"2","RUG","Notes","2"',
                        '"3","SUB","Notes","7"',
                        '"4","SLOPE","Notes","2"',
                        '"5","SIZE","Notes","2"',
                        '"6","SAND","Notes",""',
                        '"7","SAND","Notes",""',
                        '"8","SAND","Notes",""',
                        '"9","MATR","Notes",""',
                        '"10","SAND","Notes",""',
                        '"11","MATR","Notes",""',
                        '"12","SAND","Notes",""',
                        '"13","SAND","Notes",""',
                        '"14","ECK","Notes",""',
                        '"15","MATR","Notes",""',
                        '"16","SAND","Notes",""',
                        '"17","MATR","Notes",""',
                        '"18","MATR","Notes",""',
                        '"19","MATR","Notes",""',
                        '"20","MATR","Notes",""',
                        '"21","MATR","Notes",""',
                        '"22","UNID","Notes",""',
                        '"23","SAND","Notes",""',
                        '"24","RFOL","Notes",""',
                        '"25","MATR","Notes",""',
                        '"26","MATR","Notes",""',
                        '"27","SAND","Notes",""',
                        '"28","ECK","Notes",""',
                        '"29","MATR","Notes",""',
                        '"30","MATR","Notes",""',
                        '"31","SAND","Notes",""',
                        '"32","SAND","Notes",""',
                        '"33","SAND","Notes",""',
                        '"34","ECK","Notes",""',
                        '"35","SAND","Notes",""',
                        '"36","RFOL","Notes",""',
                        '"37","SAND","Notes",""',
                        '"38","SAND","Notes",""',
                        '"39","SAND","Notes",""',
                        '"40","RFOL","Notes",""',
                        '"41","RFOL","Notes",""',
                        '"42","MATR","Notes",""',
                        '"43","SAND","Notes",""',
                        '"44","SAND","Notes",""',
                        '"45","MATR","Notes",""',
                        '"46","MATR","Notes",""',
                        '"47","MATR","Notes",""',
                        '"48","SAND","Notes",""',
                        '"49","MATR","Notes",""',
                        '"50","SAND","Notes",""',
                        '"51","MATR","Notes",""',
                        '"52","ECK","Notes",""',
                        '"53","ECK","Notes",""',
                        '"54","MATR","Notes",""',
                        '"55","SAND","Notes",""',
                        '',
                      ]))
        f.close()
        
        
    def tearDown(self):
        os.remove(TESTCPC)
        
    def test_getDataGeneral(self):
        cpcReader = pycpce.CPCeFileReader(TESTCPC)
        data = cpcReader.getData()
        
        self.assertIsInstance(data, np.recarray)
        self.assertEqual(len(data), 50)
        
    def test_classes(self):
        cpcReader = pycpce.CPCeFileReader(TESTCPC)
        data = cpcReader.getData()
        self.assertEqual(data[-1]['class'], 'SAND')
        self.assertEqual(data[-20]['class'], 'RFOL')
        
    def test_coords(self):
        hScale = 20400.
        vScale = 15360.
        cpcReader = pycpce.CPCeFileReader(TESTCPC)
        data = cpcReader.getData()
        self.assertAlmostEqual(data[-1]['hFrac'],  5463./hScale, places=3)
        self.assertAlmostEqual(data[-1]['vFrac'],  14765./vScale, places=3)

    def test_patchNums(self):
        cpcReader = pycpce.CPCeFileReader(TESTCPC)
        data = cpcReader.getData()
        self.assertEqual(data[0][pycpce.PATCHNUM], 6)
        self.assertEqual(data[-1][pycpce.PATCHNUM], 55)
    
    def test_metaData(self):
        cpcReader = pycpce.CPCeFileReader(TESTCPC)
        data = cpcReader.getData()
        self.assertTrue((data[pycpce.CPCFOLDER] == cpcReader.folder).all())
        self.assertTrue((data[pycpce.IMAGEFILENAME] == 'PR_20081006_232302_383_LC16').all())
        self.assertTrue((data['id'] == 7).all())
        self.assertTrue((data['rug'] == 2).all())
        self.assertTrue((data['sub'] == 7).all())
        self.assertTrue((data['slope'] == 2).all())
        self.assertTrue((data['size'] == 2).all())


TEMPTESTCWD = 'testing_temp'
TESTDATAFOLDER = 'integration_test_data'
CAMPAIGNDIR = 'Tasmania200810'
DIVEDIRS = ['r20081006_231255_waterfall_05_transect',
            'r20081013_230755_high_yellow_19_quadrep']
class CPCeDatasetTester(unittest.TestCase):
    '''
    This class performs functional testing (as unit tests don't really make
    sense at this level).
    '''
    def setUp(self):
        os.mkdir(TEMPTESTCWD)
        self.cwd = os.getcwd()
        os.chdir(TEMPTESTCWD)
        dataRoot = os.path.join(self.cwd, TESTDATAFOLDER)
        self.testFolderPaths = [os.path.join(dataRoot, lf) for lf in DIVEDIRS]
        
    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(TEMPTESTCWD)
        
    def test_cpcFilesImported(self):
        cpcFiles = ['PR_20081006_232302_383_LC16.cpc',
                    'PR_20081006_232441_396_LC16.cpc',
                    'PR_20081013_231631_457_LC16.cpc',
                    'PR_20081013_231811_471_LC16.cpc',
                    'PR_20081013_231951_481_LC16.cpc'
                    ]
        cpcFiles.sort()
        ds = pycpce.CPCeDataset(dataFolders=self.testFolderPaths,
                                campaignDir=CAMPAIGNDIR)
        readFiles = [fr.fileName for fr in ds.cpcFileReaders]
        readFiles.sort()
        self.assertEqual(cpcFiles, readFiles)
    
    def test_getCPCData(self):
        ds = pycpce.CPCeDataset(dataFolders=self.testFolderPaths,
                                campaignDir=CAMPAIGNDIR)
        data = ds._getCPCData()
        self.assertIsInstance(data, np.recarray)
        self.assertEqual(len(data), 50*5)
        
    def test_getImages(self):
        ds = pycpce.CPCeDataset(dataFolders=self.testFolderPaths,
                                campaignDir=CAMPAIGNDIR)
        ds.getImages(DIVEDIRS)
        self.assertTrue(os.path.exists(pycpce.LOCALIMAGEDIR))
        
        retrievedImageFiles = os.listdir(pycpce.LOCALIMAGEDIR)
        retrievedImageFiles.sort()
        
        data = ds._getCPCData()
        imagesToRetrieve = list(set(data[pycpce.IMAGEFILENAME]))
        imagesToRetrieve = [im+'.png' for im in imagesToRetrieve]
        imagesToRetrieve.sort()
        
        self.assertEqual(retrievedImageFiles, imagesToRetrieve)
    
    def test__getPatchFeaturesTransparent(self):
        if not os.path.exists(pycpce.LOCALIMAGEDIR):
            os.mkdir(pycpce.LOCALIMAGEDIR)
        TESTIM = 'test.png'
        ds = pycpce.CPCeDataset(dataFolders=self.testFolderPaths,
                                campaignDir=CAMPAIGNDIR)
        class TransparentFeatureModel:
            def transform(self, x):
                return x.flatten()
            
        # Make a test RGB image and save it
        imArray = np.array([
        [ 0,  1,  2,  3,  4],
        [ 5,  6,  7,  8,  9],
        [43, 67, 21, 10, 40],
        [100, 200, 255, 153, 80],
        ])
        im = np.zeros((4,5,3))
        im[:,:,0] = imArray
        im[:,:,1] = imArray
        im[:,:,2] = imArray
        im = Image.fromarray(np.uint8(im))
        im.save(os.path.join(pycpce.LOCALIMAGEDIR, TESTIM))
        featureModel = TransparentFeatureModel()
        
        # Make some test coords representing vFrac, hFrac from top left
        coords = [
                  # Corners should return None
                  (0, 0),
                  (3, 0),
                  (0, 4),
                  (3, 4),
                  (1, 1),
                  (2, 3),
                  (0., 2),
                  ]
        coords = np.array(coords)
        coords += 0.5
        coords[:,0] /= imArray.shape[0]
        coords[:,1] /= imArray.shape[1]
        
        correctPatches = [
                          None,
                          None,
                          None,
                          None,
                          np.array([0,1,2,5,6,7,43,67,21]),
                          np.array([7,8,9,21,10,40,255,153,80]),
                          None,
                          ]
        patches = ds._getPatchFeatures(imageFileName=TESTIM,
                                       featureModel=featureModel,
                                       coords=coords,
                                       patchSize=3,
                                       greyscale=True)
        os.remove(os.path.join(pycpce.LOCALIMAGEDIR, TESTIM))
        for i in range(len(coords)):
            if correctPatches[i] == None:
                self.assertTrue(patches[i] == correctPatches[i])
            else:
                self.assertTrue((patches[i] == correctPatches[i]).all())

    def test_getFeaturesTransparent(self):
        PATCHSIZE = 3
        
        ds = pycpce.CPCeDataset(dataFolders=self.testFolderPaths,
                                campaignDir=CAMPAIGNDIR)
        ds.getImages(DIVEDIRS)
        
        class TransparentFeatureModel:
            def transform(self, x):
                return x.flatten()
        featureModel = TransparentFeatureModel()
        outData, featureArray = ds.getFeatures(featureModel=featureModel,
                                               patchSize=PATCHSIZE,
                                               greyscale=True
                                               )
        print set(outData[pycpce.IMAGEFILENAME])
        self.assertEquals(len(featureArray), 50*5)
        self.assertEquals(len(outData), 50*5)
        imageFeatures = featureArray[outData[pycpce.IMAGEFILENAME] == 'PR_20081006_232302_383_LC16']
        imageCPCData = outData[outData[pycpce.IMAGEFILENAME] == 'PR_20081006_232302_383_LC16']
        vFrac = imageCPCData[0]['vFrac']
        hFrac = imageCPCData[0]['hFrac']
        self.assertAlmostEqual(vFrac, 0.364973, places=6)
        self.assertAlmostEqual(hFrac, 0.493725, places=6)
        
        # Manually looked up the image patch around vFrac, hFrac
        patchExtract = imageFeatures[0].reshape(PATCHSIZE, PATCHSIZE)
        correctPatch = np.array([
                                 [96.00, 94.67, 93.67],
                                 [96.00, 92.33, 93.67],
                                 [87.33, 88.00, 91.33],
                                 ])
        diffPatch = patchExtract-correctPatch
        self.assertAlmostEqual(np.abs(diffPatch).sum(), 0, delta=1)

if __name__ == '__main__':
    unittest.main()
