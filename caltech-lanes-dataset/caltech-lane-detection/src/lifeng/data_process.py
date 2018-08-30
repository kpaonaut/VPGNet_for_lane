import os

pix = os.listdir('.')

tot = 0
for pic in pix:
	if pic[len(pic) - 3 : len(pic)] == 'png':
		os.rename(pic, str(tot)+'.png')
		tot += 1