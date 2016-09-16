function [X3,Y3,A3,V3,Z3]=plot_massspec(massmat,sec, mbasefig,outfile,lb,navmat)


% massmat(:,4) = latvec;
% massmat(:,5) = lonvec;
% massmat(:,6) = depthvec;
% massmat(:,7) = altvec;
% massmat(:,8) = xvec;
% massmat(:,9) = yvec;


% from visual inspection
 
%block1 = [5000+massmat(1,3), 40000+massmat(1,3)];
%block1a = [29500+massmat(1,3), 36100+massmat(1,3)];
%block1b = [36200+massmat(1,3), 40000+massmat(1,3)];
%block2 = [41000+massmat(1,3), 66000+massmat(1,3)];
%block3 = [67000+massmat(1,3), 94000+massmat(1,3)];
%tsel = block1;

%section(7).dive='sentry190';
%section(7).label='blk1';
%section(7).alt =5;
%section(7).speed = 'slw';
%section(7).tstart = 29500;
%section(7).tend = 36100;

tsel(1) = sec.tstart + massmat(1,3);
tsel(2) = sec.tend + massmat(1,3);


massmat = massmat( (massmat(:,3)<=tsel(2)) & (massmat(:,3)>= tsel(1)),:);
% temporal hi res version

navmat = navmat ((navmat(:,end)<=tsel(2)) & (navmat(:,end)>= tsel(1)),:);

% filter on altitude
%asel = massmat(:,7) < 50;
%massmat = massmat(asel,:);

peaks = unique(massmat(:,1));
% don't use water
lb = lb(peaks~=17);
peaks = peaks(peaks~=17);


npeaks = length(peaks);

contextfig = 40;


plot_context_mass(massmat(:,8),massmat(:,9),massmat(:,6),massmat(:,7),massmat(:,3),contextfig)

altvec = sec.alt;
half_int = 4;
for j = 1: length(altvec)
    target_alt = altvec(j)
    for k = 1:npeaks
 
    mass = peaks(k);
    psel = (massmat(:,1) == mass);
    pmassmat = massmat(psel,:);
    sela = (pmassmat(:,7) > target_alt-half_int ) & (pmassmat(:,7) < target_alt+half_int );
    figure(22); plot(sela)
    px = pmassmat(sela,8);
    
    py = pmassmat(sela,9);
    plat = pmassmat(sela,4);
    plon = pmassmat(sela,5);
    pz = pmassmat(sela,6);
    alt = pmassmat(sela,7);
    pv = pmassmat(sela,2);
    t = pmassmat(sela,3);
    
    basefig = mbasefig+10*k+j;
   
    %plot_single_mass(mass,target_alt,plon,plat,pz,pv,alt,t,basefig)
    [X3,Y3,A3,V3,Z3]=plot_single_mass(mass,target_alt,px,py,pz,pv,alt,t,basefig);
    
    
    
    % for each peak in the section, output a csv
    datamat = [plon plat pz alt pv];
    
    fname = sprintf('mssim_%s_%s_%dm_%s_peak%02d_lb%ds_n17.csv',sec.dive,sec.label,sec.alt,sec.speed,mass,lb(k));
    dlmwrite(fname,datamat,'precision','%.6f');

    % for each peak in the section, generate a high resolution temporal
    % interpolation
    fname = sprintf('htr_%s_%s_%dm_%s_peak%02d_lb%ds_n17.csv',sec.dive,sec.label,sec.alt,sec.speed,mass,lb(k));
    dlmwrite(fname,navmat(:,[1:4 4+k end]),'precision','%.6f');
    % 
    figure(200);plot3(px,py,pz)





    
    
    end
    
end



    



function [X3,Y3,A3,V3,Z3]=plot_single_mass(mass,target_alt,px,py,pz,pv,alt,t,basefig)
% run after optimization
% x = approx 10*sqrt(mass/17)
%outfile = 'sentry189_v3';
    
title_str = sprintf('peak %d at %.1f [m] altitude',mass,target_alt);

maxx = max(px);
minx = min(px);
maxy = max(py);
miny = min(py);
maxa = max(alt);
mina = min(alt);

% [X,Y] = meshgrid([minx:2:maxx],[miny:2:maxy]);
% 
% 
% V = griddata(px,py,pv,X,Y,'natural');
% % figure(basefig+2);
% % surf(X,Y,V);axis equal; shading flat; 
% % title(title_str);
% % colorbar
% 
% figure(basefig+3)
% [C,H]=contour(X,Y,V);axis equal
% title(title_str);
% colorbar
% clabel(C,H);
% 


%[X3,Y3,A3] = meshgrid([minx:0.00001*cos(DTR*miny):maxx],[miny:0.00001:maxy],target_alt);
[X3,Y3,A3] = meshgrid([minx:5:maxx],[miny:5:maxy],target_alt);


V3 = griddata(px,py,alt, pv,X3,Y3,A3,'natural');
Z3 = griddata(px,py,pz,X3,Y3,'natural');


% figure(basefig+4);
% surf(X3,Y3,V3);axis equal; shading flat; 
% title(title_str);
% colorbar

figure(basefig+5)
[C,H]=contour(X3,Y3,V3);axis equal

title(title_str);
colorbar
%hold on; plot(px,py,'b.'); hold off
%clabel(C,H);

