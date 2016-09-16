function [Vs,LONs,LATs,Vn,R]=mass_spec_georef(X3,Y3,V3,Z3,rnv)

% generate geotiff
geotiff = 0

[LAT,LON] = xy2ll(X3,Y3,rnv.orglat,rnv.orglon);
    % resample to a grid
minLat = min(LAT(:));
maxLat = max(LAT(:));

minLon = min(LON(:));
maxLon = max(LON(:));

% 
nlat = size(LAT,1); 
nlon = size(LON,2); 
vecLon = linspace(minLon,maxLon,nlon);
vecLat = linspace(minLat,maxLat,nlat);
[LONs,LATs] = meshgrid(vecLon, vecLat);

% resampled and lined up with lat / lon lines
[Vs] = griddata(LON,LAT,V3,LONs,LATs,'natural');

[Zs] = griddata(LON,LAT,Z3,LONs,LATs,'natural');

% Construct a spatialref.GeoRasterReference object.
if geotiff
    R = georasterref('RasterSize',size(Vs), ...
           'RasterInterpretation', 'cells', ...
           'Latlim', [minLat maxLat], 'Lonlim', [minLon maxLon], ...
           'ColumnsStartFrom', 'south','RowsStartFrom','west');



       %normalize Vs
       Vsmin = min(Vs(:));
       Vsmax = max(Vs(:));
     Vn = uint8( 255*(Vs - Vsmin)/(Vsmax-Vsmin));


    fname = 'sentry190_block1b_5m_peak78_lb91s';
    fname_geotiff = sprintf('%s%s',fname,'.tif');
    geotiffwrite(fname_geotiff, Vn ,R);
end

% A = imread('testfigtogeo.png');
% R2 = georasterref('RasterSize',size(A), ...
%        'RasterInterpretation', 'cells', ...
%        'Latlim', [minLat maxLat], 'Lonlim', [minLon maxLon], ...
%        'ColumnsStartFrom', 'north','RowsStartFrom','west');
% 
% geotiffwrite('testfigtogeotif.tif',A,R2);

% fname_csv = sprintf('%s%s',fname,'_grid.csv');
% seldat = (~isnan(Zs(:))) & (~isnan(Vs(:)));
% datamat = [LONs(seldat) LATs(seldat) Zs(seldat) Vs(seldat)];
% dlmwrite(fname_csv,datamat,'precision','%.7f');

fname_gmt = sprintf('%s%s',fname,'_depth.grd');
grdwrite2(vecLon,vecLat,Zs,fname_gmt);

fname_gmt = sprintf('%s%s',fname,'_val.grd');
grdwrite2(vecLon,vecLat,Vs,fname_gmt);

figure(201);
plot3(LONs(:),LATs(:),Zs(:),'.')
% figure(202);
% geoshow(Vn,R)
%this doesn't work d=makedbfspec(R)

