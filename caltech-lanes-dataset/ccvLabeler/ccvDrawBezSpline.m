function ha = ccvDrawBezSpline(spline, h, clr, width, ctrlPtClr)
% ccvDrawBezSpline draws a Bezier Spline onto the current figure
%
% INPUTS
% ------
% spline    - an array 3x2 (or 4x2) depending on the degree of the spline
% h         - [0.05] the interval to use for evaluation
% clr       - ['b'] The spline color
% width     - [3] the width of the line
% ctrlPtClr - [clr] the color to draw the control point
% 
% OUTPUTS
% -------
% ha        - array of handles to graphic objects
%
% EXAMPLE
% -------
% %to draw blue spline with red control points
% ccvDrawBezSpline(spline, 0.1, 'b', 5, 'r');
%
% See also ccvEvalBezSpline
%

if nargin<2 || isempty(h), h = .05; end;
if nargin<3 || isempty(clr), clr = 'b'; end;
if nargin<4 || isempty(width), width = 3; end;
if nargin<5 || isempty(ctrlPtClr)
    if length(clr)==1, ctrlPtClr = clr;
    else ctrlPtClr = clr(end); end;
end;


%get points on that spline
points = ccvEvalBezSpline(spline, h);

%loop on the points and draw
hold on;
ha = [];
for i=1:size(points, 1)-1
	ha = [ha plot([points(i,1), points(i+1,1)], ...
    [points(i,2), points(i+1,2)], clr, 'LineWidth', width)];
end;
%plot control points
ha = [ha plot(spline(:,1), spline(:,2), ['*' ctrlPtClr], 'MarkerSize', 5)];
hold off;
