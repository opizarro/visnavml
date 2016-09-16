% run after optimization
% x = approx 10*sqrt(mass/17)
%outfile = 'sentry189_v3';



clip_depth = -900;
layback = x;
laybackv = zeros(size(massmat(:,3)));
% remove peak17
%layback = layback(sel_peaks~=17);
%sel_peaks = sel_peaks(sel_peaks~=17);
%npeaks = length(sel_peaks)

for p=1:npeaks
    laybackv(massmat(:,1) == sel_peaks(p))=layback(p);
end
masstime = massmat(:,3)-laybackv;

% interp nav
latvec = interp1(rnv.t,rnv.lat,masstime,'linear');
lonvec = interp1(rnv.t,rnv.lon,masstime,'linear');
depthvec = interp1(rnv.t,rnv.pos(:,3),masstime,'linear');
altvec = interp1(rnv.t,rnv.alt,masstime,'linear');

% stuff in matrix
massmat(:,4) = latvec;
massmat(:,5) = lonvec;
massmat(:,6) = depthvec;
massmat(:,7) = altvec;

if 1
htrvalp = zeros(length(rnv.t(1:5:end)),npeaks);
for p=1:npeaks
    selp = (massmat(:,1) == sel_peaks(p));
    seld = (depthvec < clip_depth);
    selp = selp&seld;
    latp = massmat(selp,4);
    lonp = massmat(selp,5);
    depthp = massmat(selp,6);
    altp = massmat(selp,7);
    valp = massmat(selp,2);
    datamat = [masstime(selp) lonp latp depthp altp valp];
    
    fname = sprintf('%s_peak%02d_lb%ds.csv',outfile,sel_peaks(p),round(layback(p)));
    dlmwrite(fname,datamat,'precision','%.7f');
    
    
    
    % high resolution version of mass spec data
    htrvalp(:,p) = interp1(masstime(selp),valp,rnv.t(1:5:end),'linear');
    %fname = sprintf('%s_nav.csv',rnv.fname_base);
    %dlmwrite(fname,navmat,'precision','%.6f');

end

% nav once a second
navmat = [rnv.t(1:5:end),rnv.lon(1:5:end),rnv.lat(1:5:end),rnv.pos(1:5:end,3),rnv.alt(1:5:end),htrvalp];
fname = sprintf('%s_nav.csv',outfile);
dlmwrite(fname,navmat,'precision','%.7f');
end

F = dlmread('uvfluor_comp.csv');
% print fluorometer file
tstart = min(masstime);
tend = max(masstime);

self = (F(:,1) >= tstart) & (F(:,1) <= tend);
fname =sprintf('%s_flr.csv',outfile);
flrtime = F(self,1);
length(flrtime)

% interp nav
latvec = interp1(rnv.t,rnv.lat,flrtime,'linear');
lonvec = interp1(rnv.t,rnv.lon,flrtime,'linear');
depthvec = interp1(rnv.t,rnv.pos(:,3),flrtime,'linear');
altvec = interp1(rnv.t,rnv.alt,flrtime,'linear');

fmat = [flrtime lonvec latvec depthvec altvec F(self,2)];

dlmwrite(fname,fmat,'precision','%.7f');










