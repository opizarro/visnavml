
function Vcor = mass_spec_cor(tref, massmat, sel_peaks, rnv_t, rnv_pos)

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
    
   %if sel_peaks(p) == 15
    P = [px py pz];
    [idx,dx] = knnsearch(P,P,'k',5);
    % zero points that are too far;
   
    pvar = zeros(size(px));
    
    j = 1;
    sel = (dx >= 0) & (dx < 20);
    %size(sel)
    %size(px)
    for i = 1:length(px)
        
        useful_idx = idx(sel(i,:));
        
        if length(useful_idx) >= 5
            pvar(j) = var(pv(useful_idx));
            j=j+1;
        end
    end
    pvar = pvar(1:j-1);
    %[length(px) length(pvar)]
    costterm = costterm + length(px)*mean(pvar);
        
    %end          
   % [max(max(isnan(Vq))) max(max(isnan([px py pz pv])))]
   
end
Vq(isnan(Vq))=0;



%figure(5);
%plot(Vq,'.')
Vcor1 = sum(prod(Vq,2));
Vcor = costterm/Vcor1;
%[Vcor1 costterm]



