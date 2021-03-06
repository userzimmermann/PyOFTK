#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt   # For plotting graphs.
import numpy as np
import subprocess                 # For issuing commands to the OS.
import os
import sys                        # For determining the Python version.

import Image
import time
import fkabcd


not_found_msg = """
The mencoder command was not found;
mencoder is used by this script to make an avi file from a set of pngs.
It is typically not installed by default on linux distros because of
legal restrictions, but it is widely available.
"""

try:
    subprocess.check_call(['mencoder'])
except subprocess.CalledProcessError:
    print "mencoder command was found"
    pass # mencoder is found, but returns non-zero exit as expected
    # This is a quick and dirty check; it leaves some spurious output
    # for the user to puzzle over.
except OSError:
    print not_found_msg
    sys.exit("quitting\n")

print 'Initializing data set...'   # Let the user know what's happening.


# Number of frames we want in the movie.
step = 50 
dz = 0.5/step
focalLenght = 0.1
champ_in = Image.open("anneaux_mince.gif")
intensiteArchive = np.zeros([512,512,step])
champ_in_fld = np.zeros([1024,1024], complex)
tampon = list(champ_in.getdata())

for x in range(1024):
	for y in range(1024):
		champ_in_fld[x,y] = float(tampon[(1024*y)+x])

t1 = time.time()

# Premier step a 0.2
fkabcd.Prop(champ_in_fld, 632e-9, 0.0000116, 1.0-(0.2/focalLenght), focalLenght, -1.0/focalLenght, 0.0, 1.0-(0.2/focalLenght), focalLenght, -1.0/focalLenght, 0.0)

# Step de 0.2 a 0.7
for i in range(step):
	fkabcd.Prop(champ_in_fld, 632e-9, 0.000116, 1.0-(dz/focalLenght), focalLenght, -1.0/focalLenght, 0.0, 1.0-(dz/focalLenght), focalLenght, -1.0/focalLenght, 0.0)
	intensiteArchive[:,:,i] = pow(abs(champ_in_fld),2)[256:512+256,256:512+256]

# Bench
elapsed = time.time() - t1
print "Processing time: " + str(elapsed) + " secondes" + "(" + str(elapsed/60) + " minutes)"

print 'Done.'    

for i in range(step) :
	plt.imshow(intensiteArchive[:,:,i])
	filename = "./output/" + str('%03d' % i) + '.png'
	plt.savefig(filename, dpi=100)
	print 'Wrote file', filename
	plt.clf()

#
# Now that we have graphed images of the dataset, we will stitch them
# together using Mencoder to create a movie.  Each image will become
# a single frame in the movie.
#
# We want to use Python to make what would normally be a command line
# call to Mencoder.  Specifically, the command line call we want to
# emulate is (without the initial '#'):
# mencoder mf://*.png -mf type=png:w=800:h=600:fps=25 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o output.avi
# See the MPlayer and Mencoder documentation for details.
#

command = ('mencoder',
           'mf://output/*.png',
           '-mf',
           'type=png:w=800:h=600:fps=10',
           '-ovc',
           'lavc',
           '-lavcopts',
           'vcodec=mpeg4',
           '-oac',
           'copy',
           '-o',
           'output.avi')


print "\n\nabout to execute:\n%s\n\n" % ' '.join(command)
subprocess.check_call(command)

print "\n\n The movie was written to 'output.avi'"

print "\n\n You may want to delete *.png now.\n\n"


