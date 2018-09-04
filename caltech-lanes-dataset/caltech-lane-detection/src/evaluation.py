import os
import sys
import lane_extension_polyline_for_MultiNet as pp # post-processing main module

def main():
	for i in range(0, 335):
		print "num:", i
		lines = pp.main('unity/'+str(i)+'.png','.', False, None)
		os.system('cp threshold.png unity/output/'+str(i)+'.png')

if __name__ == "__main__":
	main()