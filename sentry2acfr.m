% prototype script to generate equivalent RAW.auv log files for ACFR nav
% processing from sentry nav logs

% load into memory the DVL, best attitude and depth observations by running
% read_dvl_v2
% read_gvx
% read_dep

% TODO GPS or equivalent to intialize filter
% one possiblity is to spoof a GPS fix from USBL data


% print out a RAW log file
% sort in matlab vs sort files
dvl = read_dvl_v2;
gvx = read_gvx;
dep = read_dep;

% keep n pointers

% determine which one is oldest
% print oldest one
% advance oldest one
% repeat

tdvl = dvl.t(1);
tgvx = gvx.t(1);
tdep = dep.t(1);

stream = {'dvl','gvx','dep'};
nstreams = length(stream);

kvec = ones(1,nstreams);
stream_active = ones(1,length(stream));

for i=1:nstreams
    tvec(i) = eval([stream{i} '.t(kvec(i))']);
    stream_length(i) = eval(['length(' stream{i} '.t)']);
end


%
fid=fopen('test.RAW.auv','w+');


while nstreams > 0

    [next_t_obs,next_stream_ind] = min(tvec);
    
    % print next observation
    
    
    
    i = next_stream_ind;
    k = kvec(i);
    next_stream = stream{i};
    switch next_stream
        case 'dep'
            fprintf(fid,'PAROSCI: %.3f\t%.4f\n',dep.t(k),dep.depth(k));
        case 'dvl'
            fprintf(fid,'RDI: %.3f\talt:%.3f r1:%.3f r2:%.3f r3:%.3f r4:%.3f h:%.3f p:%.3f r:%.3f vx:%.3f vy:%.3f vz:%.3f nx:%.3f ny:%.3f nz:%.3f COG:%.3f SOG:%.3f bt_status:%d h_true:%.3f p_gimbal:%.3f sv:%.3f\n',...
                dvl.t(k),dvl.altitude(k),dvl.beam_range(k),dvl.beam_range(k),dvl.beam_range(k),dvl.beam_range(k),...
                dvl.dvl_attitude(k,1),dvl.dvl_attitude(k,2),dvl.dvl_attitude(k,3),dvl.bottom_vel(k,1),dvl.bottom_vel(k,2),dvl.bottom_vel(k,3),...
                dvl.bottom_disp(k,1),dvl.bottom_disp(k,2),dvl.bottom_disp(k,3),dvl.bottom_course(k),dvl.bottom_speed(k),dvl.bottom_stat(k),...
                dvl.dvl_attitude(k,1),dvl.dvl_attitude(k,2),dvl.sound_speed(k));
        case 'gvx'
            % TODO check if rdians or degrees expected
            fprintf(fid,'3DM: %.3f  Roll:%6.2f Pitch:%6.2f Heading:%6.2f Ax:0 Ay:0 Az:0 Rx:0 Ry:0 Rz:0 iR:0 iP:0 iH:0 iAx:0 iAy:0 iAz:0 iRx:0 iRy:0 iRz:0\n',...
                gvx.t(k), gvx.roll(k), gvx.pitch(k), gvx.heading(k));
    end
        
    % increment counter
    if kvec(i)+1 <= stream_length(i)
        kvec(i) = kvec(i) + 1;        
        tvec(i) = eval([stream{i} '.t(kvec(i))']);
    else
        % that was the last data point for that stream
        % [1:i-1 i+1:nstreams]
        % stream
        stream = {stream{[1:i-1 i+1:nstreams]}};
        tvec = tvec([1:i-1 i+1:nstreams]);
        stream_length = stream_length([1:i-1 i+1:nstreams]);
        nstreams = length(stream);
    end

end

fclose(fid);


% PARO
% sprintf(logger_msg, "%s:  %.3f\t%.4f\n", cfg->label, timestamp, sensor_data.value[0]);

% DVL
%  sprintf(logger_msg, "%s:  %.3f\talt:%.3f r1:%.3f r2:%.3f r3:%.3f r4:%.3f h:%.3f p:%.3f r:%.3f vx:%.3f vy:%.3f vz:%.3f nx:%.3f ny:%.3f nz:%.3f COG:%.3f SOG:%.3f bt_status:%d h_true:%.3f p_gimbal:%.3f sv:%.3f\n",
%            cfg->label,  timestamp,  rdi->altitude,   rdi->range[0],  rdi->range[1], rdi->range[2], 
 %           rdi->range[3],  rdi->heading * RTOD, rdi->pitch * RTOD, rdi->roll * RTOD, rdi->btv.x, rdi->btv.y,
  %          rdi->btv.z, rdi->bt.x, rdi->bt.y, rdi->bt.z, rdi->bt_cog, rdi->bt_sog, rdi->bt_status, hdg_true * RTOD,
   %         gimbal_pitch * RTOD, rdi->sv);
   
   
% 3DM   
   % sprintf(logger_msg, "%s:  %.3f  Roll:%6.2f Pitch:%6.2f Heading:%6.2f Ax:%7.4f Ay:%7.4f Az:%7.4f Rx:%6.4f Ry:%6.4f Rz:%6.4f iR:%i iP:%i iH:%i iAx:%i iAy:%i iAz:%i iRx:%i iRy:%i iRz:%i\n",
% 		    cfg->label, timestamp, imu.Roll, imu.Pitch, imu.Yaw,
% 		    imu.Accel_X, imu.Accel_Y, imu.Accel_Z,
% 		    imu.Rate_X, imu.Rate_Y, imu.Rate_Z,
% 		    imu.IntRoll,imu.IntPitch,imu.IntYaw,imu.IntAccel_X,imu.IntAccel_Y,imu.IntAccel_Z,
% 		    imu.IntRate_X,imu.IntRate_Y,imu.IntRate_Z);
% 	   
%    
   
   
   
   
   