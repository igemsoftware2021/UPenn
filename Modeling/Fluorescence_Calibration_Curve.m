% Files with plate reader data
fileNames = {'20210608_DyeFC.csv','20210608_12xFC.csv','20210609_36xFC.csv','20210609_108xFC.csv','20210609_324xFC.csv','20210609_972xFC.csv','20210608_2916xFC.csv', '20210609_WaterFC.csv'};
% Took out '20210609_WaterFC.csv'
% Took out '20210608_2916xFC.csv'

% Declare variables
numDils = 8;
byWell = zeros(96,numDils);
xAxDils = zeros(96,numDils);
dyeConc = (0.25*0.001/(444.24*0.001)); % Molarity of 4x diluted dye which should be ~5.627e-4

% Put averages of all 100 readings per well into matrix
% Matrix will be 96 rows for each well, 8 columns for each dilution
for k = 1:numDils
    file = readmatrix(fileNames{k});
    avgs = mean(file, 2);
    byWell(1:96,k) = avgs;
 
    % Define matrix
    one = ones(96,1);
    
    % Different ways to plot the x axis
    xAxDils(1:96,k) = (dyeConc/(3^(k-1)))*one; % Using actual dye molarity
    %xAxDils(1:96,k) = 4*(3^(k-1))*one;          % Using dilution factor
    %xAxDils(1:96,k) = k - 1;                   % Using 1,2,3,4,5,6,7,8
end

xAxDils(:,numDils) = (10^-80)*ones(96,1);

% Make plot log log
xAxDils = log(xAxDils);
byWell = log(byWell);

% Declare matrix
fitMatrix = zeros(96,4);

% Determine the fit coefficients for each row and save into matrix
for y = 1:96
    % Declare which row you are working with
    byWellRow = byWell(y,1:numDils);
    xAxDilsRow = xAxDils(y,1:numDils);
    
    % Determine fit
    [fitresult,var1,coeff] = createFit1(xAxDilsRow, byWellRow);
    
    % Save into fitMatrix
    fitMatrix(y,1:4) = coeff;
end

% Plot only the last data set
figure( 'Name', 'untitled fit 1' );
plot( fitresult );
hold on
plot(xAxDilsRow, byWellRow,'b.','MarkerSize',20);
% Label axes
xlabel( 'Molarity (logged) [mol/L]', 'Interpreter', 'none','FontSize',15 );
ylabel( 'Photodiode Reading (logged) [arbitrary units]', 'Interpreter', 'none', 'FontSize', 15 );
title('Calibration curve', 'FontSize',20);
lgd = legend('fitted curve', 'data');
lgd.Location = 'northwest';
set(gcf, 'color','white');
grid on

%Fit equation: a/(1+exp((-x+c)/b))+d
%4x dye concentration is 5.627e-4 mol/L