import cv2
import string

def color_options(x):
	return {
		1: (0, 255, 0),
		2: (255, 0, 0),
		3: (0, 0, 255),
	}[x]

def main():
	'''
	visualizes one instance of caltech lane detection data
	'''
	img = cv2.imread('../cordova1/f00000.png')
	pt1 = (41, 297)
	pt2 = (49, 289)

	f = open('../cordova1.txt', 'r')
	label1_string = f.readline()
	labels = label1_string.split()
	i = 2
	while i < len(labels) - 1:
		pt1 = (int(labels[i]), int(labels[i + 1]))
		pt2 = (int(labels[i + 2]), int(labels[i + 3]))
		bb_class = int(labels[i + 4])
		i += 5
		cv2.rectangle(img, pt1, pt2, color_options(bb_class), 2)

	cv2.imwrite('example.png', img)


if __name__ == '__main__':
	main()