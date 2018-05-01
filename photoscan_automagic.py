# test photoscan scripts in python
import PhotoScan as ps
import os

# inputs
# camera_poses: csv file with camera poses
# imfolder: folder with images to add to project
imfolder = '/Users/opizarro/data/survey_20160410_201009_R1922/camB'

doc = ps.app.document
#doc.open("project.psz")
chunk = doc.addChunk()
#chunk.addPhotos()
# camera calibration

# load images
imlist = []
for imfile in os.listdir(imfolder):
    if os.path.isfile(imfile):
        imlist = [imlist, imfile]
        print(imlist)



# coordinate reference system
chunk.crs = ps.CoordinateSystem("EPSG::32641")
# column order in csv format (n - label, x/y/z - coordinates, s - accuracy, a/b/c - yaw, pitch, roll)
chunk.loadReference(camera_poses,"csv","nxyzabc")
chunk.updateTransform()



chunk.matchPhotos(accuracy=Photoscan.HighAccuracy, preselection=Photoscan.ReferencePreselection)
chunk.alignCameras()
chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)
chunk.buildModel(surface=Photoscan.Arbitrary, interpolation=Photoscan.EnabledInterpolation)
chunk.buildUV(mapping=PhotoScan.GenericMapping)
chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=4096)


doc.save()
