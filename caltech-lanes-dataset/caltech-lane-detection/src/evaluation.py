import os
import sys
import lane_extension_polyline_for_MultiNet as pp # post-processing main module

def main():
	sum = 0
	for i in range(0, 335):
		print "num:", i
		t, lines = pp.main('unity/'+str(i)+'.png', True, True)
		sum += t
		#os.system('cp threshold.png unity/output/'+str(i)+'.png')
	print sum / 335.0

if __name__ == "__main__":
	main()