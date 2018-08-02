% 
% CCVLABELER is a small script to view and modify the labels in still iamges. 
% It is adpated here specifically to view/modify the labels of lanes for 
% the purpose of comparing performance of various algorithms.
% 
% There are 4 different clips included cordova1, cordova2, washington1, and
% washignton2. In each frame, the visible lanes are labeled according to 
% their type: solid white, broken white, solid yellow, broken yellow, and 
% double yellow. Every lane is represented by the four control points of 
% a Bezier spline. Every clip is contained in a separete folder, which 
% includes the frames (in *.png image files) and the labels file 
% (labels.ccvl).
% 
% Labels are not yet connected into tracks. If you happen to connect them
% into labels with this tool, please let me know :)
% 
% There are two matlab scripts:
% 
% ccvLabeler.m    - This is the viewer/editor of the labels
% ccvLabel.m      - This is the helping script to handle the labels structure
% 
% 
% Sample use:
% 
% % This will open the viewer on clip cordova1
% ccvLabeler('../cordova1/', 'labels.ccvl');
% 
% 
% AUTHOR  Mohamed Aly <malaa@caltech.edu>
% DATE    May 26, 2009
% 
