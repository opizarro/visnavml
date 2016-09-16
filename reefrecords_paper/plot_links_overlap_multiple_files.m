% script to read multiple pose and relative pose files
% assumes that the target files are in a text file

fid_poses = fopen('/Users/opizarro/data/pose_file_locations_box.txt');
fid_rel_poses = fopen('/Users/opizarro/data/rel_pose_file_locations_box.txt');
pose_list = textscan(fid_poses,'%s');
rel_pose_list = textscan(fid_rel_poses,'%s');

num_dives =  length(pose_list{1});

cum_LCcount = [];
cum_blinks = [];

for k = 1:num_dives
%for k = 1:1    
    pose_file = pose_list{1}{k};
    fprintf('processing %s\n',pose_file)
    rel_pose_file = rel_pose_list{1}{k};
    [LCcount_images, blanket_links]=plot_links_overlap_func(pose_file, rel_pose_file);
    cum_LCcount = [cum_LCcount; LCcount_images];
    cum_blinks = [cum_blinks; blanket_links];
end

figure(4);hist(cum_LCcount,[0:140])


fid_poses = fopen('pose_file_locations_spiral.txt');
fid_rel_poses = fopen('rel_pose_file_locations_spiral.txt');
pose_list = textscan(fid_poses,'%s');
rel_pose_list = textscan(fid_rel_poses,'%s');

num_dives =  length(pose_list{1});

cum_LCcount_sp = [];
cum_blinks_sp = [];
for k = 1:num_dives
%for k = 1:1
    pose_file = pose_list{1}{k};
    fprintf('processing %s\n',pose_file)
    rel_pose_file = rel_pose_list{1}{k};
    [LCcount_images, blanket_links] = plot_links_overlap_func(pose_file, rel_pose_file);
    cum_LCcount_sp = [cum_LCcount_sp; LCcount_images];
    cum_blinks_sp = [cum_blinks_sp; blanket_links];
end

figure(5);hist(cum_LCcount_sp,[0:140])


figure(6);
histogram(cum_LCcount,[0:140],'facecolor','b','Normalization','probability','facealpha',.5)
hold on;
histogram(cum_LCcount_sp,[0:140],'facecolor','g','Normalization','probability','facealpha',.5)
hold off;


if 0
figure(11);
Hbox=histogram(cum_blinks,[0.5:9.5],'facecolor','r','Normalization','probability','facealpha',.5)
hold on;
Hsp=histogram(cum_blinks_sp,[0.5:9.5],'facecolor','g','Normalization','probability','facealpha',.5)
hold off;
legend('mow the lawn','spiral')
xlabel('shortest path (in links) to cameras within 2*median(link size)')
end

figure(12);
bar([Hbox.Values' Hsp.Values'],'hist')
legend('mow the lawn','spiral')
xlabel('shortest path (in links) to cameras within 2*median(link size)')
