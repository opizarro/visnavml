% filter / clip data

%massmat(:,4) = latvec;
%massmat(:,5) = lonvec;
%massmat(:,6) = depthvec;
%massmat(:,7) = altvec;
%massmat(:,8) = xvec;
%massmat(:,9) = yvec;

basefig=1;

% all data


plot_massspec(massmat,basefig)


% subset

% time window
tstart = 1;
tend = length(massmat(:,1));
selt = (massmat(:,3) >= tstart) & (massmat(:,3) <= tend); 

% depth limit
mindepth = -1150;
seld = massmat(:,6) < mindepth

% altitude limits
minalt = 0;
maxalt = 100;
sela = (massmat(:,7) >= minalt) & (massmat(:,7) <= maxalt); 

submassmat = massmat(selt&seld&sela,:);

sbasefig=1000;
plot_masspec(submassmat,sbasefig)





