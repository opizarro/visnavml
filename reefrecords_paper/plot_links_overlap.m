close all
clear

fid=fopen('stereo_pose_est.data');
orig = textscan(fid, '%*s %f', 2,'CommentStyle','%');
sWreckA = textscan(fid, '%d%f%f%f%f%f%f%f%f%f%s%s%f%f%d','CommentStyle','%', 'Headerlines', 2);

fidRel=fopen('stereo_relative_poses.data');
sWreckARelativePoses = textscan(fidRel, '%f%f%f%f%f%f%s%s%s%s','CommentStyle','%');

INDX = 1;
TIME = 2;
LAT = 3;
LON = 4;
N = 5;
E = 6;
DEPTH = 7;
ROLL = 8;
PITCH = 9;
YAW = 10;
LEFT_IMG = 11;
RIGHT_IMG = 12;
ALT = 13;
OLAP = 14;
CLOSURE = 15;

REL_X = 1;
REL_Y = 2;
REL_Z = 3;
REL_ROLL = 4;
REL_PITCH = 5;
REL_YAW = 6;
REL_LEFT_A = 7;
REL_RIGHT_A = 8;
REL_LEFT_B = 9;
REL_RIGHT_B = 10;

nImg = length(sWreckA{INDX});

% look for altitude outliers
zeroAltNdx = find (sWreckA{ALT} == 0);

for i = 1:length(zeroAltNdx) 
  sWreckA{ALT}(zeroAltNdx(i)) = (sWreckA{ALT}(zeroAltNdx(i)-1) + sWreckA{ALT}(zeroAltNdx(i)+1))/2;
end

% compute the depth of the seafloor
depth = sWreckA{DEPTH}+sWreckA{ALT};

% compute the speed of the vehicle
for i=2:length(sWreckA{INDX})
    speed(i) = sqrt((sWreckA{N}(i) - sWreckA{N}(i-1))^2 + (sWreckA{E}(i) - sWreckA{E}(i-1))^2) / (sWreckA{TIME}(i) - sWreckA{TIME}(i-1));
end

wreckNdx{1} = [1:length(sWreckA{TIME})];
% wreckNdx{2} = [6566:17119];
% wreckNdx{3} = [17120:23260];
% wreckNdx{4} = [23261:32353];
% wreckNdx{5} = [32354:37582];
% wreckNdx{6} = [37583:length(sWreckA{TIME})];

wreckCol{1} = 'c.';
% wreckCol{2} = 'b.';
% wreckCol{3} = 'm.';
% wreckCol{4} = 'g.';
% wreckCol{5} = 'y.';
% wreckCol{6} = 'k.';

% Find pose links
numLinks = length(sWreckARelativePoses{REL_LEFT_A});
k = 1;
numSkip = 1;
LCstart = zeros(ceil(numLinks/numSkip),6);
LCend = zeros(ceil(numLinks/numSkip),6);
LCcounts = zeros(6);

minE = min(sWreckA{E});
minN = min(sWreckA{N});
LCdensityRes = 1;
LCdensity = zeros(int32(LCdensityRes*(max(sWreckA{E})-minE)+1), int32(LCdensityRes*(max(sWreckA{N})-minN))+1);
LCcount_images = zeros(length(sWreckA{INDX}),1);
for i = 1:numSkip:numLinks
   ndxstart = find(strcmp(sWreckARelativePoses{REL_LEFT_A}(i), sWreckA{LEFT_IMG}));
   ndxend = find(strcmp(sWreckARelativePoses{REL_LEFT_B}(i), sWreckA{LEFT_IMG}));
   LCcount_images(ndxstart)= LCcount_images(ndxstart) + 1;
   LCcount_images(ndxend) = LCcount_images(ndxend) + 1;
   if (~isempty(ndxstart))
       %for j = 1:length(ndxstart)
       for diveNdx = 1:1
           if(ndxstart >= wreckNdx{diveNdx}(1) & ndxstart <= max(wreckNdx{diveNdx}));
                startDiveNdx = diveNdx;
           end
           if(ndxend >= wreckNdx{diveNdx}(1) & ndxend <= max(wreckNdx{diveNdx}));
               endDiveNdx = diveNdx;
           end
       end
       LCcounts(startDiveNdx, endDiveNdx) = LCcounts(startDiveNdx, endDiveNdx) + 1;
      
       
       LCstart(k,:) = [sWreckA{TIME}(ndxstart) sWreckA{E}(ndxstart) sWreckA{N}(ndxstart) sWreckA{DEPTH}(ndxstart) ndxstart startDiveNdx];
       LCend(k,:) = [sWreckA{TIME}(ndxend) sWreckA{E}(ndxend) sWreckA{N}(ndxend) sWreckA{DEPTH}(ndxend) ndxend endDiveNdx];

       % update the LC density counts
       start_E = int32(LCdensityRes*(sWreckA{E}(ndxstart)-minE)+1);
       start_N = int32(LCdensityRes*(sWreckA{N}(ndxstart)-minN)+1);
       end_E = int32(LCdensityRes*(sWreckA{E}(ndxend)-minE)+1);
       end_N = int32(LCdensityRes*(sWreckA{N}(ndxend)-minN)+1);
       LCdensity(start_E, start_N) = LCdensity(start_E, start_N) + 0.5;
       LCdensity(end_E, end_N) = LCdensity(end_E, end_N) + 0.5;
       k = k + 1;
       
       if (mod(k,100) == 0)
           sprintf('%d of %d',k, length(sWreckARelativePoses{REL_LEFT_A}))
       end
   end   
