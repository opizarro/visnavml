% convert mssim mat file into a .DAT for plotting as kml


load sentry002_mssim.mat
% all peaks
% peaks = find(~isnan(mssim.peak(1,:)));
sel_peaks = [15    17    27    32    41    43    44];

% desired output format
% HST 2013/07/16 15:34:28.920740 SMS:1101,R1 SMS:1101,R1143861|005  1317165169.6 6 -289 346 -446.0 3.4 2.688e+01 1.232e+04 6.637e+03 0.00

% output file
outDAT = 'mass_mat.DAT';
fd = fopen(outDAT,'w');


for i=1:length(mssim.t)
    year = mssim.start_year(i);
    month = mssim.start_month(i);
    day = mssim.start_day(i);
    hours = mssim.start_hour(i);
    minutes = mssim.start_minute(i);
    seconds = mssim.start_second(i);
    unixtime = ymdhms_to_sec(year,month,day,hours,minutes,seconds);
    peaks = mssim.peak(i,sel_peaks);
    
    fprintf(fd,'HST %04d/%02d/%02d %02d:%02d:%02.6f SMS:1101,R1 SMS:1101,R1143861|005 %f 6 0 0 0 0 %f %f %f %f\n',year,month,day,hours,minutes,seconds,unixtime,peaks(1),peaks(2),peaks(3),peaks(4));
end
fclose(fd);

    