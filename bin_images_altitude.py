import csv
from sets import Set
import sys
import math
import itertools
import os

# args
# 1 pose file
# 2 cluster id ? Not needed for this
# 2 converted image path

# steps for altitude band
def frange6(*args):
    """A float range generator."""
    start = 0.0
    step = 1.0

    l = len(args)
    if l == 1:
        end = args[0]
    elif l == 2:
        start, end = args
    elif l == 3:
        start, end, step = args
        if step == 0.0:
            raise ValueError, "step must not be zero"
    else:
        raise TypeError, "frange expects 1-3 arguments, got %d" % l

    v = start
    while True:
        if (step > 0 and v >= end) or (step < 0 and v <= end):
            raise StopIteration
        yield v
        v += step


from operator import itemgetter
from itertools import islice, chain

def skip_comments(iterable):
    for line in iterable:
        if not line.startswith('%') or not line.startswith('ORIGIN_'):
            yield line


listofimg = []
dcluster = {}
# arg 2 is the list of labels?
# not needed for Exxon application so making dcluster =1 for all calls further down
#with open(sys.argv[2]) as f:
#    for line in f:
#       (key, val) = line.split()
#       dcluster[key] = int(val)

# read pose file
gpath=os.path.dirname(os.path.abspath(sys.argv[1]))

# converted image path
imcvpath=sys.argv[2]

print 'Global path %s\n' % gpath
with open(sys.argv[1],'rb') as f:
    for line in csv.reader(skip_comments(f),delimiter = ' '):
        n=len(line)
        #print line
        if n > 2:
            imagenameL = line[10]
            imagenameR = line[11]
            alt = float(line[12])
            print '%s %s %f' % (imagenameL,imagenameR,alt)
            entry = {'left': imagenameL, 'right':imagenameR,'alt':alt}
            if alt > 0.0:
                listofimg.append(entry)
newlist = sorted(listofimg, key=itemgetter('alt')) 
seq = [x['alt'] for x in newlist]
minAlt=min(seq)
maxAlt=max(seq) 
meanAlt=float(sum(seq))/len(seq) if len(seq) > 0 else float('nan')
print 'min alt ' + str(minAlt)
print 'max alt ' +  str(maxAlt)
print 'mean alt ' + str(meanAlt)
adir='stacked_cluster'
t="%s/%s/" %(gpath,adir)
if not os.path.exists(t):
        os.makedirs(t)
tmpf="%s/%s/clusterfile" %(gpath,adir)
tmpf2="%s/%s/clusterfile2" %(gpath,adir)
tmpf3="%s/%s/clusterfile3" %(gpath,adir)

tf=open("%s/%s/pixelstatsargs.txt" %(gpath,adir),'w')
tf.write('--mean AVGREPLACE --std STDREPLACE ')
tf.close()
tf=open("%s/%s/greyworldargs.txt" %(gpath,adir),'w')
tf.write(' --int 0.30 ')
tf.close()

