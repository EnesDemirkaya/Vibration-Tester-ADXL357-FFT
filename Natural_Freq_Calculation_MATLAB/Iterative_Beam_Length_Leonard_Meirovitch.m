clc;   % Clear the command window.
clear; % Clear all variables from the workspace.

% Beam Details Setup:
Bb = 50.8e-3;    % Width of the beam in meters (50.8 mm).
d = 2700;        % Density of the beam material in kg/m^3 (for Aluminum).
E = 70e9;        % Modulus of elasticity of the beam material in Pascals (for Aluminum).
Mt = 0.01;       % Tip mass in kilograms (0.01 kg).

% Define Lengths and Preallocate Storage:
L_values = linspace(0.2, 1, 200);  % Array of beam lengths from 0.2m to 1m, with 200 points.
Db = 2e-3;       % Depth (thickness) of the beam in meters (2 mm).
fn_values = zeros(4, length(L_values));  % Preallocate matrix to store the first 4 natural frequencies.

% Symbolic Variables and Equation Setup:
syms bL_sym  % Define a symbolic variable for the product of the wave number and beam length.
C = cos(bL_sym);
S = sin(bL_sym);
Ch = cosh(bL_sym);
Sh = sinh(bL_sym);
A1 = (S + Sh) / (C + Ch);  % Combination of trigonometric and hyperbolic functions.

% Define a function handle to generate the characteristic equation.
eqn_template = @(m, Mt, L) m * (-cos(bL_sym) - cosh(bL_sym) - A1 * (sin(bL_sym) - sinh(bL_sym))) + ...
                          Mt * (bL_sym / L) * (sin(bL_sym) - sinh(bL_sym) - A1 * (cos(bL_sym) - cosh(bL_sym))) == 0;

% Precompute the lengths in centimeters:
L_values_cm = L_values * 100;  % Convert length values from meters to centimeters for plotting.

% Loop Over Length Values to Calculate Natural Frequencies:
for j = 1:length(L_values)
    L = L_values(j);  % Current length of the beam.
    Mb = (L * Bb * Db) * d;  % Mass of the beam (kg).
    I = Bb * Db^3 / 12;  % Second moment of area of the beam's cross-section.
    m = Mb / L;  % Mass per unit length of the beam (kg/m).

    % Generate the characteristic equation using the template:
    eqn = eqn_template(m, Mt, L);

    % Solve for the first 4 solutions within a specified range:
    bLi = [];
    search_start = 1;  % Start point for the search range in the solver.
    search_end = 2;    % End point for the search range in the solver.
    while length(bLi) < 4 && search_end <= 30
        bL_sol = vpasolve(eqn, bL_sym, [search_start, search_end]);  % Solve the equation.
        bL_sol = double(bL_sol);  % Convert symbolic solution to double.
        bLi = [bLi, bL_sol.'];  % Store the solutions.
        search_start = search_end;  % Update the search range.
        search_end = search_end + 1;
    end

    if length(bLi) < 4
        warning('Not enough solutions found for L=%.2f and Db=%.2f', L, Db);
        continue; % Skip this iteration if not enough solutions are found.
    end

    bLi = bLi(1:4);  % Take the first 4 solutions.

    % Calculate natural angular frequencies (wn) and convert to Hz:
    wn = bLi.^2 * sqrt((E * I) / (m * L^4));  % Natural angular frequencies.
    fn = wn / (2 * pi);  % Convert to natural frequencies in Hz.

    fn_values(:, j) = fn;  % Store the frequencies for the current length.
end

% Plotting the Natural Frequencies:
figure;
hold on;
colors = ['b', 'b', 'b', 'b'];  % Colors for the plots.
line_styles = {'-', '--', ':', '-.'};  % Line styles for different modes.

% Plot each mode's natural frequency vs. beam length:
for i = 1:4
    if all(fn_values(i, :) == 0)
        continue; % Skip if no valid data for this mode.
    end
    plot(L_values_cm, fn_values(i, :), 'Color', colors(i), 'LineStyle', line_styles{i}, ...
         'DisplayName', ['Mode ' num2str(i)]);
end

% Add labels, title, grid, and legend to the plot:
xlabel('Length (cm)');
ylabel('Natural Frequencies (Hz)');
title('Natural Frequencies vs. Length of Beam (Thickness = 2mm)');
set(gca, 'YScale', 'log');  % Set y-axis to logarithmic scale.
grid on;
legend('show', 'Location', 'northeastoutside');

% Save the Plot to a Folder:
output_folder = 'output_figures';  % Specify the output folder.
if ~exist(output_folder, 'dir')
    mkdir(output_folder);  % Create the folder if it doesn't exist.
end
output_filename = sprintf('2D_Plot_TipMass_%.1fkg_Material_Aluminum_Width_%.2fcm_Depth_2mm', Mt, Bb*100);
saveas(gcf, fullfile(output_folder, [output_filename, '.png']));  % Save as PNG.
savefig(fullfile(output_folder, [output_filename, '.fig']));  % Save as FIG.

disp('2D Figure saved successfully.');
