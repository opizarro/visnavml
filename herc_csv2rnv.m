% read DATs in directory and create a rnv structure for HERC JDS

% python script used to create csv from DAT.

%csv_file = '/Users/opizarro/data/hercrawnav/H1279_1280.csv';
%csv_file = '/Users/opizarro/data/hercrawnav/H1279_1284.csv';
csv_file = '/Users/opizarro/data/hercrawnav/H1279_1288.csv';

navmat = csvread(csv_file);




% create rnv structure
rnv.t = navmat(:,1);
rnv.lat = navmat(:,2);
rnv.lon = navmat(:,3);
rnv.pos = navmat(:,4:6);
rnv.alt = navmat(:,7);
rnv.fname_base = 'H1279_1284nav'

% invert depth
rnv.pos(:,3) = -rnv.pos(:,3);

%save '~/data/sentry201307/git/massproc_herc/H1279_1284.mat'
save '~/data/sentry201307/git/massproc_herc/H1279_1288.mat'
