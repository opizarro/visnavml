# script for photoScan 1.3.2 pyhton API (the API changes with version)

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
doc.open(dive_name+'.psx')
chunk = doc.chunk

print('----------- number of chunks ', len(doc.chunks))
# tiledModel
# chunk.buildTiledModel(tile_size=256)
# doc.save()
#
# # DEM
# chunk.buildDem(source=PhotoScan.DataSource.DenseCloudData, interpolation=PhotoScan.EnabledInterpolation)
# doc.save()
#
# # orthomosaic
# chunk.buildOrthomosaic(surface=PhotoScan.DataSource.ElevationData, blending=PhotoScan.MosaicBlending, color_correction=False, fill_holes=True)
# doc.save()

# export Report
chunk.exportReport(path=os.path.join(workfolder,dive_name+'.pdf'), title=dive_name)

# export DEM
chunk.exportDem(path=os.path.join(workfolder,'DEM_'+dive_name+'.tif'))

# export Mesh
mesh_folder = os.path.join(workfolder,'mesh')
os.makedirs(mesh_folder)
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
