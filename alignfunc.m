%% 
function e = alginfunc(dvec, hvec, p, z, bathy)
% p = [xoffset; yoffset; dh_global];
% synthesize new nav from original nav and p
xoffset = p(1);
yoffset = p(2);
dh_global = p(3);

% rotate vectors with dh_global
hvec = hvec + dh_global;

% create nav positions
dx = dvec.*cos(hvec);
dy = dvec.*sin(hvec);

veh_x = cumsum([xoffset; dx]);
veh_y = cumsum([yoffset; dy]);

% calculate errors against dvec and hvec and bathy

Zq = interp2(bX,bY,bathy,veh_x,veh_y,'nearest');

e = z-Zq;
