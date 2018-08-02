function ccvLabeler(lPath, lFile)
% CCVLABELER views/changes labels in still images. Labels can be anything
% from splines, circles, squares, or arbitrary closed polygons.
% 
% INPUTS
% ------
% lPath     - the path to the labels file
% lFile     - the file containing the labels
% 
% OUTPUTS
% -------
%
% See also ccvLabel ccvEvalBezSpline ccvDrawBezSpline
% 
% AUTHOR    - Mohamed Aly <malaa@caltech.edu>
% DATE      - May 26, 2009
%

addpath(genpath('..'));

%global variables start with 'g'
[gLabelData, gCurIndex, gPath, gFile, gCurIm, gState, ...
  gCurLabel, gCurPoint, gAddLabel, gW, gH, gLabelsHandles, ...
  gAddHandles] = deal([]);

%handles of some ui controls
[hFig, hAxis, hTbar, hCurPoint, hCurFrameTxt1, hCurFrameTxt2, hCurFrame, ...
  hCurLabelTxt, hCurLabelSubtype, hCurLabelTxt2, hCurLabelObject, ...
  hCurState, hLabelTypes, hLabelTypesTxt, hDelObject] = deal(0);

%
% Edit types of labels here to suit your needs
% 

%types of labels
gLabelTypes = {'spline', 'line', 'rect', 'polygon', 'point'};
%number of points per label, Inf for arbitrary number of points
gLabelTypesNpoints = [4, 2, 2, Inf, 1];
%default type when adding new labels
gLabelAddType = 1;
%subtypes for every type e.g. for lanes there are broken white, solid
%white, double yellow, ... etc.
gLabelSubtypes = {{'bw', 'sw', 'dy', 'by', 'sy'}, {'sw'}, {'y'}, {'m'}, {'y'}};
%Colors of every label subtype
gLabelSubtypesClr = {{'b', 'k', 'y', 'c', 'm'}, {'b'}, {'y'}, {'m'}, {'y'}};

%default for adding label
gAddLabel = ccvLabel('createLabel', [], gLabelTypes{gLabelAddType}, ...
            gLabelSubtypes{gLabelAddType}{1}, []);

%colors for selected labels and points
gSelLabelClr = 'r';
gSelPointClr = 'g';
gTxtClr = 'y';

%extensions of images
gImExt = {'*.png'};

%default width and height
gW = 640; gH = 480;

%create the layout
createLayout;

%initial state
gState = 'STATE_NORMAL';

%check default path
if ~exist('lPath','var'), lPath = '../../linePerceptor/clips/washington2/'; end;
if ~exist('lFile','var'), lFile = 'labels.ccvl'; end;

