%module IPM
%{
    #define SWIG_FILE_WITH_INIT
    #include <cstring>
    struct scale_xy{
        double step_x, step_y;
    };
    scale_xy points_image2ground(int n, float *points_x, int m, float *points_y);
    scale_xy points_ipm2image(int n, float *points_x, int m, float *points_y);
    void image_ipm(float *input, int h_in, int w_in, float *output, int h, int w);
%}


%include "numpy.i"
%init %{
import_array();
%}

struct scale_xy{
    double step_x, step_y;
};
%apply (int DIM1, float* INPLACE_ARRAY1) {(int n, float *points_x), (int m, float *points_y)};
scale_xy points_image2ground(int n, float *points_x, int m, float *points_y);
scale_xy points_ipm2image(int n, float *points_x, int m, float *points_y);

%apply (float* INPLACE_ARRAY2, int DIM1, int DIM2) {(float *input, int h_in, int w_in), (float *output, int h, int w)};
void image_ipm(float *input, int h_in, int w_in, float *output, int h, int w);