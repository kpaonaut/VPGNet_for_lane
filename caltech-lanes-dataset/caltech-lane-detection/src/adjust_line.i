%module adjust_line
%{
    #define SWIG_FILE_WITH_INIT
    int* adjust(float k, float b, int y_size, int x_size, int downscale, int* img, int m, int n)
%}


%include "numpy.i"
%init %{
import_array();
%}

%apply (float* IN_ARRAY1, int DIM1, int DIM2) {(int n, int *points_x)};
int* adjust(float k, float b, int y_size, int x_size, int downscale, int* img, int m, int n)
