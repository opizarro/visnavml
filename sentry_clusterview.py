#! /usr/bin/env python
""" Script to generate the AUV dive reports.

Author: Daniel Steinberg
        Australian Centre for Field Robotics

Date:   07/05/2013.

"""

import os
import sys
import math
import argparse
import matplotlib
import subprocess
import Image
matplotlib.use('Agg')  # Do not require X server
import matplotlib.pyplot as plt
import renavutils as rutil
import numpy as np
#import markdown
from scipy.io import netcdf
from matplotlib import rc
from markdown import markdown
from datetime import datetime


def main():
    """ Function to generate dive reports. """

    parser = argparse.ArgumentParser(description="Generate the plot for a dive"
                " renav.", 
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("stereopose", help="Stereo pose data for this renav.")
    parser.add_argument("vehiclepose", help="Vehicle pose data for this renav.")
    parser.add_argument("--outdir", help="Directory to output report to.",
                        default="report")
    parser.add_argument("--labels", help="Cluster labels for this renav.",
                        default=None)
    parser.add_argument("--imagedir", help="Processed image directory (PNG).",
                        default=None)
    parser.add_argument("--divename", help="Name of the dive.", default=None)
    parser.add_argument("--seabirdfile", help="Seabird NetCDF file name.",
                        default=None)
    parser.add_argument("--ecopuckfile", help="Ecopuck NetCDF file name.",
                        default=None)
    args = parser.parse_args()

    # Try to make the save path
    if not os.path.exists(args.outdir):
        try:
            os.mkdir(args.outdir)
        except Exception as e:
            print("Cannot make {0}, error {1}".format(args.savdir, e))
            return 1

    # Construct the report
    md = markdown()
    if args.divename is not None:
        md.heading1('Dive Report for {0}'.format(args.divename))
        repname = args.divename + '_report'
    else:
        dnow = datetime.now()
        md.heading1('Dive Report {0}/{1}/{2}, {3}:{4}.'.format(dnow.day,
                    dnow.month, dnow.year, dnow.hour, dnow.minute))
        repname = 'report'

#    # Get some dive statistics
#    print("Calculatind dive statistics...")
#    md.heading2('Dive statistics:')
#    dstats = divestats(args.stereopose)
#    md.unordered_list(dstats)

    # Make the plots use Serif fonts
    rc('font', family='serif')

    md.heading2('Sensor plots and dive summaries:')

    # Plot AUV tracklines with depth
    print("Making topographical depth plot...")
    fig = rutil.overlay_depth(args.stereopose)
    trackname = 'auv_track.png'
    fig.savefig(os.path.join(args.outdir, trackname))
    md.image(trackname, 'AUV survey track, coloured by depth.')

    # Plot depth profile
    print("Making depth profile...")
    fig = rutil.depth_profile(args.vehiclepose)
    dprofname = 'depth_profile.png'
    fig.savefig(os.path.join(args.outdir, dprofname))
    md.image(dprofname, 'Depth profile.')

    # Plot AUV tracklines with clusters
    if args.labels is not None:
        print("Making topographical cluster plot...")
        fig = rutil.overlay_clusters(args.stereopose, args.labels)
        ctrackname = 'cluster_track.png'
        fig.savefig(os.path.join(args.outdir, ctrackname))
        md.image(ctrackname, 'Image cluster labels overlaid on AUV track.')
    else:
        print("No cluster labels input, skipping topographical cluster plot.")

    # Plot the AUV cluster exemplars
    if (args.labels is not None) and (args.imagedir is not None):
        print("Making cluster exemplar mosaic...")
        immos = rutil.show_clusters(args.imagedir, args.labels)
        cmosname = 'cluster_examples.png'
        img = Image.fromarray(immos)
        img.save(os.path.join(args.outdir, cmosname))
        md.image(cmosname, 'Random examples of the image clusters (row-wise).')
    else:
        print("No labels or image directory input, skipping image mosaic.")

    # Plot Searbird CTD information
    if args.seabirdfile is not None:
        print("Making CTD profile...")
        fig = plot_seabird(args.seabirdfile)
        sbprofname = 'seabird_profile.png'
        fig.savefig(os.path.join(args.outdir, sbprofname))
        md.image(sbprofname, 'Seabird CTD.')
    else:
        print("No CTD file input, skipping CTD profile.")

    if args.ecopuckfile is not None:
        print("Making ecopuck profile...")
        fig = plot_ecopuck(args.ecopuckfile)
        ecprofname = 'ecopuck_profile.png'
        fig.savefig(os.path.join(args.outdir, ecprofname))
        md.image(ecprofname, 'Ecopuck.')
    else:
        print("No ecopuck file input, skipping ecopuck profile.")

    # Write report
    print("Writing report...")
    repname_md = repname + '.md'
    repname_pdf = repname + '.pdf'
    repname_html = repname + '.html'
    os.chdir(args.outdir)
    md.write_markdown(repname_md) 
    subprocess.check_call(['pandoc', '-o', repname_pdf, repname_md])
    subprocess.check_call(['pandoc', '-o', repname_html, repname_md])
    print('Done!')


def divestats(stereopose):
    """ Calculate some dive statistics -- Based on Duncan's reports. """

    renav, olat, olon, ftype = rutil.read_renav(stereopose)

    if ftype is not 'stereo':
        raise ValueError("Need the stereo pose data file!")

    # Track distance and image spacing (using Duncan's calcs)
    X = np.array(renav['Xpos'])
    Y = np.array(renav['Ypos'])
    delX = X[1:] - X[:-1]
    delY = Y[1:] - Y[:-1]
    imdist = np.sqrt(delX**2 + delY**2)
    dist = np.sum(imdist)
    imspace = np.mean(imdist)

    # Field of View - also using Duncan's formulae
    avalt = np.mean(renav['altitude'])
    fov_horiz = 42.4*math.pi/180
    fov_verti = 34.5*math.pi/180
    horizview = 2 * avalt * math.tan(fov_horiz/2)
    vertiview = 2 * avalt * math.tan(fov_verti/2)

    dstats = ['Latitude: {0:.6f}'.format(olat),
              'Longitude: {0:.6f}'.format(olon),
              'Maximum camera depth: {0:.2f} m'.format(np.max(renav['Zpos'])),
              'Minimum camera depth: {0:.2f} m'.format(np.min(renav['Zpos'])),
              'Approx. distance travelled: {0:.2f} m'.format(dist),
              'Average image altitude: {0:.2f} m'.format(avalt),
              'Number of stereo pairs: {0}'.format(len(renav['leftim'])),
              'Average image spacing: {0:.2f} m'.format(imspace),
              'Average image footprint: {0:.2f} x {1:.2f} m'.format(horizview,
                                                                    vertiview)
              ]

    return dstats


def plot_seabird(netcdffile):
    """ Plot the Seabird CTD sensor profile. """

    f = netcdf.netcdf_file(netcdffile, 'r')

    depth = f.variables['DEPTH'].data
    salinity = f.variables['PSAL'].data
    temp = f.variables['TEMP'].data

    f.close()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ln1 = ax1.plot(salinity, depth,  'r.', label='Salinity')
    ax1.invert_yaxis()

    ax2 = ax1.twiny()
    ln2 = ax2.plot(temp, depth, 'g.', label='Temperature')

    ax1.grid(True)
    ax1.set_ylabel('Depth (m)')
    ax1.set_xlabel('Salinity (PSU)')
    ax2.set_xlabel('Temperature ($^\circ$C)')

    lns = ln1+ln2
    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc=0)

    return fig


def plot_ecopuck(netcdffile):
    """ Plot the Ecopuck's profile. """

    f = netcdf.netcdf_file(netcdffile, 'r')

    depth = f.variables['DEPTH'].data
    cdom = f.variables['CDOM'].data
    cphl = f.variables['CPHL'].data
    opbs = f.variables['OPBS'].data

    f.close()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ln1 = ax1.plot(cdom, depth,  'r.', label='CDOM')
    ln2 = ax1.plot(cphl, depth,  'g.', label='CPHL')
    ax1.invert_yaxis()

    ax2 = ax1.twiny()
    ln3 = ax2.plot(opbs, depth, 'b.', label='Backscatter')

    ax1.grid(True)
    ax1.set_ylabel('Depth (m)')
    ax1.set_xlabel('CDOM and CPHL (mg m$^{-3}$)')
    ax2.set_xlabel('Backscatter (m$^{-1}$ sr$^{-1}$)')

    lns = ln1+ln2+ln3
    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc=0)
    #ax1.legend([ln1, ln2], [ln1.get_label(), ln2.get_label()], loc=0)

    return fig


if __name__ == "__main__":
    sys.exit(main())
