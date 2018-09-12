g++ IPM.cpp InversePerspectiveMapping.cc mcv.cc -o a -std=c++11 `pkg-config --libs opencv`
g++ -c -fPIC IPM.cpp InversePerspectiveMapping.cc mcv.cc -std=c++11 `pkg-config --libs opencv`
swig -c++ -python IPM.i
g++ -c -fPIC IPM_wrap.cxx  -I/usr/include/python2.7 -I/usr/lib/python2.7 `pkg-config --libs opencv`
g++ -shared -Wl,-soname,_IPM.so -o _IPM.so IPM.o IPM_wrap.o InversePerspectiveMapping.o mcv.o `pkg-config --libs opencv`

g++ adjust_line.cpp -o b
g++ -c -fPIC adjust_line.cpp
swig -c++ -python adjust_line.i
g++ -c -fPIC adjust_line_wrap.cxx  -I/usr/include/python2.7 -I/usr/lib/python2.7
g++ -shared -Wl,-soname,_adjust_line.so -o _adjust_line.so adjust_line.o adjust_line_wrap.o

g++ adjust_line_for_VPG.cpp -o b
g++ -c -fPIC adjust_line_for_VPG.cpp
swig -c++ -python adjust_line_for_VPG.i
g++ -c -fPIC adjust_line_for_VPG_wrap.cxx  -I/usr/include/python2.7 -I/usr/lib/python2.7
g++ -shared -Wl,-soname,_adjust_line_for_VPG.so -o _adjust_line_for_VPG.so adjust_line_for_VPG.o adjust_line_for_VPG_wrap.o