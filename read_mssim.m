function varargout = read_mssim(fname)
% Parse MSSIM log.
%
%
% Revision History
% 2009-09-15    mvj    Created.

MAX_SIM = 30;
MAX_MZ = 300;

% Construct mssim fmt string.
mssimfmt = '';
mssimdat = '';
for n=1:MAX_SIM
  mssimfmt = [mssimfmt ' %d %f'];
  mssimdat = [mssimdat sprintf('c.mz(:,%d),c.peak(:,%d),',n,n)];
end
mssimdat = mssimdat(1:end-1);

[mssim.t,mssim.start_year,mssim.start_month,mssim.start_day,mssim.start_hour,mssim.start_minute,mssim.start_second] = deal(NaN);
str = sprintf(['[mssim.end_year,mssim.end_month,mssim.end_day,mssim.end_hour,mssim.end_minute,mssim.end_second,' ...
      'mssim.dt,' ...
      'mssim.start_temperature,mssim.start_conductivity,mssim.start_pressure,mssim.start_salinity,mssim.start_soundspeed,' ...
      'mssim.end_temperature,mssim.end_conductivity,mssim.end_pressure,mssim.end_salinity,mssim.end_soundspeed,' ...
      'mssim.filename,' ...
      'mssim.file_number,' ...
      'mssim.cycle_number,' ...
      'mssim.mission_step_number,' ...
      'mssim.mission_mssim_number,' ...
      'mssim.record_number,' ...
      '%s' ...
      '] = textread(fname,''MSSIM %%d/%%d/%%d %%d:%%d:%%f ' ...
      '%%f ' ...
      '%%f %%f %%f %%f %%f ' ...
      '%%f %%f %%f %%f %%f ' ...
      '%%s %%d %%d %%d %%d %%d' ...
      '%s%%*[^\\n]'');'], ...
    mssimdat, ...
    mssimfmt);
eval(str)

% Center timestamp in interval.
mssim.t = ymdhms_to_sec(mssim.end_year,mssim.end_month,mssim.end_day,mssim.end_hour,mssim.end_minute,mssim.end_second);
[mssim.start_year,mssim.start_month,mssim.start_day,mssim.start_hour,mssim.start_minute,mssim.start_second] = ...
    sec_to_ymdhms(mssim.t - mssim.dt);
mssim.t = mssim.t-mssim.dt/2;
mssim.t = mssim.t-30.0;  % 2009-09-25    mvj    On RC's advice, shift data back additional 30 s.

N = min(size(mssim.t,1),size(c.peak,1));
mssim = sext(mssim,1:N);
c = sext(c,1:N);

% Sort mz data to make indexing easier.
N = length(mssim.t);
mssim.peak = NaN*zeros(N,MAX_MZ);
for n = 1:N
  m = 1;
  while(m <= MAX_SIM && c.mz(n,m) > 0)
    mssim.peak(n,c.mz(n,m)) = c.peak(n,m);
    m = m+1;
  end
end
  
if nargout == 0
  assignin('caller','mssim',mssim);
else
  varargout{1} = mssim;
end