end

ndxIntraLC = find(LCstart(:,6) == LCend(:,6));
ndxInterLC = find(LCstart(:,6) ~= LCend(:,6));
%for diveNdx = 1:6
%    IntraLC{diveNdx} = ndxIntraLC(find(LCstart(ndxIntraLC,5) >= wreckNdx{diveNdx}(1) & LCstart(ndxIntraLC,5) <= max(wreckNdx{diveNdx})));
%end
%%ndxIntraLC_B = ndxIntraLC(find(LCstart(ndxIntraLC,5) > wreckALength));
%ndxInterLCIntraYear = find(LCstart(:,6) == LCend(:,6));
%ndxInterLCInterYear = find(abs(LCstart(:,1) - LCend(:,1)) > 2e6);

figure
hold on
axis equal
axis([min(sWreckA{E}) max(sWreckA{E}) min(sWreckA{N}) max(sWreckA{N})]);
%hIntraLC = line([LCstart(ndxIntraLC,2) LCend(ndxIntraLC,2)]', [LCstart(ndxIntraLC,3) LCend(ndxIntraLC,3)]', 'Color', 'red');    
%hInterLC = line([LCstart(ndxInterLC,2) LCend(ndxInterLC,2)]', [LCstart(ndxInterLC,3) LCend(ndxInterLC,3)]', 'Color', [125/255 100/255 175/255]);    
%hInterLCIntraYear = line([LCstart(ndxInterLCIntraYear,2) LCend(ndxInterLCIntraYear,2)]', [LCstart(ndxInterLCIntraYear,3) LCend(ndxInterLCIntraYear,3)]', 'Color', 'green');    
%hInterLCInterYear = line([LCstart(ndxInterLCInterYear,2) LCend(ndxInterLCInterYear,2)]', [LCstart(ndxInterLCInterYear,3) LCend(ndxInterLCInterYear,3)]', 'Color', 'black');    
%for diveNdx = 1:6
%    hIntraLCD{diveNdx} = line([LCstart(IntraLC{diveNdx},2) LCend(IntraLC{diveNdx},2)]', [LCstart(IntraLC{diveNdx},3) LCend(IntraLC{diveNdx},3)]', 'Color', 'red');
%end

% Dive plots
for diveNdx = 1:1
%    figure(dive)
    hDive(diveNdx) = plot(sWreckA{E}(wreckNdx{diveNdx}), sWreckA{N}(wreckNdx{diveNdx}), wreckCol{diveNdx});

%    orient landscape
%    print -dpdf 'AntikytheraMultiSessionSLAMDiveA.pdf'
%    close
end
%axis tight
grid on
xlabel('East (m)');
ylabel('North (m)');

%legend([hDive hIntraLC(1) hInterLC(1)], 'Dive A (2014)', 'Dive B (2014)', 'Dive C (2015)', 'Dive D (2015', 'Dive E (2015)', 'Dive F (2015)', 'IntraLC', 'InterLC');
%legend(hDive, 'Dive A (2014)', 'Dive B (2014)', 'Dive C (2015)', 'Dive D (2015', 'Dive E (2015)', 'Dive F (2015)');

%print -dpdf 'AntikytheraMultiSessionSLAM2014_2015.pdf'

