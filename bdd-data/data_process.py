import json
import os
import cv2

files = os.listdir()
#Read JSON data into the datastore variable
highway_pix = []
for filename in files:
    if filename[len(filename) - 4 : len(filename)] == 'json':
        with open(filename, 'r') as f:
            datastore = json.load(f)
        if datastore["attributes"]["weather"]["scene"] == "highway":
            name = datastore["name"]
            highway_pix.append(name)
            pic = cv2.imread(name+'.jpg')
            for object in datastore["frames"][0]["objects"]:
                if object["category"][0:4] == "lane" and object["category"][5] != 'c': # a lane, but not a crosswalk
                    lane = object["poly2d"]
                    len(lane)
                    pt1 = lane[0][0:1]
                    pt2 = lane[1][0:1]

#Use the new datastore datastructure
print datastore["office"]["parking"]["style"]