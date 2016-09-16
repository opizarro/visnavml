% trying to make sense of the bathymetrics tif

figure(1)
[A,R]=geotiffread('sentry189_area2_p5xp5_arc_adjusted_nocross1.tif');
cd ~/Downloads
[A,R]=geotiffread('sentry189_area2_p5xp5_arc_adjusted_nocross1.tif');
B=A;
B(A == -99999)=NaN;
h=mapshow(B,R,'DisplayType','contour','ShowText','on','LevelStep',1);
veh = importdata('/Users/opizarro/Dropbox/visdives/georef_collapsed_labels_v3.csv');
[vx,vy]=projfwd(Ai,veh(:,2),veh(:,1));
Ai=geotiffinfo('sentry189_area2_p5xp5_arc_adjusted_nocross1.tif');
[vx,vy]=projfwd(Ai,veh(:,2),veh(:,1));
vx2=vx+20;
vy2=vy-5;
colormap
colorbar
cmap = colormap;
cmap2 = cmap(round(linspace(1,58,7)),:)
cmap2(1,:)=[0.5 0.5 0.5]
colorbar
caxis([1 7])
cmap2(1,:)=[0.5 0.5 0.5]
scatter(vx2,vy2,1,veh(:,4),'o','filled')
hold on
colorbar
colormap(cmap2)
h=mapshow(B,R,'DisplayType','contour','ShowText','on','LevelStep',1);
caxis([1 7])
axis equal
vx2=vx+25;
scatter(vx2,vy2,1,veh(:,4),'o','filled')
vx2=vx+35;
scatter(vx2,vy2,1,veh(:,4),'o','filled')
hold off
scatter(vx2,vy2,1,veh(:,4),'o','filled')
h=mapshow(B,R,'DisplayType','contour','ShowText','on','LevelStep',1);
hold on
scatter(vx2,vy2,1,veh(:,4),'o','filled')
caxis([1 7])
scatter(vx2,vy2,20,veh(:,4),'o','filled')
vy2=vy-5;
vx2=vx+40;
scatter(vx2,vy2,20,veh(:,4),'o','filled')