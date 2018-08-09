import caffe
import lmdb
import numpy as np
import matplotlib.pyplot as plt
from caffe.proto import caffe_pb2

lmdb_file = "../LMDB_train"
lmdb_env = lmdb.open(lmdb_file)
lmdb_txn = lmdb_env.begin()
lmdb_cursor = lmdb_txn.cursor()
datum = caffe_pb2.Datum()
tot = 0

for key, value in lmdb_cursor:
    datum.ParseFromString(value)
    # print datum
    print key
    tot += 1
    if tot == 10:
        break

    label = datum.label
    data = caffe.io.datum_to_array(datum)
    # im = data.astype(np.uint8)
    # im = np.transpose(im, (2, 1, 0)) # original (dim, col, row)
    # print "label ", label

#     plt.imshow(im)
# plt.show()