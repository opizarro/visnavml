function [LCcount_images, blinks] =plot_links_overlap_func(pose_file, rel_pose_file)

fid=fopen(pose_file);
orig = textscan(fid, '%*s %f', 2,'CommentStyle','%');
sWreckA = textscan(fid, '%d%f%f%f%f%f%f%f%f%f%s%s%f%f%d','CommentStyle','%', 'Headerlines', 2);

fidRel=fopen(rel_pose_file);
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

if nImg > 1
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


wreckCol{1} = 'c.';

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

Amat = sparse(nImg, nImg);
Dmat = zeros(nImg, nImg);

for i=1:nImg
    for j=i+1:nImg
        camd = norm([(sWreckA{N}(i)-sWreckA{N}(j)), (sWreckA{E}(i)-sWreckA{E}(j))]);
        Dmat(i,j) = camd;
        Dmat(j,i) = camd;
    end
end





figure
hold on
axis equal
axis([min(sWreckA{E}) max(sWreckA{E}) min(sWreckA{N}) max(sWreckA{N})]);


% Dive plots
for diveNdx = 1:1
%    figure(dive)
    hDive(diveNdx) = plot(sWreckA{E}(wreckNdx{diveNdx}), sWreckA{N}(wreckNdx{diveNdx}), '.r','MarkerSize',3);
    %hDive(diveNdx) = plot(sWreckA{E}(wreckNdx{diveNdx}), sWreckA{N}(wreckNdx{diveNdx}), wreckCol{diveNdx},'.r');
    
%    orient landscape
%    print -dpdf 'AntikytheraMultiSessionSLAMDiveA.pdf'
%    close
end
%axis tight
grid on
xlabel('East (m)');
ylabel('North (m)');



for i = 1:numSkip:numLinks
   ndxstart = find(strcmp(sWreckARelativePoses{REL_LEFT_A}(i), sWreckA{LEFT_IMG}));
   ndxend = find(strcmp(sWreckARelativePoses{REL_LEFT_B}(i), sWreckA{LEFT_IMG}));
   LCcount_images(ndxstart) = LCcount_images(ndxstart) + 1;
   LCcount_images(ndxend) = LCcount_images(ndxend) + 1;
   
   % populate adjency matrix and distance matrix
   Amat(ndxstart,ndxend) = 1;
   Amat(ndxend,ndxstart) = 1;
  
   
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
           sprintf('%d of %d',k, length(sWreckARelativePoses{REL_LEFT_A}));
       end
       % using figure hold above loop
       Hline=line([sWreckA{E}(ndxstart); sWreckA{E}(ndxend)],[sWreckA{N}(ndxstart); sWreckA{N}(ndxend)]);
       set(Hline,'LineWidth',0.001,'Color',[0 0.4470 0.7410, 0.75]);
   end   
end

for diveNdx = 1:1
%    figure(dive)
    hDive(diveNdx) = plot(sWreckA{E}(wreckNdx{diveNdx}), sWreckA{N}(wreckNdx{diveNdx}), '.r','MarkerSize',3);
    %hDive(diveNdx) = plot(sWreckA{E}(wreckNdx{diveNdx}), sWreckA{N}(wreckNdx{diveNdx}), wreckCol{diveNdx},'.r');
    
%    orient landscape
%    print -dpdf 'AntikytheraMultiSessionSLAMDiveA.pdf'
%    close
end

[pathstr,pose_file_divename]=fileparts(fileparts(fileparts(pose_file)))

cmd = sprintf('print -dpdf %s.pdf',pose_file_divename)
eval(cmd)

close(gcf)

ndxIntraLC = find(LCstart(:,6) == LCend(:,6));
ndxInterLC = find(LCstart(:,6) ~= LCend(:,6));


% % figure
% % hDensity=imagesc([minE,max(sWreckA{E})],[minN,max(sWreckA{N})],log10(LCdensity'+1))
% % set(gca,'YDir','normal')
% % xlabel('East (m)');
% % ylabel('North (m)');
% % axis equal
% % axis tight
% % colorbar
% % y=get(colorbar,'YTick');
% % h=colorbar('YTickLabel',round(10.^y-1));
% % cmap = colormap('bone');
% % %colormap(flipud(cmap));
% % colormap jet
% % ylabel(h, 'density of image overlap [counts/m^2]')


%print -dpdf 'horseshoe_circle01_201404_16_LCDensity.pdf'
%print -dpng 'horseshoe_circle01_201404_16_LCDensity.png'

% histogram of number of links per image
figure(4);hist(LCcount_images,[0:140]);

blinks = [];
if 0 % don't do the Dijkstra calculation
%if calc_blank == true
    
    [Acosts,paths]=dijkstra(Amat,Amat,[],[],true);


    % go over adjancency and distance matrices
    % figure out distance for blanket
    Dut = triu(Dmat.*Amat);
    medD = full(median(Dut(Dut > 0)));
    figure(200); hist(Dut(Dut >0),[0:0.1:5])
    fprintf('Median distance is %.2f\n',medD);
    blanket_mat = ((Dmat <= 2*medD) & (Dmat > 0));

    % all links within blanket
    %blinks_mat = Acosts.*double(blanket_mat);
    blinks_mat = Acosts((Dmat <= 2*medD) & (Dmat > 0));

    % as a vector:
    blinks = blinks_mat(:);
    blinks = blinks(~isinf(blinks));

    figure(100);imagesc(Amat);title('Adjacency matrix');colorbar;
    figure(101);imagesc(Dmat);title('Distance matrix');colorbar;
    figure(102);imagesc(blanket_mat);title('blanket matrix');colorbar;
    figure(103);imagesc(Acosts);title('Dijkstra costs');colorbar;
    figure(104);imagesc(blinks_mat);title('blanket links matrix');colorbar;

end
 




else
       fprintf('Warning: no images found!\n');
    LCcount_images = [];
    blinks = [];
end

    
    


