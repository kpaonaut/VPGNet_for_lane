%module adjust_line
%{
    #define SWIG_FILE_WITH_INIT
    void adjust(int *line, int line_dim1, int line_dim2, float k, float b, float downscale, int* img, int y_size, int x_size);
%}

%include "numpy.i"
%init %{
import_array();
%}

%apply (int* INPLACE_ARRAY2, int DIM1, int DIM2) {(int *line, int line_dim1, int line_dim2), (int* img, int y_size, int x_size)};
void adjust(int *line, int line_dim1, int line_dim2, float k, float b, float downscale, int* img, int y_size, int x_size);
