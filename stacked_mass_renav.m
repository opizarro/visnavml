% renavs mass spec


stacked_mass = dlmread('/Users/opizarro/data/visdives/Sentry197/contents/stacked_mass.csv')
 

optimize = 0;
singlemachine = 1;

% visualization
display_output = 0


lb0 = [10 16 57 64 91]
%32.0740   38.4549   43.4552   50.1167   91.3028;
%
%9.5007   15.9660   57.3173   63.8177   70.3177
%32.7192   37.8932   42.8979   50.1161   91.2597
%global massmat sel_peaks rnv_t rnv_pos;

% all peaks
% peaks = find(~isnan(mssim.peak(1,:)));
sel_peaks = [15 17 27 43 78];
evalsel = [1 3:length(sel_peaks)];
npeaks = length(sel_peaks);

% desired output format
% HST 2013/07/16 15:34:28.920740 SMS:1101,R1 SMS:1101,R1143861|005  1317165169.6 6 -289 346 -446.0 3.4 2.688e+01 1.232e+04 6.637e+03 0.00

% output file

 dt = 25;
        % internal start time
 massmat = stacked_mass;       
 mass = massmat(:,1);
 
 % extract nav
 [ut,uind] = unique(massmat(:,3));
 rnv.t = ut;
 rnv.lat = massmat(uind,4);
 rnv.lon = massmat(uind,5);
 rnv.depth = massmat(uind,6);
 
 
 for k=1:length(mass)
    
    unixtime_start = massmat(k,3);
    
    p = find(mass(k)==sel_peaks);
 
    tp = unixtime_start + dt*(p-1)/(npeaks-1) - lb0(p);
    % spread out the sampling time within interval   
    massmat(k,3) = tp;
        
end

% clean up NaN

selnan = isnan(massmat(:,2));
massmat(selnan,2) = 0;




% interpolate nav solution to mass spec time
masstime = massmat(:,3);
latvec = interp1(rnv.t,rnv.lat,masstime,'linear','extrap');
lonvec = interp1(rnv.t,rnv.lon,masstime,'linear','extrap');

depthvec = interp1(rnv.t,rnv.depth,masstime,'linear');

%altvec = interp1(rnv.t,rnv.alt,masstime,'linear');
%xvec = interp1(rnv.t,rnv.pos(:,1),masstime,'linear');
%yvec = interp1(rnv.t,rnv.pos(:,2),masstime,'linear');

% stuff in matrix
massmat(:,4) = latvec;
massmat(:,5) = lonvec;
massmat(:,6) = depthvec;
% massmat(:,7) = altvec;
% massmat(:,8) = xvec;
% massmat(:,9) = yvec;




%% now interpolate missing mass spec values 
valq = zeros(length(masstime),npeaks);
for p = 1:npeaks
    mass = sel_peaks(p)
    selrows = (massmat(:,1) == mass);
    val = massmat(selrows,2);
    mtime = massmat(selrows,3);
    valq(:,p) = interp1(mtime,val,massmat(:,3),'linear','extrap');
    
end

massmat_interp = [massmat(:,3) massmat(:,4:6) valq];
    
% select depth
seld = (massmat_interp(:,4) < -1000);
massmat_interp = massmat_interp(seld,:);

% sort based on time
[tsort,indsort] = sort(massmat_interp(:,1));
massmat_interp = massmat_interp(indsort,:);
massmat_interp(:,1) = massmat_interp(:,1)-massmat_interp(1,1);

selt = massmat_interp(:,1) > 2600;
massmat_interp = massmat_interp(selt,:);

fname='interp_stacked_mass.csv';
fd = fopen(fname,'w');
fprintf(fd,'unixtime,lat,lon,depth,mz15,mz17,mz27,mz43,mz78\n');

dlmwrite(fname,massmat_interp,'precision','%.7f','-append');


