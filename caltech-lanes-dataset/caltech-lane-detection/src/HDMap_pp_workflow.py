# This program executes the entire post-processing workflow for HD Map generation
# usage: python HDMap_pp_workflow.py img_before_pp.png img_after_pp.png
import os
import sys
import lane_extension_polyline_for_MultiNet as pp # post-processing main module

def main():
	# substitute sys.argv[1] with file name
	lines = pp.main(sys.argv[1], '.', True) # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]; "True": suppress output. use "None" if want outputs

if __name__ == "__main__":
	main()