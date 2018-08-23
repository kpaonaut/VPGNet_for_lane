%module IPM
%{
    #define SWIG_FILE_WITH_INIT
    struct scale_xy{
        double step_x, step_y;
    };
    scale_xy points_image2ground(int n, int *points_x, int m, int *points_y);
%}


%include "numpy.i"
%init %{
import_array();
%}

struct scale_xy{
    double step_x, step_y;
};
%apply (int DIM1, int* INPLACE_ARRAY1) {(int n, int *points_x), (int m, int *points_y)};
scale_xy points_image2ground(int n, int *points_x, int m, int *points_y);