%open labels file
open(lPath, lFile);

  function createLayout()
    %create the figure
    w=640; h=480;
    scrSize = get(0, 'ScreenSize');
    figPos = [1 1 scrSize(3:4)-10];
    hFig = figure('Units','Pixels', 'MenuBar','none', 'Toolbar','none',...
      'Position',figPos, 'Visible','off', ...
      'Name','Caltech CV Labeler', 'NumberTitle','off', ...
      'WindowButtonMotionFcn',@motionCb, 'WindowButtonDownFcn',@downCb, ...
      'KeyPressFcn',@keyPressCb, 'ResizeFcn',@resizeCb, 'Color','k');

    %left and bottom of axis
    axl = (scrSize(3)-w)/2; 
    axb = (scrSize(4)-h)/2;
    %create the axis component
    hAxis = axes('Parent',hFig, 'Units','Pixels', ...
      'Position',[axl axb  w h]);
    set(hFig, 'CurrentAxes', hAxis);
    axis off;
    
    
    %create the caption above the image
    hCurFrameTxt1 = uicontrol(hFig, 'style','text', 'String', 'Frame', ...
      'Visible','Off', 'Position',[axl axb+h+5 50 15], ...
      'HorizontalAlignment','Left', 'Backgroundcolor','k', ...
      'ForegroundColor','w');
    hCurFrameTxt2 = uicontrol(hFig, 'style','text', 'String', '', ...
      'Visible','Off', 'Position',[axl+100 axb+h+5 400 15], ...
      'HorizontalAlignment','Left', 'Backgroundcolor','k', ...
      'ForegroundColor','w');
    hCurFrame = uicontrol(hFig, 'style','popupmenu', 'String','1', ...
      'Visible','Off', 'Position',[axl+50 axb+h+7 50 15], ...
      'HorizontalAlignment','Center', 'Backgroundcolor','k', ...
      'ForegroundColor','w', 'Callback',@selectFrameCb);
    
    %crreate text for the current function
    hCurState = uicontrol(hFig, 'style','text', 'String', '', ...
      'Visible','off', 'Position',[axl+w-125 axb+h+5 125 15], ...
      'HorizontalAlignment','Center', 'Backgroundcolor','k', ...
      'ForegroundColor','r');    

    %create the current label text
    hCurLabelTxt = uicontrol(hFig, 'style','text', 'String', '', ...
      'Visible','off', 'Position',[axl axb-17 200 15], ...
      'HorizontalAlignment','Left', 'Backgroundcolor','k', ...
      'ForegroundColor','w');
    hCurLabelSubtype = uicontrol(hFig, 'style','popupmenu', ...
      'String','', 'Visible','Off', ...
      'Position',[axl+205 axb-15 100 15], ...
      'HorizontalAlignment','Center', 'Backgroundcolor','k', ...
      'ForegroundColor','w', 'Callback',@selectLabelSubtypeCb);
    hCurLabelTxt2 = uicontrol(hFig, 'style','text', 'String',' & object=', ...
      'Visible','off', 'Position',[axl+310 axb-17 70 15], ...
      'HorizontalAlignment','Left', 'Backgroundcolor','k', ...
      'ForegroundColor','w');
    hCurLabelObject = uicontrol(hFig, 'style','popupmenu', ...
      'String',{'None','Add'}, 'Visible','Off', ...
      'Position',[axl+380 axb-15 50 15], ...
      'HorizontalAlignment','Center', 'Backgroundcolor','k', ...
      'ForegroundColor','w', 'Callback',@selectLabelObjectCb);
    hDelObject = uicontrol(hFig, 'style','pushbutton', 'String','Delete Object', ...
      'Visible','Off', 'Position',[axl+440 axb-25 100 25], ...
      'HorizontalAlignment','Center', 'Backgroundcolor','k', ...
      'ForegroundColor','w', 'Callback',@deleteObjectCb);
    
    %create the (x,y) text
    hCurPoint = uicontrol(hFig, 'style','text', 'String', '', ...
      'Visible','off', 'Position',[axl+w-100 axb-15 100 15], ...
      'HorizontalAlignment','right', 'Backgroundcolor','k', ...
      'ForegroundColor','w');

    %Add label types
    hLabelTypesTxt = uicontrol(hFig, 'style','text', 'String', 'Label Type', ...
      'Visible','off', 'Position',[axl+w-200 axb-32 75 15], ...
      'HorizontalAlignment','Left', 'Backgroundcolor','k', ...
      'ForegroundColor','w');
    hLabelTypes = uicontrol(hFig, 'style','popupmenu', 'String',gLabelTypes, ...
      'Visible','Off', 'Position',[axl+w-125 axb-30 125 15], ...
      'HorizontalAlignment','Center', 'Backgroundcolor','k', ...
      'ForegroundColor','w', 'Callback',@selectLabelTypeCb);
    
    
    %load icons
    icons = load('ccvLabelerIcons.mat');

    %create the toolbar
    hTbar = uitoolbar('Parent', hFig);
    %create the buttons
    btnIcons = {'iconNew', 'iconOpen', 'iconSave', 'iconLeft', ...
      'iconRight', 'iconSelect', 'iconMove', 'iconEdit', 'iconCopy', ...
      'iconDelete', 'iconAdd', 'iconHide'};
    btnToolTips = {'New', 'Open', 'Save', 'Left', 'Right', 'Select', ...
      'Move', 'Edit', 'Copy', 'Delete', 'Add', 'Hide'};
    btnCbs = {@newCb, @openCb, @saveCb, @navCb, @navCb, @stateCb, ...
      @stateCb, @stateCb, @stateCb, @stateCb, @stateCb, @stateCb};
    btnPush = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0];
    btnData = {[], [], [], -1, 1, 'STATE_SELECT', 'STATE_MOVE', ...
      'STATE_EDIT', 'STATE_COPY', 'STATE_DELETE', ...
      'STATE_ADD', 'STATE_HIDE'};
    for i=1:length(btnCbs)
      if btnPush(i)
        uipushtool('Parent',hTbar, 'CData',icons.(btnIcons{i}), ...
          'TooltipString',btnToolTips{i}, 'ClickedCallback',btnCbs{i}, ...
          'UserData',btnData{i});
      else
        uitoggletool('Parent',hTbar, 'CData',icons.(btnIcons{i}), ...
          'TooltipString',btnToolTips{i}, 'ClickedCallback',btnCbs{i}, ...
          'UserData',btnData{i});
      end;
    end;    
        
    %position the controls
    positionLayout(figPos);
    
    %set visible
    set(hFig, 'Visible','on');
  end

  %Callbck for window resize
  function resizeCb(h, event)%#ok<INUSD>
    %get the figure position
    pos = get(h, 'Position');
    %position the layout
    positionLayout(pos);
  end

  %Positions the layout given the figure position
  function positionLayout(figPos)
    %left and bottom of axis
    axl = (figPos(3)-gW)/2; 
    axb = (figPos(4)-gH)/2;
    
    %position controls
    set(hAxis, 'Position',[axl axb  gW gH]);
    
    %the caption above the image
    set(hCurFrameTxt1, 'Position',[axl axb+gH+5 50 15]);
    set(hCurFrameTxt2, 'Position',[axl+100 axb+gH+5 400 15]);
    set(hCurFrame, 'Position',[axl+50 axb+gH+7 50 15]);
    
    %text for the current function
    set(hCurState, 'Position',[axl+gW-125 axb+gH+5 125 15]);    

    %the current label text
    row = 30;
    set(hCurLabelTxt, 'Position',[axl axb-row-2 200 15]);
    set(hCurLabelSubtype, 'Position',[axl+205 axb-row 100 15]);
    set(hCurLabelTxt2, 'Position',[axl+310 axb-row-2 70 15]);
    set(hCurLabelObject, 'Position',[axl+380 axb-row 50 15]);
    set(hDelObject, 'Position',[axl+440 axb-row-10 100 25]);
    
    %the (x,y) text
    row = 15;
    set(hCurPoint, 'Position',[axl+gW-100 axb-row 100 15]);

    %Add label types
    row = 55;
    set(hLabelTypesTxt, 'Position',[axl axb-row 75 15]); % [axl+gW-200 axb-32 75 15]);
    set(hLabelTypes, 'Position',[axl+125 axb-row-2 125 15]); %[axl+gW-125 axb-30 125 15]);    
  end

  %Callback for Open Button
  function openCb(h, event) %#ok<INUSD>
    %get the file to open
    [file, path] = uigetfile({'*.ccvl', 'CCV Labeler files (*.ccvl)'; ...
      '*.mat', 'MAT files (*.mat)'}, 'Open a saved file', ...
      '../../linePerceptor/clips/cordova1/');
    %open
    if ~isempty(file) && ~isempty(path)
      open(path, file);
    end;
  end

  %Callback for Save Button
  function saveCb(h, event) %#ok<INUSD>
    if isempty(gPath) || isempty(gFile)
      %get the file to open
      [file, path] = uiputfile({'*.ccvl', 'CCV Labeler files (*.ccvl)'}, ...
        'Save ...', 'labels.ccvl');
      gPath =path;  gFile = file;
    end;
    %open
    saveFile();
  end

  %Callback for New Button
  function newCb(h, event) %#ok<INUSD>
    if ~isempty(gPath) && ~isempty(gFile)
      %make sure he doesn't want to save
      res = questdlg('Do you want to save first?', '', 'Yes');
      %check response
      if strcmp(res, 'Yes'), saveCb();  
      elseif strcmp(res,'No'), new();
      end;
    else
      new();
    end;
  end

  %Callback for Select Label Type 
  function selectLabelTypeCb(h, event) %#ok<INUSD>
    %set the current label type
    gLabelAddType = get(h, 'Value');
    gAddLabel = ccvLabel('createLabel', [], gLabelTypes{gLabelAddType}, ...
      gLabelSubtypes{gLabelAddType}{1}, []);
    gLabelsHandles{length(gLabelsHandles) + 1} = [];
    %update status
    set(hCurState, 'String',['ADD ' gAddLabel.type]);
  end

  %Callback for Select Label Subtype 
  function selectLabelSubtypeCb(h, event) %#ok<INUSD>
    %is something is selected
    if ~isempty(gCurLabel)
      %get indices of types and subtypes
      label = ccvLabel('getLabel', gLabelData, gCurIndex, gCurLabel);
      typeInd = getTypeInds(label);
      %get selected subtype
      newSubtype = get(h, 'Value');
      %set
      gLabelData = ccvLabel('updateLabel', gLabelData, gCurIndex, ...
        gCurLabel, nan, nan, gLabelSubtypes{typeInd}{newSubtype});
