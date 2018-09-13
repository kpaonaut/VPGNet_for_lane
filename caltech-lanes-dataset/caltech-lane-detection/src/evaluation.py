import os
import sys
import lane_extension_polyline_for_MultiNet as pp # post-processing main module

def main():
	sum = 0
	for i in range(0, 335):
		print "num:", i
		t, lines = pp.main('unity/%d.png'%i, True, False)
		sum += t
		os.system('cp output_log/labeled.png unity/output/driver_'+str(i)+'.png')
		os.system('cp output_log/threshold.png unity/output/inversed_'+str(i)+'.png')
	print sum / 335.0

if __name__ == "__main__":
	main()