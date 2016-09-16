% renavs mass spec
% load massproc/sentry197_20130811_1920_rnv.mat
% load massproc/sentry197_mssim.mat
% outfile = 'sentry197_v1'

%load massproc/sentry196_20130811_1350_rnv.mat
%load massproc/sentry196_mssim.mat
%outfile = 'sentry196_v1'

%load massproc/sentry195_20130810_0641_rnv.mat
%load massproc/sentry195_mssim.mat
%outfile = 'sentry195_v1'

% mssim file not reading
%load massproc/sentry194_20130808_0612_rnv.mat
%load massproc/sentry194_mssim.mat
%outfile = 'sentry194_v1'

%load massproc/sentry193_combined_rnv.mat
%load massproc/sentry193_mssim.mat
%outfile = 'sentry193_v1'

%load massproc/sentry192_20130811_1509_rnv.mat
%load massproc/sentry192_mssim.mat
%outfile = 'sentry192_v1'

%load massproc/sentry191_20130803_1655_rnv.mat
%load massproc/sentry191_mssim.mat
%outfile = 'sentry191_v1'

%load massproc/sentry190_20130801_2136_rnv.mat
%load massproc/sentry190_mssim.mat
%outfile = 'sentry190_v1'

%load massproc/sentry189_20130731_1534_rnv.mat
%load massproc/sentry189_mssim.mat
%outfile = 'sentry189_v1'



%load massproc_herc/H1279_1284.mat
%load massproc_herc/H1279mass.mat
%outfile = 'H1279'

%load massproc_herc/H1279_1284.mat
%load massproc_herc/H1280mass.mat
%outfile = 'H1280'

%load massproc_herc/H1279_1284.mat
%load massproc_herc/H1281mass.mat
%outfile = 'H1281'
% 
%load massproc_herc/H1279_1284.mat
%load massproc_herc/H1283mass.mat
%outfile = 'H1283'
% 
% load massproc_herc/H1279_1284.mat
% load massproc_herc/H1284mass.mat
% outfile = 'H1284'


%load massproc_herc/H1279_1288.mat
%load massproc_herc/H1285mass.mat
%outfile = 'H1285'


 %load massproc_herc/H1279_1288.mat
 %load massproc_herc/H1286mass.mat
 %outfile = 'H1286' 
 
 %load massproc_herc/H1279_1288.mat
 %load massproc_herc/H1287mass.mat
 %outfile = 'H1287'
 
 load massproc_herc/H1279_1288.mat
 load massproc_herc/H1288mass.mat
 outfile = 'H1288'
 
 
 

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
tref = 10;



if size(mssim.peak,2) > length(sel_peaks)
% reading from sentry matix with all peaks
    peaks = mssim.peak(:,sel_peaks);
    val17 = mssim.peak(:,17);
else
    peaks = mssim.peak;
    val17 = mssim.peak(:,2);
end

for i=1:length(mssim.start_year)
    year = mssim.start_year(i);
    month = mssim.start_month(i);
    day = mssim.start_day(i);
    hours = mssim.start_hour(i);
    minutes = mssim.start_minute(i);
    seconds = mssim.start_second(i);
    unixtime_start = ymdhms_to_sec(year,month,day,hours,minutes,seconds);
    
    year = mssim.end_year(i);
    month = mssim.end_month(i);
    day = mssim.end_day(i);
    hours = mssim.end_hour(i);
    minutes = mssim.end_minute(i);
    seconds = mssim.end_second(i);
    unixtime_end = ymdhms_to_sec(year,month,day,hours,minutes,seconds);
   
    
    for p=1:npeaks
        indx = (i-1)*npeaks+p;
        mass = sel_peaks(p);
        val = peaks(i,p);
        massmat(indx,1) = mass;
        massmat(indx,2) = val/val17(i);
        dt = unixtime_end - unixtime_start;
        % internal start time
        tp = unixtime_start + dt*(p-1)/(npeaks-1);
       
        massmat(indx,3) = tp;
        
    
    end
    
    ctind = 2*i-1;
    ctmat(ctind,1) = unixtime_start;
    ctmat(ctind,6) = mssim.start_temperature(i);
    ctmat(ctind,7) = mssim.start_conductivity(i);
    ctmat(ctind,8) = mssim.start_pressure(i);
    ctmat(ctind,9) = mssim.start_salinity(i);
    ctmat(ctind,10) = mssim.start_soundspeed(i);
    
    ctmat(ctind+1,1) = unixtime_end;
    ctmat(ctind+1,6) = mssim.end_temperature(i);
    ctmat(ctind+1,7) = mssim.end_conductivity(i);
    ctmat(ctind+1,8) = mssim.end_pressure(i);
    ctmat(ctind+1,9) = mssim.end_salinity(i);
    ctmat(ctind+1,10) = mssim.end_soundspeed(i);
    
    
end

% clean up NaN

selnan = isnan(massmat(:,2));
massmat(selnan,2) = 0;


% interpolate nav solution to mass spec time
masstime = massmat(:,3);
latvec = interp1(rnv.t,rnv.lat,masstime,'linear');
lonvec = interp1(rnv.t,rnv.lon,masstime,'linear');

depthvec = interp1(rnv.t,rnv.pos(:,3),masstime,'linear');

