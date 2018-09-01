import numpy as np
import IPM

def transform(x, y):
	"""
	Input: x, y, two lists/ndarrays of number, representing points' x and y coordinates by pixel in a 640*480 image
	Output: x, y, two numpy ndarays, the transformed coordinates in ground coordinate system, in mm
	"""

	# x, y must be transformed into float32!
	npx = np.array(x, dtype = np.float32)
	npy = np.array(y, dtype = np.float32)
	IPM.points_image2ground(npx, npy)
	return npx, npy

if __name__ == "__main__":
	print transform([400,400,400],[400,400,400])