%       gLabelData.frames(gCurIndex).labels(gCurLabel).subtype = gLabelSubtypes{typeInd}{newSubtype};
      %refresh
%       refresh(0);
      refreshCurLabel();
    end;
  end

  %Callback for Select Label Object
  function selectLabelObjectCb(h, event) %#ok<INUSD>
    %is something is selected
    if ~isempty(gCurLabel)
      %get selected index
      index = get(h, 'Value');
      %get the objects in the dropbox
      objs = get(h, 'String');      
      %switch
      switch index
        %none, then put []
        case 1, obj = [];
        %new, then add another object
        case 2, 
          %add a new object
          [gLabelData, obj] = ccvLabel('addObj', gLabelData);
%           obj = length(get(h,'String')) - 1;
%           %add to list of objects
%           gLabelData.objects = [gLabelData.objects struct('id', obj)];
          %fill objects dropbox
          fillObjects();
          %select the latest object
          set(h, 'Value',length(objs)+1);
        %otherwise, just set the object
        otherwise, obj = str2double(objs{index});
      end; %switch
      
      %set object of the current label
      gLabelData = ccvLabel('updateLabel', gLabelData, gCurIndex, ...
        gCurLabel, nan, nan, nan, obj);
%       gLabelData.frames(gCurIndex).labels(gCurLabel).obj = obj;
      
      %refresh
