% script form
% inputs:
% a nav path
% a bathymetric grid

% create cost function that allows 'wiggle' in nav positions subject to the
% constraint of the distance between positions being held constant
% maximises correlation between them


% load bathy

[A,R]=geotiffread('~/Dropbox/visdives/sentry189_area2_p5xp5_arc_adjusted_nocross1.tif');
B=A;
B(A == -99999)=NaN;
h=mapshow(B,R,'DisplayType','contour','ShowText','on','LevelStep',1);
Xmeshrange=linspace(R.XWorldLimits(1)-R.CellExtentInWorldX/2,R.XWorldLimits(2)-R.CellExtentInWorldX/2,R.RasterSize(2));
Ymeshrange=linspace(R.YWorldLimits(2)-R.CellExtentInWorldY/2,R.YWorldLimits(1)-R.CellExtentInWorldY/2,R.RasterSize(1));

[bX,bY] = meshgrid(Xmeshrange,Ymeshrange);


% load nav
nav = importdata('~/Dropbox/visdives/georef_labels_test.csv');
x = nav(:,4);
y = nav(:,5);
z = nav(:,6); % assuming that his is actual bottom depth, not vehicle depth

% calc horizontal distance between poses
% large error weighting associated to these
dx = diff(x);
dy = diff(y); 

dvec = (dx.^2 + dy.^2).^0.5 ;

% calc direction between original poses
hvec = atan2(dy,dx);

% associate weighting to changes in these directions




