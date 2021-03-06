# prepare SOI run
import json
import argparse
import sys, os, shutil
import prep_SOI_images as pi
import prep_SOI_poses_from_LOKI as pp

class imargs():
    image_location = ''
    dive_location = ''
    start_time_str = ''
    stop_time_str = ''

class nvargs():
    navcsv_file = ''
    SOI_impath = ''
    cam_poses_file = ''


# argument is the config file for run as a json file
def main():
    parser = argparse.ArgumentParser(description="sets up 3D photoscan run from a json configuration file",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("config_file",help="config file as json file")
    args = parser.parse_args()



# read config file
    with open(args.config_file) as json_config_file:
        config_data = json.load(json_config_file)
    print(config_data)


# call image copy

    imargs.image_location = config_data['original_images_path']
    imargs.dive_location = os.path.join(config_data['processing_base_dir'],config_data['dive_name'],'camB')
    imargs.start_time_str = config_data['start_time']
    imargs.stop_time_str = config_data['stop_time']
    #pi.copy_SOI_images(imargs)

# call nav generate

    nvargs.navcsv_file = config_data['original_nav_file']
    nvargs.SOI_impath = imargs.dive_location
    nvargs.cam_poses_file = os.path.join(config_data['processing_base_dir'],config_data['dive_name'],'loki_nav_'+config_data['dive_name']+'.csv')
    #pp.generate_SOI_poses_from_LOKI(nvargs)

# generate a dive-specific json config for generic script to load in PhotoScan

#processing_base_dir = '/media/opizarro/Samsung_T3/chuckFK160407/processedACFR/

#dive_name = 'ABE2test'
#imfolder = os.path.join(processing_base_dir,dive_name,'/camB')
#workfolder = os.path.join('Users/opizarro/data/processedACFR/',dive_name)
# camera poses are in the dive_name folder
#camera_poses = 'loki_nav_'+dive_name+'.csv'
    dive_name = config_data['dive_name']
    workfolder = os.path.join(config_data['processing_base_dir'],dive_name)
    photoscan_config_data = {'dive_name':dive_name,
                        'workfolder':workfolder,
                        'imfolder':os.path.join(workfolder,'camB'),
                        'camera_poses':os.path.join(workfolder,'loki_nav_'+dive_name+'.csv'),
                        'pixel_size': '0.00645',
                        'focal_length': '10.67',
                        'camera_accuracy': '2',
                        'camera_accuracy_ypr': '10',
                        'antenna_location_acc': '1',
                        'antenna_rotation_acc': '20',
                        'antenna_fixed': 'false' }

    # json config will be self-documenting
    ps_config_file_name = os.path.join(workfolder,'photoscan_config_'+dive_name+'.json')
    with open(ps_config_file_name,'w') as outfile:
        json.dump(photoscan_config_data, outfile)
    # copy the main script for processing
    #shutil.copy('/home/opizarro/git/visnavml/photoscan_staging.py',workfolder)
    #shutil.copy('/home/opizarro/git/visnavml/photoscan_steps.py',workfolder)
    # generate mini pyhton starter script and append photoscan steps afterwards
    python_miniscript = os.path.join(workfolder,'start_photoscan_proc_'+dive_name+'.py')

    photoscan_steps_script =  '/home/opizarro/git/visnavml/photoscan_steps.py'
    with open(python_miniscript, 'w+') as f:
        #f.write('import PhotoScan \n')
        #f.write('import photoscan_staging as stage \n')
        f.write("config_file = '%s' \n" % ps_config_file_name)
        #f.write("from photoscan_steps import *")

        #f.write('stage.run_photoscan_steps(config_file) \n')
        with open(photoscan_steps_script) as infile:
            f.write(infile.read())


    #dest_symlink = os.path.join(workfolder,'photoscan_config_symlink.json' )
    # link to generic config name
    #os.symlink(ps_config_file_name, dest_symlink) # needs a file system that supports links
    #shutil.copy(ps_config_file_name,dest_symlink)
    # copy generic script
    #shutil.copy('/home/opizarro/git/visnavml/photoscan_staging.py',workfolder)




if __name__ == "__main__":
    sys.exit(main())