%       refresh(0);
      refreshCurLabel();
    end;
  end

  %Callback for Delete Object
  function deleteObjectCb(h, event) %#ok<INUSD>
    %get selected index
    index = get(hCurLabelObject, 'Value');
    %get the objects in the dropbox
    objs = get(hCurLabelObject, 'String');      
    %check it's a valid object i.e. not first two indices
    if index>2
      %get the object to detete
      objId = str2double(objs{index});
      
      %delete that object
      gLabelData = ccvLabel('removeObj', gLabelData, objId);
      
      %refill the objects dropbox
      fillObjects();
    
      %refresh
%       refresh(0);
      refreshCurLabel();
      
%       %show the label
%       showCurLabel('on');

    end;
  end

  %Callback for Select frame box
  function selectFrameCb(h, event) %#ok<INUSD>
    %get the current selected value
    f = get(h, 'Value');
    %set the frame
    selectFrame(f);
  end
  
  %Callback for mouse motion over the image
  function motionCb(h, event) %#ok<INUSD>
    %check if we have a valid index
    showp = 0;
    if ~isempty(gCurIndex)
      %get current point
      cp = get(hAxis, 'CurrentPoint'); 
      x = cp(1,1); y = cp(1,2);
%       [h, w, rgb] = size(gCurIm); %#ok<NASGU>
      %ceck if within the image
      if x>0 && x<=gW && y>0 && y<=gH, showp = 1; end;
    end;
    if showp
      %display
      set(hCurPoint, 'String',sprintf('[%.2f,%.2f]', x,y), 'Visible','on');
    else
      set(hCurPoint, 'Visible','off');
    end;
  end

  %Callback for button down that provides shortcuts
  function keyPressCb(h, event) %#ok<INUSL>
    switch event.Key
      case 's', state = 'STATE_SELECT';
      case 'm', state = 'STATE_MOVE';
      case 'e', state = 'STATE_EDIT';
      case 'c', state = 'STATE_COPY';
      case 'd', state = 'STATE_DELETE';
      case 'a', state = 'STATE_ADD';
      case 'h', state = 'STATE_HIDE';
      otherwise, state = '';
    end; %switch
    h = getTbButtonHandle(state);
    
    %toggle state
    if ~isempty(h)
      state = 'on';
      if strcmp(get(h,'State'), 'on'), state = 'off'; end;
      set(h, 'State',state);
      stateCb(h, []);
    end;
  end

  %get handle of toolbar button with given state
  function h = getTbButtonHandle(state)
    %get handles of the buttons
    handles = get(hTbar, 'Children');
    %loop and compare
    h = [];
    for i=1:length(handles)
      if strcmp(get(handles(i), 'UserData'), state)
        h = handles(i); return;
      end;
    end;
  end

  %Callback for mouse down over the image
  function downCb(h, event) %#ok<INUSD>
    if isempty(gCurIndex), return; end;
    
    %get current point
    cp = get(hAxis, 'CurrentPoint'); 
    x = min(max(cp(1,1), 1), gW); 
    y = min(max(cp(1,2), 1), gH);

    %right button was pressed
    rb = strcmp(get(h,'SelectionType'), 'alt');
    
    %get the labels
    labels = ccvLabel('getLabel', gLabelData, gCurIndex); 
    
    %refresh
    redraw = 1;

    %select
    if rb && ~any(strcmp(gState, {'STATE_HIDE', 'STATE_NORMAL', 'STATE_ADD'})) ...
        || (~rb && strcmp(gState, 'STATE_SELECT'))
      selectLabel([x y]);