f = open(tmpf, 'w')
f2 = open(tmpf2, 'w')
f3 = open(tmpf3, 'w')
i0= list(frange6(3.0,6.6,0.5))
for lowrange,hirange in itertools.izip(i0, itertools.islice(i0,1,None)):
    s="%s/%s/i%02.1f-%02.1f_cluster" %(gpath,adir,lowrange,hirange)


    if not os.path.exists(s):
        os.makedirs(s)

    print 'sdir ' + s
    clusterSet=Set()
    #print cmdtotal
    items = [ value for value in newlist if value['alt'] >= lowrange and value['alt'] < hirange ]
    print len(items)
    convertDone=(len(sys.argv) == 5)
    print convertDone
    for ist in items:
	limg=os.path.basename(ist['left']).replace('png','tif').strip(' \t\n\r')
	rimg=os.path.basename(ist['right']).replace('png','tif').strip(' \t\n\r')
	bname=os.path.splitext(limg)[0]
        #cluster=dcluster.get(bname)
	cluster = 1
        if cluster == None:
            continue
        clustername= '%d' %cluster
        clusterSet.add(clustername)
        sc=os.path.join(s,clustername)
        if not os.path.exists(sc):
            os.makedirs(sc)        
        if not convertDone:
            print ist['left']		
            print imcvpath
		# assumes image dir name is in ist (which is the case when using composite missions)
            #ll=os.readlink(os.path.join(gpath,os.path.dirname(ist['left']))).replace('PROCESSED_DATA','RAW_DATA').replace('_cv','')
            #rl=os.readlink(os.path.join(gpath,os.path.dirname(ist['right']))).replace('PROCESSED_DATA','RAW_DATA').replace('_cv','')
            ll=imcvpath.replace('PROCESSED_DATA','RAW_DATA').replace('_cv','')
            rl=imcvpath.replace('PROCESSED_DATA','RAW_DATA').replace('_cv','')
                      
            lraw=os.path.join(ll,limg)
            rraw=os.path.join(rl,rimg)

            

            loutput=os.path.join(sc,limg).strip(' \t\n\r')
            routput=os.path.join(sc,rimg).strip(' \t\n\r')
            print '%s - %s' % (lraw,loutput)
            print '%s - %s' % (rraw,routput)
            if not os.path.lexists(loutput):
                os.symlink(lraw,loutput)
            if not os.path.lexists(routput):
                os.symlink(rraw,routput)
        else:
            cv_dir="%s/%s/i%02.1f-%02.1f_cluster_stats_cv/%s" %(gpath,adir,lowrange,hirange,clustername)
            l_fin_output=os.path.join( cv_dir,limg).replace('tif','png')
            r_fin_output=os.path.join( cv_dir,rimg).replace('tif','png')
            outdir=sys.argv[3]
            lfinal=os.path.join(outdir,ist['left']).strip(' \t\n\r')
            rfinal=os.path.join(outdir,ist['right']).strip(' \t\n\r')
            outdir=os.path.dirname(lfinal)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            if not os.path.lexists(lfinal):
                os.symlink(l_fin_output,lfinal)
            if not os.path.lexists(rfinal):
                os.symlink(r_fin_output,rfinal)
            #print rraw
            #print lraw
    for cl in clusterSet:
        #sc=os.path.join(s,clustername)
        sc="%s/%s/i%02.1f-%02.1f_cluster/%s" %(gpath,adir,lowrange,hirange,cl)
        stats="%s/%s/i%02.1f-%02.1f_cluster_stats/%s" %(gpath,adir,lowrange,hirange,cl)
        cv_dir="%s/%s/i%02.1f-%02.1f_cluster_stats_cv/%s" %(gpath,adir,lowrange,hirange,cl)
        gw_dir="%s/%s/i%02.1f-%02.1f_gw/%s" %(gpath,adir,lowrange,hirange,cl)
        if not os.path.exists(stats):
            os.makedirs(stats)
        if not os.path.exists(cv_dir):
            os.makedirs(cv_dir)
        if not os.path.exists(gw_dir):
            os.makedirs(gw_dir)
#        cmd='calc_pixel_stats -s png -d %s %s\n' % (sc,stats)
        cmd='calc_pixel_stats -s tif -d %s %s\n' % (sc,stats)
        cmd2='convert_images --no-demosaic -s tif `cat pixelstatsargs.txt` -e %s -d %s %s\n' % (stats,sc,cv_dir)
        #cmd2='convert_images -s png `cat pixelstatsargs.txt` -e %s -d %s %s\n' % (stats,gw_dir,cv_dir)
        cmd3='convert_images -s tif  `cat greyworldargs.txt` -c GREYWORLD -d %s %s\n' % (s,gw_dir)

        f.write(cmd)
        f.flush()
        f2.write(cmd2)
        f2.flush()
        f3.write(cmd3)
        f3.flush()                    
f.close()
f2.close()
f3.close()
