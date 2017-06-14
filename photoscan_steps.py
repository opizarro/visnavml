import PhotoScan
import os, sys
import json
import time
# this is an incomplete script.
# it assumes config_file is defined previously

startTime = time.time()

with open(config_file) as json_config_file:
        config_data = json.load(json_config_file)
print(config_data)

imfolder = config_data['imfolder']
workfolder = config_data['workfolder']
camera_poses = config_data['camera_poses']
dive_name = config_data['dive_name']


outputLog = open("%s/output_log_%s.txt"%(workfolder, dive_name), 'w')
outputLog.write('Starting PhotoScan Python scripted run on project: %s\n'%dive_name)
outputLog.write('Project Path: %s\n'%workfolder)
outputLog.write('Starting set up: %s\n'%time.asctime())

os.chdir(workfolder)

doc = PhotoScan.app.document
doc.save(dive_name+'.psz')

chunk = doc.addChunk()
chunk.label = "chunk for " + dive_name
# add photos
imlist = list()
for imfile in os.listdir(imfolder):
    imfile_fullpath = os.path.join(imfolder,imfile)
    if os.path.isfile(imfile_fullpath):
        chunk.addPhotos([imfile_fullpath])
        imlist.append(imfile_fullpath)
#print(imlist)
# coordinate reference system
chunk.crs=PhotoScan.CoordinateSystem("EPSG::4326")

# column order in csv format (n - label, x/y/z - coordinates, s - accuracy, a/b/c - yaw, pitch, roll)
checkloaded = chunk.loadReference(os.path.join(workfolder,camera_poses),format="csv",columns="nxyzabc",delimiter=",")

cam_acc = float(config_data['camera_accuracy'])
chunk.accuracy_cameras = (cam_acc, cam_acc, cam_acc)
#chunk.cameras[0].reference.accuracy = PhotoScan.Vector( (cam_acc, cam_acc, cam_acc) )
cam_acc_ypr = float(config_data['camera_accuracy_ypr'])
chunk.accuracy_cameras_ypr = (cam_acc_ypr, cam_acc_ypr, cam_acc_ypr)
#chunk.cameras[0].reference.accuracy_ypr = PhotoScan.Vector( (cam_acc_ypr, cam_acc_ypr, cam_acc_ypr) )

chunk.updateTransform()
PhotoScan.app.update()
if checkloaded:
    PhotoScan.ConsolePane.contents='loaded reference poses'
    outputLog.write('loaded reference poses: %s\n'%time.asctime())
else:
    PhotoScan.ConsolePane.contents='FAILED to load reference poses!'
    outputLog.write('FAILED to load reference poses!: %s\n'%time.asctime())




#add known calibration information
#chunk.sensors[0].pixel_height = float(config_data['pixel_size'])
#chunk.sensors[0].pixel_width = float(config_data['pixel_size'])
sens = chunk.addSensor()
sens.focal_length = float(config_data['focal_length'])

sens.antenna.fixed = ('True'==config_data['antenna_fixed'])
loc_acc = float(config_data['antenna_location_acc'])
sens.antenna.location_acc = PhotoScan.Vector( (loc_acc, loc_acc, loc_acc) )
ang_acc = float(config_data['antenna_rotation_acc'])
sens.rotation_acc = PhotoScan.Vector( (ang_acc, ang_acc, ang_acc) )

#Align Photos
outputLog.write('Starting match photos: %s\n'%time.asctime())
#chunk.matchPhotos(accuracy = "high", preselection="disabled", filter_mask=False, point_limit=40000)
#####chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, preselection=PhotoScan.ReferencePreselection)

outputLog.write('Starting align photos: %s\n'%time.asctime())
#chunk.alignPhotos()
#####chunk.alignCameras()

outputLog.write('Starting save: %s\n'%time.asctime())
doc.save()
#doc.save("%s/%s_points.psz"%(path, projectName))
#chunk.exportPoints("%s/%s_points.ply"%(path, projectName), format='ply', dense=False)

outputLog.write('Done: %s\n'%time.asctime())

timeElapsed = (time.time() - startTime)/60.
outputLog.write('Elapsed Time: %.2f minutes'%timeElapsed)

outputLog.close()






# chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, preselection=PhotoScan.ReferencePreselection)
# chunk.alignCameras()
# chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)
# chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation)
# chunk.buildUV(mapping=PhotoScan.GenericMapping)
# chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=4096)
