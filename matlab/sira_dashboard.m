function sira_dashboard(episodes_file, output_dir)
% SIRA_DASHBOARD MATLAB Advanced Analytics Dashboard for SIRA
%
% Main entry point for SIRA advanced analytics. Loads episodes data,
% performs analyses, generates visualizations, and creates PDF report.
%
% Inputs:
%   episodes_file - Path to episodes.mat file (default: 'data/matlab/episodes.mat')
%   output_dir - Directory for output files (default: 'data/matlab/reports')
%
% Outputs:
%   PDF report saved to output_dir
%   Figures saved as PNG files
%
% Example:
%   sira_dashboard();  % Use defaults
%   sira_dashboard('my_episodes.mat', 'my_reports/');
%
% Requirements:
%   - MATLAB R2020a or later
%   - Statistics and Machine Learning Toolbox
%   - Image Processing Toolbox (for PDF generation)
%
% Author: SIRA Team
% Date: 2025-11-27

% Set defaults
if nargin < 1 || isempty(episodes_file)
    episodes_file = fullfile('data', 'matlab', 'episodes.mat');
end

if nargin < 2 || isempty(output_dir)
    output_dir = fullfile('data', 'matlab', 'reports');
end

% Create output directory if it doesn't exist
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

fprintf('\n========================================\n');
fprintf('SIRA Advanced Analytics Dashboard\n');
fprintf('========================================\n\n');

%% 1. Load Episodes Data
fprintf('Loading episodes from: %s\n', episodes_file);
try
    episodes = load_episodes(episodes_file);
    fprintf('✓ Loaded %d episodes\n\n', length(episodes));
catch ME
    error('Failed to load episodes: %s', ME.message);
end

%% 2. Learning Velocity Analysis
fprintf('Computing learning velocity...\n');
addpath('analytics');
[velocity, velocity_stats] = learning_velocity(episodes);

%% 3. Pattern Effectiveness Analysis
fprintf('Analyzing pattern effectiveness...\n');
[effectiveness, heatmap_data] = pattern_effectiveness(episodes);

%% 4. Generate Visualizations
fprintf('Generating visualizations...\n');
addpath('visualizations');

% Quality trends plot
fig1 = plot_quality_trends(episodes, velocity_stats);
trends_file = fullfile(output_dir, 'quality_trends.png');
saveas(fig1, trends_file);
fprintf('✓ Saved: %s\n', trends_file);

% Domain heatmap
fig2 = heatmap_domains(heatmap_data);
heatmap_file = fullfile(output_dir, 'domain_heatmap.png');
saveas(fig2, heatmap_file);
fprintf('✓ Saved: %s\n\n', heatmap_file);

%% 5. Generate PDF Report
fprintf('Generating PDF report...\n');
report_file = fullfile(output_dir, sprintf('sira_report_%s.pdf', datestr(now, 'yyyymmdd_HHMMSS')));

try
    generate_pdf_report(report_file, episodes, velocity_stats, effectiveness, ...
                        trends_file, heatmap_file);
    fprintf('✓ PDF Report: %s\n\n', report_file);
catch ME
    warning('PDF generation failed: %s', ME.message);
    fprintf('Continuing without PDF...\n\n');
end

%% 6. Summary and Recommendations
fprintf('========================================\n');
fprintf('ANALYSIS SUMMARY\n');
fprintf('========================================\n\n');

fprintf('Learning Performance:\n');
fprintf('  Learning Velocity: %.6f quality/hour\n', velocity);
fprintf('  R² (fit quality): %.4f\n', velocity_stats.r_squared);
fprintf('  Improvement: %.2f%%\n\n', velocity_stats.improvement_pct);

fprintf('Pattern Effectiveness:\n');
fprintf('  Domains analyzed: %d\n', length(effectiveness.by_domain));
fprintf('  Pattern types: %d\n', length(effectiveness.by_pattern));
if ~isempty(effectiveness.best_combinations)
    fprintf('  Best combination: %s + %s (%.4f)\n\n', ...
            effectiveness.best_combinations(1).domain, ...
            effectiveness.best_combinations(1).pattern, ...
            effectiveness.best_combinations(1).quality);
