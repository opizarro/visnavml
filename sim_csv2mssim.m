% read DATs in directory and create a rnv structure for HERC JDS

% python script used to create csv from DAT.

dive = 'H1288';
path = '/Users/opizarro/data/sentry201307/git/massproc_herc/';
csv_file = sprintf('%s%smass.csv',path,dive)

%csv_file = '/Users/opizarro/data/sentry201307/git/massproc_herc/H1280mass.csv';
%csv_file = '/Users/opizarro/data/sentry201307/git/massproc_herc/H1280mass.csv';
%csv_file = '/Users/opizarro/data/sentry201307/git/massproc_herc/H1280mass.csv';

mssim_mat = csvread(csv_file);

mssim.start_year = mssim_mat(:,1) ;
mssim.start_month = mssim_mat(:,2);
mssim.start_day =  mssim_mat(:,3);
mssim.start_hour = mssim_mat(:,4) ;
mssim.start_minute = mssim_mat(:,5);
mssim.start_second = mssim_mat(:,6);

unixtime_start = ymdhms_to_sec(mssim.start_year,mssim.start_month,mssim.start_day,...
                            mssim.start_hour,mssim.start_minute,mssim.start_second);
    
mssim.end_year = mssim_mat(:,7);
mssim.end_month = mssim_mat(:,8);
mssim.end_day = mssim_mat(:,9);
mssim.end_hour = mssim_mat(:,10);
mssim.end_minute = mssim_mat(:,11);
mssim.end_second = mssim_mat(:,12);

unixtime_end = ymdhms_to_sec(mssim.start_year,mssim.start_month,mssim.start_day,...
                            mssim.start_hour,mssim.start_minute,mssim.start_second);
   
mssim.peak = mssim_mat(:,14:18);


mssim.start_temperature = mssim_mat(:,19);
mssim.start_conductivity = mssim_mat(:,20);
mssim.start_pressure = mssim_mat(:,21);
mssim.start_salinity = mssim_mat(:,22);
mssim.start_soundspeed = mssim_mat(:,23);

mssim.end_temperature = mssim_mat(:,24);
mssim.end_conductivity = mssim_mat(:,25);
mssim.end_pressure = mssim_mat(:,26);
mssim.end_salinity = mssim_mat(:,27);
mssim.end_soundspeed = mssim_mat(:,28);




cmd = ['save ' sprintf('%s%smass.mat',path,dive) ' mssim']
eval(cmd)
%save '/Users/opizarro/data/sentry201307/git/massproc_herc/H1279mass.mat' mssim 
