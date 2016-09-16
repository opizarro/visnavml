% csv of time, lat, lon, depth, alt from rnv

function write_pose_csv(rnv) 

fname = sprintf('%s_camint.csv',rnv.fname_base);

navmat = [rnv.t(1:5:end) rnv.lat(1:5:end) rnv.lon(1:5:end) rnv.pos(1:5:end,3) rnv.alt(1:5:end)];

dlmwrite(fname, navmat,'precision','%.7f')