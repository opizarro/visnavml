% first stab at collapsing some of the image clusters
A=importdata('georef_labels_test.csv');


labels_o = A(:,7);

labels_n = zeros(size(labels_o));

% mapping assingment
% new classes: 
%1=high altitude?
%2=not busy
%3=carbonate
%4=microbes
%5=clams 
%6=brine pool 
%7=brine 2

clp(1) = 4;
clp(2) = 2;
clp(3) = 2;
clp(4) = 5;
clp(5) = 2;
clp(6) = 7;
clp(7) = 1;
clp(8) = 5;
clp(9) = 3;
clp(10) = 1;
clp(11) = 6;

for i = 1:length(clp)
    selclp = (labels_o == i);
    labels_n(selclp) = clp(i)
end

figure(1);
scatter(A(:,4),A(:,5),[],A(:,7),'filled')
grid on;

figure(2);
scatter(A(:,4),A(:,5),[],labels_n,'filled')
grid on;

depth = -A(:,6);

M = [A(:,3) A(:,2) depth labels_n];

dlmwrite('georef_collapsed_labels.csv',M,'precision',7);