figure
hDensity=imagesc([minE,max(sWreckA{E})],[minN,max(sWreckA{N})],log10(LCdensity'+1))
set(gca,'YDir','normal')
xlabel('East (m)');
ylabel('North (m)');
axis equal
axis tight
colorbar
y=get(colorbar,'YTick');
h=colorbar('YTickLabel',round(10.^y-1));
cmap = colormap('bone');
%colormap(flipud(cmap));
colormap jet
ylabel(h, 'density of image overlap [counts/m^2]')


print -dpdf 'horseshoe_circle01_201404_16_LCDensity.pdf'
print -dpng 'horseshoe_circle01_201404_16_LCDensity.png'

% histogram of number of links per image
figure(4);hist(LCcount_images,[0:80])

% % Dive B
% figure(2)
% hold on
% 
% hSingleLCDiveB = line([LCstart(ndxIntraLC_B,2) LCend(ndxIntraLC_B,2)]', [LCstart(ndxIntraLC_B,3) LCend(ndxIntraLC_B,3)]', 'Color', 'magenta');
% 
% hDiveB = plot(sWreckA{E}(wreckALength:length(sWreckA{E})) + diveOffset, sWreckA{N}(wreckALength:length(sWreckA{E})), 'b.');
% %ndxSurveyA = find(abs(LCstart(:,1) - LCend(:,1)) < 2e4);
% %ndxSurveyB = find(abs(LCstart(:,1) - LCend(:,1)) > 2e4);
% 
% legend([hDiveB, hSingleLCDiveB(1)], 'Dive B', 'Intra-session LC');
% axis equal
% %axis tight
% grid on
% xlabel('East (m)');
% ylabel('North (m)');
% 
% orient landscape
% print -dpdf 'AntikytheraMultiSessionSLAMDiveB.pdf'
% close 
% 
% % Combined Dive
% figure(3)
% hold on
% 
% hSingleLCDiveA = line([LCstart(ndxIntraLC_A,2) LCend(ndxIntraLC_A,2)]', [LCstart(ndxIntraLC_A,3) LCend(ndxIntraLC_A,3)]', 'Color', 'red');
% hSingleLCDiveB = line([LCstart(ndxIntraLC_B,2) LCend(ndxIntraLC_B,2)]', [LCstart(ndxIntraLC_B,3) LCend(ndxIntraLC_B,3)]', 'Color', 'magenta');
% hMultiLC = line([LCstart(ndxInterLC,2) LCend(ndxInterLC,2)]', [LCstart(ndxInterLC,3) LCend(ndxInterLC,3)]', 'Color', 'green');
% 
% hDiveA = plot(sWreckA{E}(1:wreckALength), sWreckA{N}(1:wreckALength), 'c.');
% hDiveB = plot(sWreckA{E}(wreckALength:length(sWreckA{E})) + diveOffset, sWreckA{N}(wreckALength:length(sWreckA{E})), 'b.');
% %ndxSurveyA = find(abs(LCstart(:,1) - LCend(:,1)) < 2e4);
% %ndxSurveyB = find(abs(LCstart(:,1) - LCend(:,1)) > 2e4);
% 
% legend([hDiveA, hDiveB, hSingleLCDiveA(1), hSingleLCDiveB(1), hMultiLC(1)], 'Dive A', 'Dive B', 'Intra-session LC Dive A', 'Inter-session LC Dive B', 'Inter-session LC');
% axis equal
% %axis tight
% grid on
% xlabel('East (m)');
% ylabel('North (m)');
% 
% orient landscape
% print -dpdf 'AntikytheraMultiSessionSLAMCombined.pdf'
% close 
%     
% % for i = 1:length(poseMatch)
% %     j = poseMatch(i);
% %     if (j > 0)
% %         plot([sWreckARelativePoses{E}(i) sWreckA{E}(j)], [sWreckARelativePoses{N}(i) sWreckA{N}(j)], 'r')
% %     end
% % end
% 
% figure(4)
% scatter3(sWreckA{E}, sWreckA{N}, -depth, 5, depth)
% hold on
% axis equal
% %colorbar
% rotate3d
% title('Position vs Depth');
% xlabel('East (m)');
% ylabel('North (m)');
% zlabel('Depth (m)');
% % % if (exist('lc_pose_ids'))
% % %     for i=1:size(lc_pose_ids,1)
% % %        index1 = find(sWreckA{INDX}==lc_pose_ids(i,1) );
% % %        index2 = find(sWreckA{INDX}==lc_pose_ids(i,2) );
% % % 
% % %        plot3( [sWreckA{E}(index1),sWreckA{E}(index2)], [sWreckA{N}(index1), sWreckA{N}(index2)], [-depth(index1), -depth(index2)], linkcol ) 
% % %     end    
% % % end
% 
% figure(5)
% subplot(2,1,1)
% plot(sWreckA{TIME}(1:wreckALength)-sWreckA{TIME}(1), sWreckA{ALT}(1:wreckALength))
% ylabel('Alt. (m)');
% subplot(2,1,2)
% plot(sWreckA{TIME}(1:wreckALength)-sWreckA{TIME}(1), -sWreckA{DEPTH}(1:wreckALength))
% hold on
% plot(sWreckA{TIME}(1:wreckALength)-sWreckA{TIME}(1), -depth(1:wreckALength))
% ylabel('Depth. (m)');
% xlabel('Mission time (s)');
% figure(6)
% subplot(2,1,1)
% plot(sWreckA{TIME}(wreckALength+1:length(sWreckA{E}))-sWreckA{TIME}(wreckALength+1), sWreckA{ALT}(wreckALength+1:length(sWreckA{E})))
% ylabel('Alt. (m)');
% subplot(2,1,2)
% plot(sWreckA{TIME}(wreckALength+1:length(sWreckA{E}))-sWreckA{TIME}(wreckALength+1), -sWreckA{DEPTH}(wreckALength+1:length(sWreckA{E})))
% hold on
% plot(sWreckA{TIME}(wreckALength+1:length(sWreckA{E}))-sWreckA{TIME}(wreckALength+1), -depth(wreckALength+1:length(sWreckA{E})))
% ylabel('Depth. (m)');
% xlabel('Mission time (s)');
