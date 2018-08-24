# This program executes the entire post-processing workflow for HD Map generation
# usage: python HDMap_pp_workflow.py img_before_pp.png img_after_pp.png
import os
import sys

def main():
	os.system("cp " + sys.argv[1] + " 1.png")
	os.system("python resize.py")
	os.system("./a")
	os.system("python lane_extension_polyline_for_MultiNet.py")
	os.system("cp gray_labeled.png " + sys.argv[2])

if __name__ == "__main__":
	main()