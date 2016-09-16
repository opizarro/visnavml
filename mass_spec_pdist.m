
function Vcor = mass_spec_pdist(tref, massmat, sel_peaks, rnv_t, rnv_pos)

%global massmat sel_peaks rnv_t rnv_pos;

npeaks = length(sel_peaks);


%layback = tref*sqrt(massmat(:,1)/17);
layback = zeros(size(massmat(:,1)));
for p=1:npeaks
    layback(massmat(:,1) == sel_peaks(p))=tref(p);
end
masstime = massmat(:,3)-layback;


depthvec = interp1(rnv_t,rnv_pos(:,3),masstime,'linear');

xvec = interp1(rnv_t,rnv_pos(:,1),masstime,'linear');
yvec = interp1(rnv_t,rnv_pos(:,2),masstime,'linear');
Vq = zeros(length(layback),npeaks);

maxd = 20;
costterm = 0;
for p=1:npeaks
    
    selp = (massmat(:,1) == sel_peaks(p));
    seld = (depthvec < -1150);
    selp = selp&seld;
    px = xvec(selp);
    py = yvec(selp);
    pz = depthvec(selp);
    pv = massmat(selp,2);
    %figure(3);plot3(py,px,pz,'.')
    F = TriScatteredInterp([py px pz],pv,'linear');
    Vq(:,p) = F([yvec,xvec,depthvec]);

   %distance to peaks
   %figure(100);hist(pv,100)
    selt = ( pv > (mean(pv)+2*std(pv)) );
    P = [px(selt) py(selt) pz(selt)];
    %size(P)
    [idx,dx] = knnsearch(P,P,'k',5);
    % zero points that are too far;

    % pvar = zeros(size(px));
 
    
    dx(dx > maxd) = maxd;
    %size(sel)
    %size(px)


    pvar = sum(sum(dx.*dx,2));
   % pvar
   % size(dx)

    %[length(px) length(pvar)]
    costterm = costterm + pvar;

    %end          
   % [max(max(isnan(Vq))) max(max(isnan([px py pz pv])))]

   
end
Vq(isnan(Vq))=0;



%figure(5);
%plot(Vq,'.')
Vcor1 = sum(prod(Vq,2));
Vcor = costterm/Vcor1/1000;
%[Vcor1 costterm];