%       %get closest label
%       [gCurLabel, cPoint, gCurPoint, dist] = getClosestPoint([x y]);
%       %check the distance
%       if dist>15, gCurLabel = []; end;
      
    %add
    elseif strcmp(gState, 'STATE_ADD')
      %unselect selected label
      if ~isempty(gCurLabel)
        showCurLabel('off');
        refreshCurLabel(0);
      end;
      %add the point
      x = min(max(x, 1), gW);
      y = min(max(y, 1), gH);
      gAddLabel.points = [gAddLabel.points; x y];
      npoints = size(gAddLabel.points, 1);
      %plot a line to the new point
      hold on;
      gAddHandles = [gAddHandles plot(gAddLabel.points(max(1,npoints-1):npoints,1), ...
        gAddLabel.points(max(1,npoints-1):npoints,2), ...
        ['-*' gSelLabelClr])];
      hold off;

      %check the number of points so far, or if right-clicked when
      %entering a 'region'
      if npoints>=gLabelTypesNpoints(gLabelAddType) || ...
          (rb && isinf(gLabelTypesNpoints(gLabelAddType))) 
        %add the new label to the list of labels
        [gLabelData, gCurLabel] = ccvLabel('addLabel', gLabelData, ...
          gCurIndex, gAddLabel);
        gCurPoint = size(gAddLabel.points,1);
%         selectLabel([x y]);
%         labels = [labels gAddLabel];
        %clear the label
        gAddLabel.points = [];
        %remove drawn lines
        delete(gAddHandles);
        gAddHandles = [];
      else
        redraw = 0;
      end;      
      
    elseif ~rb && ~isempty(gCurLabel)
      switch gState            
        %Move
        case 'STATE_MOVE'
          %move the selected point to the current point, and translate the
          %rest of the points
          label = labels(gCurLabel);
          diff = [x y] - label.points(gCurPoint,:);
          label.points = label.points + repmat(diff, size(label.points,1),1);
          gLabelData = ccvLabel('updateLabel', gLabelData, gCurIndex, ...
            gCurLabel, label);
%           labels(gCurLabel).points = labels(gCurLabel).points + ...
%             repmat(diff, size(labels(gCurLabel).points,1),1);

        %Edit
        case 'STATE_EDIT'
          %move the selected point to the current point
          labels(gCurLabel).points(gCurPoint,:) = [x y];
          gLabelData = ccvLabel('updateLabel',gLabelData,gCurIndex, ...
            gCurLabel, labels(gCurLabel));

        %Copy
        case 'STATE_COPY'
          %copy the label at this location
          newLabel = labels(gCurLabel);
          newLabel.points = newLabel.points + ...
            repmat([x y] - newLabel.points(gCurPoint,:), ...
              size(newLabel.points,1), 1);
          %put at the end of labels
%           labels = [labels newlabel];
          gLabelData = ccvLabel('addLabel', gLabelData, gCurIndex, newLabel);
          %add another handles
          gLabelsHandles{length(gLabelsHandles)+1} = drawLabel(newLabel, 0);
         
        %Delete
        case 'STATE_DELETE'
          %detele the current label
%           labels(gCurLabel) = [];
          gLabelData = ccvLabel('removeLabel', gLabelData, gCurIndex, ...
            gCurLabel);
          %remove label
          delete(gLabelsHandles{gCurLabel});
          gLabelsHandles(gCurLabel) = [];
          %clear
          gCurLabel = [];          
      end; %switch
    end; %if
    
%     %save the labels
%     gLabelData.frames(gCurIndex).labels = labels;
    
    %update display
%     if redraw, refresh(0); end;
    refreshCurLabel();
    showCurLabel('on');
%     if ~isempty(gCurLabel)
%       %mark the label as selected
%       label = ccvLabel('getLabel', gLabelData, gCurIndex, gCurLabel);
%       drawLabel(label, 1);
%       drawPoint(label.points(gCurPoint,:), gSelPointClr);
% 
%       %display info about the current selected label
% %       showCurLabel('on');
%       set(hCurLabelTxt, 'String',sprintf('Selected type=%s & subtype=', ...
%         labels(gCurLabel).type));
%     else
%       showCurLabel('off');
%     end;

  end

  %Callback for left/right Button
  function navCb(h, event) %#ok<INUSD>
    %get the value
    v = get(h, 'UserData');
    %advance
    selectFrame(gCurIndex + v);
  end

  %Callback for State changing buttons
  function stateCb(h, event) %#ok<INUSD>
    %set state
    bstate = get(h, 'State');
    newState = get(h, 'UserData');
    switch bstate
      case 'on'
        %if turning off Add state, then disable the type dropbox
        if strcmp(gState, 'STATE_ADD')
          showLabelTypes('off');
        end;

        %check if current state allows chagne of state
        if strcmp(gState,'STATE_HIDE')
          %this doesnt allow change of state, so keep the current state
          set(h,'State','off');
          return;
        else
          %set new state
          gState = newState;
        end;
        
            
        %uncheck the rest of buttons
        for i=get(get(h,'Parent'), 'Children')'
          if i~=h && strcmp(get(i,'Type'),'uitoggletool')
            set(i, 'State','off');
          end;
        end;
        
        %update status texts for some buttons
        switch gState
          case 'STATE_ADD',     
            str = ['ADD ' gAddLabel.type];
            %enable the dropbox
            showLabelTypes('on');
            %reset selection
            resetSelection();
          case 'STATE_MOVE',    str = 'MOVE';
          case 'STATE_EDIT',    str = 'EDIT';
          case 'STATE_COPY',    str = 'COPY';
          case 'STATE_DELETE',  str = 'DELETE';
          case 'STATE_HIDE',    
            str = 'HIDE';
            %hide labels
            refresh(0,1);
          case 'STATE_SELECT',  str = 'SELECT';
        end;
        
      %turning off a button
      case 'off'
        %turn off if the same button
        if strcmp(newState, gState)
          %check state
          switch gState
            case 'STATE_ADD'
              %hide dropbox
              showLabelTypes('off');
            case 'STATE_SELECT'
              %reset selection
              resetSelection();
            case 'STATE_HIDE'
              %show labels
              refreshLabels();
          end
          %normal state
          gState = 'STATE_NORMAL';
          %clear text
          str = '';
        end;
    end;
    
    %status
    set(hCurState, 'String', str);

    %reset stuff
