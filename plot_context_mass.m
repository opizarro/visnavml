function plot_context_mass(px,py,pz,alt,t,basefig)


    
figure(basefig);
subplot(4,1,1)
plot(t-t(1),pz)
ylabel('depth [m]')

subplot(4,1,2)
plot(t-t(1),px,'.')
ylabel('x [m]')

subplot(4,1,3)
plot(t-t(1),py,'.')
ylabel('y [m]')

subplot(4,1,4)
plot(t-t(1),alt)
ylabel('alt [m]')

figure(basefig+1);
plot(px,py,'.')

figure(basefig+3);
subplot(2,1,1)
plot(t(1:end-1)-t(1),diff(t))
ylabel('dt [s]')
subplot(2,1,2)
plot(t(1:end-1)-t(1), ((diff(px).^2+diff(py).^2).^0.5 )./(diff(t)) )
ylabel('speed [m/s]')

figure(basefig+2)
subplot(2,1,1)
hist(pz,100)
xlabel('depth [m]')
subplot(2,1,2)
hist(alt,[0:100])
xlabel('altitude [m]')