function ouput_massspec_csv_func(rnv,x,massmat,outfile,varargin)
% run after optimization
% x = approx 10*sqrt(mass/17)
%outfile = 'sentry189_v3';

if nargin > 4
    timewindow = 1;
    tstart = varargin{1}
    tend = varargin{2}
else
    timewindow = 0;
end

sel_peaks = unique(massmat(:,1));
npeaks = length(sel_peaks);

clip_depth = -1100;
layback = x;
laybackv = zeros(size(massmat(:,3)));
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

for p=1:npeaks
    selp = (massmat(:,1) == sel_peaks(p));
    seld = (depthvec < clip_depth);
    selp = selp&seld;
    if timewindow
        selt = ( massmat(:,3) <= tend ) & ( massmat(:,3) >= tstart);
        selp = selp&selt;
    end
    latp = massmat(selp,4);
    lonp = massmat(selp,5);
    depthp = massmat(selp,6);
    altp = massmat(selp,7);
    valp = massmat(selp,2);
    datamat = [lonp latp depthp altp valp];
        
    fname = sprintf('%s_peak%02d_lb%ds_n17.csv',outfile,sel_peaks(p),round(layback(p)));
    dlmwrite(fname,datamat,'precision','%.6f');

end

% nav once a second
navmat = [rnv.lon(1:5:end),rnv.lat(1:5:end),rnv.pos(1:5:end,3),rnv.alt(1:5:end)];
fname = sprintf('%s_nav.csv',rnv.fname_base);
dlmwrite(fname,navmat,'precision','%.6f');
