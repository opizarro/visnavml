# script for photoScan 1.3.2 pyhton API (the API changes with version)

import PhotoScan
import os, sys
import json
import time
import argparse
# this is an incomplete script.
# it assumes config_file is defined previously

parser = argparse.ArgumentParser(description="photoscan steps from a json configuration file",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("config_file",help="photoscan config file as json file")
args = parser.parse_args()

startTime = time.time()

with open(args.config_file) as json_config_file:
        config_data = json.load(json_config_file)
print(config_data)

imfolder = config_data['imfolder']
workfolder = config_data['workfolder']
camera_poses = config_data['camera_poses']
dive_name = config_data['dive_name']

mesh_folder = os.path.join(workfolder,'mesh')
if not os.path.exists(mesh_folder):
    print("Making mesh dir")
    os.makedirs(mesh_folder)

outputLog = open("%s/output_log_%s.txt"%(workfolder, dive_name), 'w')
outputLog.write('Starting PhotoScan Python scripted run on project: %s\n'%dive_name)
outputLog.write('Project Path: %s\n'%workfolder)
outputLog.write('Starting set up: %s\n'%time.asctime())

os.chdir(workfolder)

doc = PhotoScan.app.document
doc.save(os.path.join(workfolder,dive_name+'.psx'))

print('number of chunks ', len(doc.chunks))
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
checkloaded = chunk.loadReference(os.path.join(workfolder,camera_poses),format=PhotoScan.ReferenceFormatCSV,columns="nyxzabc",delimiter=",")

cam_acc = float(config_data['camera_accuracy'])
chunk.camera_location_accuracy = (cam_acc, cam_acc, cam_acc)
#chunk.cameras[0].reference.accuracy = PhotoScan.Vector( (cam_acc, cam_acc, cam_acc) )
cam_acc_ypr = float(config_data['camera_accuracy_ypr'])
chunk.camera_rotation_accuracy = (cam_acc_ypr, cam_acc_ypr, cam_acc_ypr)
#chunk.cameras[0].reference.accuracy_ypr = PhotoScan.Vector( (cam_acc_ypr, cam_acc_ypr, cam_acc_ypr) )

chunk.updateTransform()
PhotoScan.app.update()
if checkloaded:
    PhotoScan.app.ConsolePane.contents='loaded reference poses'
    outputLog.write('loaded reference poses: %s\n'%time.asctime())
else:
    PhotoScan.app.ConsolePane.contents='FAILED to load reference poses!'
    outputLog.write('FAILED to load reference poses!: %s\n'%time.asctime())




#add known calibration information
print ("chunk.sensors " ,  chunk.sensors)

chunk.sensors[0].pixel_height = float(config_data['pixel_size'])
chunk.sensors[0].pixel_width = float(config_data['pixel_size'])
chunk.sensors[0].focal_length = float(config_data['focal_length'])

#sens.calibration.f = 1700
print("focal length in mm ", chunk.sensors[0].focal_length)
#print("focal length in pixel ", sens.calibration.f)
#print("sensor fixed ",sens.fixed)
#sens.focal_length = float(config_data['focal_length'])

chunk.sensors[0].antenna.fixed = ('True'==config_data['antenna_fixed'])
print("chunk.sensors[0].antenna.fixed", chunk.sensors[0].antenna.fixed)
loc_acc = float(config_data['antenna_location_acc'])
chunk.sensors[0].antenna.location_acc = PhotoScan.Vector( (loc_acc, loc_acc, loc_acc) )
ang_acc = float(config_data['antenna_rotation_acc'])
chunk.sensors[0].antenna.rotation_acc = PhotoScan.Vector( (ang_acc, ang_acc, ang_acc) )

#Align Photos
outputLog.write('Starting match photos: %s\n'%time.asctime())
chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, generic_preselection=True, reference_preselection=True)

outputLog.write('Starting align photos: %s\n'%time.asctime())
chunk.alignCameras()

outputLog.write('Starting save: %s\n'%time.asctime())
doc.save()

# optimize camera parameters
chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_k1=True, fit_k2=True, fit_k3=True, fit_p1=True, fit_p2=True)
doc.save()
# dense cloud of points
chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)
doc.save()
# mesh
chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation)
doc.save()
# texture
chunk.buildUV(mapping=PhotoScan.GenericMapping,count=4)
doc.save()
chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=4096)
doc.save()

# tiledModel
chunk.buildTiledModel(tile_size=256)
doc.save()
#
# # DEM
chunk.buildDem(source=PhotoScan.DataSource.DenseCloudData, interpolation=PhotoScan.EnabledInterpolation)
doc.save()
#
# # orthomosaic
chunk.buildOrthomosaic(surface=PhotoScan.DataSource.ElevationData, blending=PhotoScan.MosaicBlending, color_correction=False, fill_holes=True)
doc.save()

# export Report
chunk.exportReport(path=os.path.join(workfolder,dive_name+'.pdf'), title=dive_name)

# export DEM
chunk.exportDem(path=os.path.join(workfolder,'DEM_'+dive_name+'.tif'))

# export Mesh

chunk.exportModel(path=os.path.join(mesh_folder,'mesh_'+dive_name+'.ply'))

# export orthomosaic
chunk.exportOrthomosaic(path=os.path.join(workfolder,'mosaic_'+dive_name+'.tif'))

outputLog.write('Done: %s\n'%time.asctime())

timeElapsed = (time.time() - startTime)/60.
outputLog.write('Elapsed Time: %.2f minutes'%timeElapsed)

outputLog.close()
print("End of script !!!!!!!!")



# chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, preselection=PhotoScan.ReferencePreselection)
# chunk.alignCameras()
# chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)
# chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation)
# chunk.buildUV(mapping=PhotoScan.GenericMapping)
# chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=4096)