%     resetSelection();
%     refresh(0);    
  end

  %show/hide label subtypes dropbox
  function showCurLabel(show)
    %make sure there is something to show
    if strcmp(show,'on') && ~isempty(gCurLabel)
      %get label type of selected label
      label = ccvLabel('getLabel',gLabelData, gCurIndex, gCurLabel);
      [typeInd, subtypeInd] = getTypeInds(label);
      
      %fill in the dropbox for subtypes
      set(hCurLabelSubtype, 'String',gLabelSubtypes{typeInd}, ...
        'Value',subtypeInd);
      
      %set object combo
      if isempty(label.obj)
        obj = 1;
      else
        obj = find(strcmp(num2str(label.obj), ...
          get(hCurLabelObject,'String')));
      end;
      if ~isempty(obj), set(hCurLabelObject,'Value',obj); end;
      
      %set text
      set(hCurLabelTxt, 'String', ...
        sprintf('Selected type=%s & subtype=', label.type));

    else
      show = 'off';
    end;
    
    set(hCurLabelTxt, 'Visible',show);
    set(hCurLabelTxt2, 'Visible',show);
    set(hCurLabelSubtype, 'Visible',show);
    set(hCurLabelObject, 'Visible',show);
    set(hDelObject, 'Visible',show);
    
  end

  %show/hide label types dropbox
  function showLabelTypes(show)
    set(hLabelTypesTxt, 'Visible',show);
    set(hLabelTypes, 'Visible',show);
  end

  %fill the frames drop box
  function fillFrames()
    if ~isempty(gLabelData)
      %get number of frames
      nframes = ccvLabel('nFrames',gLabelData); 
      %fill box
      set(hCurFrame, 'String',num2str((1:nframes)'));
    end;
  end

  %fill the frames drop box
  function fillObjects()
    if ~isempty(gLabelData)
      %str
      str = {'None', 'Add'};
      
      %get number of frames
      if isempty(gLabelData.objects), objs = [];
      else objs = num2str(ccvLabel('getObjIds',gLabelData)'); 
      end;
      if ~isempty(objs)
        str = [str mat2cell(objs, ones(1,size(objs,1)), size(objs,2))']; 
      end;
      
      %fill box
      set(hCurLabelObject, 'String',str);
    end;
  end  

  %select frame
  function selectFrame(f)
    %check bounds
    nf = ccvLabel('nFrames',gLabelData);
    if ~isempty(f) && f>=1 && f<=nf
      %set frame
      gCurIndex = f;
      %check if to set the dropbox or not
      set(hCurFrame, 'Value',f);
      %refresh
      refresh(1);
      resetSelection();
    end
  end

  %get the closest point
  function [index, cPoint, cPointIndex dist] = getClosestPoint(inPoint)
  % index: the index of the closest object
  % cPoint: the closest point
  % dist: the distance to the closest point
    %loop and compute distance
    labels = gLabelData.frames(gCurIndex).labels;
    for i=1:length(labels)
      d = labels(i).points - repmat(inPoint, size(labels(i).points,1), 1);
      [dist(i), id(i)] = min(sqrt(sum(d .^ 2, 2)));
    end;
    %get the closest object and point
    [dist, index] = min(dist);
    cPointIndex = id(index);
    cPoint = labels(index).points(id(index),:);
  end
  
  %opens a saved file
  function open(path, file)
    %load the opened file
    gLabelData = ccvLabel('read', [path file]);
    if isempty(gLabelData), return; end;
%     t = load([path, file], '-mat');
    %set the global data
%     gLabelData = t.labelData; 
    gPath = path;    gFile = file;

    %fill dropbox
    fillFrames();
    fillObjects();
    %select first frame
%     set(hCurFrame, 'Value',1);
    selectFrame(1);
  end

  %saves the current file
  function saveFile()
    %save the current file
%     labelData = gLabelData; %#ok<NASGU>
%     save([gPath gFile], 'labelData', '-mat');
    ccvLabel('write', [gPath gFile], gLabelData);
  end

  %creates a new file
  function new()
    %asks for the directory ocntaining the images
    gPath = [uigetdir '/'];
    gFile = 'labels.ccvl';
    gCurIndex = [];
    %create new label data structure
    gLabelData = ccvLabel('create');
    
    %loop on image extensions
    for ex=1:length(gImExt)
      %get images with this extension
      ims = dir([gPath '/' gImExt{ex}]);
      %add frames for them
      for im=1:length(ims)
        %create a frame
%         frame = ccvLabel('createFrame', ims(im).name);
        gLabelData = ccvLabel('addFrame', gLabelData, ims(im).name);
      end;      
    end;
    
    %refresh
    fillFrames();
    fillObjects();
    %select first frame
%     set(hCurFrame, 'Value',1);
    selectFrame(1);    
%     refresh(1);
  end

  %resets the selection of the current spline
  function resetSelection()
    %current label and point
    [gCurLabel, gCurPoint] = deal([]);
    showCurLabel('off')
    %current add label
    gLabelAdd.points = [];
  end

  %Refreshes the display of the current frame
  % refIm: refreshes the image as well
  % refLabels: draws labels or not
  function refresh(refIm, refLabels)
    if nargin<1 || isempty(refIm),      refIm = 1; end;
    if nargin<2 || isempty(refLabels),  refLabels = 1; end;
    if ~isempty(gCurIndex)     
      %refresh image
      if refIm , refreshImage();    end;
      
      %refresh labels
      if refLabels 
        %delete previous handles if any
        hideLabels();

        %refresh labels if not hide
        if ~strcmp(gState, 'STATE_HIDE'), refreshLabels(); end;      
      end;
      
      show('on');
          
    else
      show('off');
    end;
  end

  %refreshes the current images
  function refreshImage()
    %get frame
    frame = ccvLabel('getFrame', gLabelData, gCurIndex);

    %load the image
    im = [gPath frame.frame];
    if exist(im, 'file')
      %load teh current image
      gCurIm = imread(im);
      %
      [h, w, rgb] = size(gCurIm); %#ok<NASGU>
      %check if to reposition controls to match size
      if h~=gH || w~=gW
        %get figure position
        fpos = get(hFig, 'Position');
        %re-position layout
        posititionLayout(fpos);
      end
      gH = h; gW = w;
      %clear labels handles
      try delete(cell2mat(gLabelsHandles)), catch end;
      gLabelsHandles = cell(1, ccvLabel('nLabels', gLabelData, gCurIndex));
    else
      msgbox(['Error opening image: ' im]); 
      return;
    end;        

    %show the image
    imshow(gCurIm);

    %update the frame caption
    set(hCurFrameTxt2, 'String', sprintf('/%d: %s', ...
      ccvLabel('nFrames',gLabelData), frame.frame));
    
  end

  %refreshes the labels in the current frame
  function refreshLabels()
    %get frame
    frame = ccvLabel('getFrame', gLabelData, gCurIndex);

    %refresh labels
    for lbl=1:length(frame.labels)
      h = [];
      %if selected
      if lbl==gCurLabel
        h = [h drawLabel(frame.labels(lbl), 1)];
        h = [h drawPoint(frame.labels(lbl).points(gCurPoint,:), ...
          gSelPointClr)];
      %not selected
      else h = [h drawLabel(frame.labels(lbl), 0)];
      end;
%       %delete previous handles if any
%       try delete(gLabelsHandles{lbl}); catch, end;
      %set new label handle
      gLabelsHandles{lbl} = h;
    end;    

    %show cur label
    showCurLabel('on');    
  end

  %clears the labels on the screen by deleting their handles
  function hideLabels()
    %delete handles if exist
    for lbl=1:length(gLabelsHandles)
      try delete(gLabelsHandles{lbl}); catch, end;
    end;
  end

  %select a label given the clicked point
  % p   - [x,y] the input point
  function selectLabel(p)
    %get closest label
    [ngCurLabel, cPoint, ngCurPoint, dist] = getClosestPoint(p);
    
    %check the distance
    if dist<=15
      %refresh the old label and paint it not selected
      refreshCurLabel(0);
      %set the cur label
      gCurLabel = ngCurLabel;
      gCurPoint = ngCurPoint;
    else
      %nothing selected
      gCurLabel = []; 
    end;
  end

  %refresh current label
  % sel   - [1] draw it as selected (1) or not (0)
  function refreshCurLabel(sel)
    if nargin<1, sel = 1; end;
    %make sure not empty
    if ~isempty(gCurLabel)
      %get frame
      frame = ccvLabel('getFrame', gLabelData, gCurIndex);
      %delete old objects
      try delete(gLabelsHandles{gCurLabel}), catch, end; %#ok<*CTCH>
      %redraw
      h = [];
      h = [h drawLabel(frame.labels(gCurLabel), sel)];
      if sel
        h = [h drawPoint(frame.labels(gCurLabel).points(gCurPoint,:), ...
            gSelPointClr)];
      end;
      %put back
      gLabelsHandles{gCurLabel} = h;
    end;
  end

  %gets indices of type and subtype for the passed label
  function [typeInd, subtypeInd] = getTypeInds(label)
    [typeInd, subtypeInd] = deal([]);
    %get type index
    t = strcmp(label.type, gLabelTypes);
    typeInd = find(t, 1); 
    if isempty(typeInd), return; end;
    %get the subtype index
    t = strcmp(label.subtype, gLabelSubtypes{typeInd});
    subtypeInd = find(t, 1);
    if isempty(subtypeInd), return; end;
  end

  %draw a label: returns handles to graphic objects and objects texts
  function h = drawLabel(label, selected)
    %get the label type and subtype index
    [typeInd, subtypeInd] = getTypeInds(label);
    if isempty([typeInd subtypeInd]), return; end;
    %get the color of the label
    clr = gLabelSubtypesClr{typeInd}{subtypeInd};
    %selected color
    if selected, pclr = gSelLabelClr; else pclr = clr; end;
    
    %now draw
    h = [];
    switch label.type
      case 'spline'        
        h = ccvDrawBezSpline(label.points, [], clr, [], pclr);
      case 'line'
        hold on;
        h = plot(label.points(:,1), label.points(:,2), ['-' clr], 'LineWidth', 2);
        h = [h plot(label.points(:,1), label.points(:,2), ['*' pclr])];
        hold off;
      case 'rect'
        h = drawRect(label.points, clr, pclr);
      case 'polygon'
        h = drawPolygon(label.points, clr, pclr);
      case 'point'
        h = drawPoint(label.points, clr);
    end;
    %put the object text
    if ~isempty(label.obj)
      h = [h text(label.points(1,1)+5, label.points(1,2), ...
        ['[' num2str(label.obj) ']'], 'Color',gTxtClr, 'FontSize', 12, ...
        'FontWeight','bold')];
    end;
      
  end

  %draw region
  function h = drawPolygon(reg, clr, pclr)
    %draw points
    hold on;
    np = size(reg, 1);
    h = [];
    h = [h plot(reg(:,1), reg(:,2), ['-*' clr], 'LineWidth',2)];
    h = [h plot(reg([np, 1],1), reg([np,1],2), ['-*' clr], 'LineWidth',2)];
    h = [h plot(reg(:,1), reg(:,2), ['*' pclr])];
    hold off;
  end

  %draw rectangle
  function h = drawRect(rect, clr, pclr)
    %get the coordinates of the rectangle, where two opposite corners are
    %stored
    left = min(rect(:,1));    right = max(rect(:,1));
    top = min(rect(:,2));     bottom = max(rect(:,2));
    %draw rect
    rectangle('Position', [left top right-left bottom-top], ...
      'EdgeColor',clr, 'LineWidth',2);
    %draw points
    hold on;
    h = plot(rect(:,1), rect(:,2), ['*' pclr]);
    hold off;
  end

  %draws a point with the given color
  function h = drawPoint(point, clr)
    if nargin<2 || isempty(clr), clr = gSelPointClr; end;
    hold on;
    h = plot(point(1), point(2), ['*' clr]);
    hold off;
  end

  %shows or hides the axis and associated stuff
  function show(state)
    set(hAxis, 'Visible',state);
    set(hCurPoint, 'Visible',state);
    set(hCurFrame, 'Visible',state);
    set(hCurFrameTxt1, 'Visible',state);
    set(hCurFrameTxt2, 'Visible',state);
%     set(hCurLabel, 'Visible',state);
    set(hCurState, 'Visible',state);
%     set(hLabelTypes, 'Visible',state);
%     set(hLabelTypesTxt, 'Visible',state);
  end

end