altvec = interp1(rnv.t,rnv.alt,masstime,'linear');
xvec = interp1(rnv.t,rnv.pos(:,1),masstime,'linear');
yvec = interp1(rnv.t,rnv.pos(:,2),masstime,'linear');

% stuff in matrix
massmat(:,4) = latvec;
massmat(:,5) = lonvec;
massmat(:,6) = depthvec;
massmat(:,7) = altvec;
massmat(:,8) = xvec;
massmat(:,9) = yvec;


% interpolate nav solution to ct times
cttime = ctmat(:,1);
latvec = interp1(rnv.t,rnv.lat,cttime,'linear');
lonvec = interp1(rnv.t,rnv.lon,cttime,'linear');

depthvec = interp1(rnv.t,rnv.pos(:,3),cttime,'linear');

altvec = interp1(rnv.t,rnv.alt,cttime,'linear');
xvec = interp1(rnv.t,rnv.pos(:,1),cttime,'linear');
yvec = interp1(rnv.t,rnv.pos(:,2),cttime,'linear');
% stuff in matrix
ctmat(:,2) = lonvec;
ctmat(:,3) = latvec;

ctmat(:,4) = depthvec;
ctmat(:,5) = altvec;
%ctmat(:,11) = xvec;
%ctmat(:,12) = yvec;


if display_output

    relmasstime = masstime-masstime(1);
    figure(10);
    subplot(4,1,1)
    plot(relmasstime,depthvec)
    subplot(4,1,2)
    plot(relmasstime,xvec)
    subplot(4,1,3)
    plot(relmasstime,yvec)
    
    figure(11);
    plot(xvec,yvec,'.')
    
    
    maxx = max(xvec);
    minx = min(xvec);
    maxy = max(yvec);
    miny = min(yvec);

    [X,Y] = meshgrid([minx:2:maxx],[miny:2:maxy]);
    figure(1);
    for p=1:npeaks
        selp = (massmat(:,1) == sel_peaks(p));
        seld = (massmat(:,6) < -1100);
        selp = selp&seld;
        px = xvec(selp);
        py = yvec(selp);
        pv = massmat(selp,2);
        subplot(2,3,p);
        V = griddata(px,py,pv,X,Y);
        imagesc(flipud(V));axis equal;

        title_str = sprintf('peak %d',sel_peaks(p));
        title(title_str);
        colorbar
    end
end


%%% ranges for output blocks
% from visual inspection
% Sentry190
% block1 = [5000+massmat(1,3), 40000+massmat(1,3)];
% block2 = [41000+massmat(1,3), 66000+massmat(1,3)];
% block3 = [67000+massmat(1,3), 94000+massmat(1,3)];

% % global search
% tvec = [1:1:150];
% for k = 1:length(tvec);
%     Vcor(k) = mass_spec_cor(massmat,sel_peaks,rnv.t,rnv.pos,tvec(k));
%     figure(1);plot(tvec(1:k),Vcor(1:k));
% end
   
%  Typical workflow to run the GlobalSearch solver:
%     ==============================================
%     1. Set up the PROBLEM structure
%         PROBLEM = createOptimProblem('fmincon','objective',...)
%tref=30;
%lb0 = tref*sqrt(sel_peaks/17);



% 
x = lb0;

if optimize
    rnv_t = rnv.t;
    rnv_pos = rnv.pos;
    
    %linear constraints so that diffusion time is greater for greater mass
    
    A = [1 -1  0  0 ;
         0  1 -1  0 ;
         0  0  1 -1 ];
        
    B = [5 0 0 ]';
    
    
    options = optimset('Display','iter');
    
    
    %f = @(x)mass_spec_cor(x,massmat, sel_peaks, rnv_t, rnv_pos);
    f = @(x)mass_spec_pdist(x,massmat, sel_peaks(evalsel), rnv_t, rnv_pos);
  
    
    %problem = createOptimProblem('fminunc','objective',@mass_spec_cor,'x0',lb0);
    problem = createOptimProblem('fmincon','objective',f,'x0',lb0(evalsel),...
        'Aineq',A,'bineq',B,'lb',[0 0 0 0],'ub',[50 100 100 150],'options',options);
    
    %     2. Construct the GlobalSearch solver
    %         GS = GlobalSearch
    
    
     gs = GlobalSearch;

     % 
     if singlemachine
         [x,f]=run(gs,problem);
     else
    % use MultiStart (doesn't work on my mac) 
        matlabpool open 12
        ms = MultiStart(gs);
        ms.UseParallel = 'always';
        [x,f]=run(ms,problem,144);
        matlabpool close
     end
    %     3. Run the solver
    %         run(GS,PROBLEM)
    %
    %

end




%     Example:
%        Run global search on the optimization problem 
%           minimize peaks(x, y); subject to 
%                     (x+3)^2 + (y+3)^2 <= 36,
%                     -3 <= x <= 3 and  
%                     -3 <= y <= 3.
%  
%        Specify the first constraint in a MATLAB file function such as
%           function [c,ceq] = mycon(x)
%           c = (x(1)+3)^2 + (x(2)+3)^2 - 36;
%           ceq = [];
%  
%        Implement the typical workflow
%           problem = createOptimProblem('fmincon','objective', ...
%           @(x) peaks(x(1), x(2)), 'x0', [1 2], 'lb', [-3 -3], ...
%           'ub', [3 3], 'nonlcon', @mycon)
%           gs = GlobalSearch
%           [x, f] = run(gs, problem)
% 
% 


    
