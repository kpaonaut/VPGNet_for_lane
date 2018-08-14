# echo "WARNING FROM RUI! You are now training from a snapshot. If you want to train from scratch, delete the --snapshot statement!"
# ../../build/tools/caffe train --solver=./solver.prototxt --snapshot=./snapshots/split_iter_30000.solverstate >> ./output/output.log 2>&1
../../build/tools/caffe train --solver=./solver.prototxt >> ./output/output.log 2>&1
