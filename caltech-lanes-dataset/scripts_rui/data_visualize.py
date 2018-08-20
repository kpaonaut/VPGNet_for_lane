import cv2
import string
import os

def color_options(x):
    return {
        1: (0, 255, 0), # green color
        2: (255, 0, 0), # blue
        3: (0, 0, 255), # red
    }[x]

def main():
    '''
    visualizes one instance of caltech lane detection data
    '''
    # img = cv2.imread('../cordova1/f00000.png')

    # f = open('../cordova1.txt', 'r')
    # label1_string = f.readline()
    # labels = label1_string.split()
    # i = 2
    # while i < len(labels) - 1:
    #     pt1 = (int(labels[i]), int(labels[i + 1]))
    #     pt2 = (int(labels[i + 2]), int(labels[i + 3]))
    #     bb_class = int(labels[i + 4])
    #     i += 5
    #     cv2.rectangle(img, pt1, pt2, color_options(bb_class), 2)
    # f.close()

    # cv2.imwrite('example.png', img)

    categories = ['cordova1', 'cordova2', 'washington2']
    for category in categories:
        pix = os.listdir('../train/'+ category)

        for pic in pix:

            if '.png' in pic:
                pic_to_vis = '../train/' + category + '/' + pic
                img = cv2.imread(pic_to_vis)
                f = open('../train/combined_labels.txt', 'r')
                tot = 0
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if pic_to_vis[len(pic_to_vis) - 15 : len(pic_to_vis) - 4] in line:
                        break
                label1_string = lines[i]
                labels = label1_string.split()
                i = 2
                print labels[0]
                tot = 0
                while tot < int(labels[1]):
                    tot += 1
                    pt1 = (int(labels[i]), int(labels[i + 1]))
                    pt2 = (int(labels[i + 2]), int(labels[i + 3]))
                    bb_class = int(labels[i + 4])
                    i += 5
                    cv2.rectangle(img, pt1, pt2, color_options(bb_class), 2)
                f.close()

                cv2.imwrite('annotated_data/' + category+ '/' + pic, img)



if __name__ == '__main__':
    main()