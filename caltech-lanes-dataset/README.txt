Caltech Lanes Dataset
---------------------

This is the dataset used to evaluate the algorithm described in [1]. The package
includes 4 clips taken on two streets in Pasadena, CA in the summer of 2007. It
consists of 1225 frames divided into 4 clips, in addition to the annotations
of the lanes. The lanes labels are useful for comparing and quantifying 
performance of different lane detection algorithms.


Contents
--------

Cordova1/ 		- frames and labels for clip cordova1. Includes 250 frames.
Cordova2/    	- frames and labels for clip cordova2. Includes 406 frames.
Washington1/	- frames and labels for clip washington1. Includes 337 frames.
Washington2/ 	- frames and labels for clip washington2. Includes 232 frames.
lists/				- includes text files containing lists of images in each direcotry,
								in addition to list.txt that includes a list of all images.

Each directory includes the frames in *.png format, the labels file labels.ccvl,
and a list.txt file containing the list of images.
              
References
----------
[1] Mohamed Aly, Real time Detection of Lane Markers in Urban Streets. 
  IEEE Intelligent Vehicles Symposium, Eindhoven, The Netherlands, June 2008.              


Author
------
Mohamed Aly <malaa@caltech.edu>
June 5, 2009.