end

fprintf('Recommendations:\n');
generate_recommendations(velocity_stats, effectiveness);

fprintf('\n========================================\n');
fprintf('Dashboard complete!\n');
fprintf('========================================\n\n');

end


%% Helper Functions

function generate_pdf_report(filename, episodes, velocity_stats, effectiveness, ...
                             trends_file, heatmap_file)
% Generate PDF report with all analyses and visualizations

% Create temporary figure for report
fig = figure('Visible', 'off', 'Position', [0, 0, 800, 1000]);

% Title page
annotation('textbox', [0.1, 0.85, 0.8, 0.1], ...
           'String', 'SIRA Analytics Report', ...
           'FontSize', 24, 'FontWeight', 'bold', ...
           'HorizontalAlignment', 'center', ...
           'EdgeColor', 'none');

annotation('textbox', [0.1, 0.75, 0.8, 0.08], ...
           'String', sprintf('Generated: %s', datestr(now)), ...
           'FontSize', 12, ...
           'HorizontalAlignment', 'center', ...
           'EdgeColor', 'none');

% Key Metrics
metrics_text = sprintf(['KEY METRICS\n\n' ...
                        'Episodes Analyzed: %d\n' ...
                        'Learning Velocity: %.6f quality/hour\n' ...
                        'R² (fit quality): %.4f\n' ...
                        'Improvement: %.2f%%\n' ...
                        'Avg Quality: %.4f\n\n' ...
                        'Domains: %d\n' ...
                        'Pattern Types: %d'], ...
                       velocity_stats.num_episodes, ...
                       velocity_stats.slope, ...
                       velocity_stats.r_squared, ...
                       velocity_stats.improvement_pct, ...
                       velocity_stats.avg_quality_overall, ...
                       length(effectiveness.by_domain), ...
                       length(effectiveness.by_pattern));

annotation('textbox', [0.1, 0.45, 0.8, 0.25], ...
           'String', metrics_text, ...
           'FontSize', 10, ...
           'BackgroundColor', [0.95 0.95 0.95], ...
           'EdgeColor', 'black');

% Save title page
exportgraphics(fig, filename, 'ContentType', 'vector');

% Append visualizations
if exist(trends_file, 'file')
    img = imread(trends_file);
    clf(fig);
    imshow(img);
    title('Quality Trends Over Time', 'FontSize', 16);
    exportgraphics(fig, filename, 'Append', true);
end

if exist(heatmap_file, 'file')
    img = imread(heatmap_file);
    clf(fig);
    imshow(img);
    title('Pattern Effectiveness Heatmap', 'FontSize', 16);
    exportgraphics(fig, filename, 'Append', true);
end

close(fig);
end


function generate_recommendations(velocity_stats, effectiveness)
% Generate actionable recommendations based on analysis

recommendations = {};

% Learning velocity recommendations
if velocity_stats.slope > 0.001
    recommendations{end+1} = '✓ Strong learning trend detected. Continue current pattern refinement approach.';
elseif velocity_stats.slope > 0
    recommendations{end+1} = '⚠ Weak learning trend. Consider increasing pattern diversity or refinement frequency.';
else
    recommendations{end+1} = '✗ No learning improvement. Review pattern extraction and quality scoring logic.';
end

% R² recommendations
if velocity_stats.r_squared < 0.5
    recommendations{end+1} = '⚠ Low R² suggests inconsistent quality. Investigate outliers or quality scoring issues.';
end

% Domain coverage
if isempty(effectiveness.best_combinations)
    recommendations{end+1} = '⚠ Insufficient pattern-domain data. Increase episode volume across domains.';
else
    best_domain = effectiveness.best_combinations(1).domain;
    recommendations{end+1} = sprintf('✓ Focus on expanding patterns for high-performing domain: %s', best_domain);
end

% Print recommendations
for i = 1:length(recommendations)
    fprintf('  %d. %s\n', i, recommendations{i});
end
end
