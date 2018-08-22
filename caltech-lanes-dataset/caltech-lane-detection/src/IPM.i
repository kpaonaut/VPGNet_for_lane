%module IPM
%{
    #define SWIG_FILE_WITH_INIT
    void points_image2ground(int n, int *points_x, int m, int *points_y);
%}


%include "numpy.i"
%init %{
import_array();
%}

%apply (int DIM1, int* INPLACE_ARRAY1) {(int n, int *points_x), (int m, int *points_y)};
void points_image2ground(int n, int *points_x, int m, int *points_y);