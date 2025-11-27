function fig = plot_quality_trends(episodes, velocity_stats)
% PLOT_QUALITY_TRENDS Plot quality improvement over time
%
% Creates a time series plot showing quality scores over episodes
% with trend line and statistics.
%
% Inputs:
%   episodes - Structure array with episode data
%   velocity_stats - Statistics from learning_velocity()
%
% Outputs:
%   fig - Figure handle
%
% Example:
%   [vel, stats] = learning_velocity(episodes);
%   fig = plot_quality_trends(episodes, stats);

% Extract data
timestamps = [episodes.timestamp]';
quality_scores = [episodes.quality_score]';

% Convert timestamps to hours
first_time = min(timestamps);
hours = (timestamps - first_time) / 3600;

% Create figure
fig = figure('Position', [100, 100, 800, 500]);

% Plot quality scores
plot(hours, quality_scores, 'o', 'MarkerSize', 4, 'MarkerFaceColor', [0.3 0.6 0.9]);
hold on;

% Plot trend line
if isfield(velocity_stats, 'slope') && isfield(velocity_stats, 'intercept')
    trend_y = velocity_stats.slope * hours + velocity_stats.intercept;
    plot(hours, trend_y, 'r-', 'LineWidth', 2);
end

% Add moving average
window = min(50, floor(length(quality_scores)/10));
if window > 1
    moving_avg = movmean(quality_scores, window);
    plot(hours, moving_avg, 'g--', 'LineWidth', 1.5);
end

% Labels and title
xlabel('Time (hours)');
ylabel('Quality Score');
title('SIRA Quality Improvement Over Time');
legend('Episodes', 'Trend Line', 'Moving Average', 'Location', 'best');
grid on;

% Add statistics text box
if isfield(velocity_stats, 'improvement_pct')
    text_str = sprintf(['Velocity: %.6f q/hr\n' ...
                        'R²: %.4f\n' ...
                        'Improvement: %.2f%%'], ...
                       velocity_stats.slope, ...
                       velocity_stats.r_squared, ...
                       velocity_stats.improvement_pct);
    annotation('textbox', [0.15, 0.75, 0.25, 0.15], ...
               'String', text_str, ...
               'FitBoxToText', 'on', ...
               'BackgroundColor', 'white', ...
               'EdgeColor', 'black');
end

hold off;
end
