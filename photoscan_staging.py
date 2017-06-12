import PhotoScan as ps
import os

# inputs
# project_name: also dive name and folder name
# camera_poses: csv file with camera poses
# imfolder: folder with images to add to project
divename = 'ABE2'
imfolder = '/Users/opizarro/data/survey_20160410_201009_R1922/camB'
workfolder = os.path.join('Users/opizarro/data/processedACFR/',divename)
camera_poses = 'loki_nav_ABE2.csv'

os.chdir(workfolder)

doc = ps.app.document
doc.save('ABE2.psz')
try:
    if len(doc.chunks) == 0:
        chunk = doc.addChunk()
except:
    chunk = doc.addChunk()

# add photos
imlist = list()
for imfile in os.listdir(imfolder):
    imfile_fullpath = os.path.join(imfolder,imfile)
    if os.path.isfile(imfile_fullpath):
        chunk.addPhotos([imfile_fullpath])
        imlist.append(imfile_fullpath)

print(imlist)

ps.app.update()

# coordinate reference system
chunk.crs=PhotoScan.CoordinateSystem("EPSG::4326")

# column order in csv format (n - label, x/y/z - coordinates, s - accuracy, a/b/c - yaw, pitch, roll)
chunk.loadReference(os.path.join(workfolder,camera_poses),"csv","nxyzabc")
chunk.updateTransform()


# chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, preselection=PhotoScan.ReferencePreselection)
# chunk.alignCameras()
# chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)
# chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation)
# chunk.buildUV(mapping=PhotoScan.GenericMapping)
# chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=4096)
doc.save()
