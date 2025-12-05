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
% Convert timestamp strings to numeric (seconds since epoch)
timestamps = zeros(length(episodes), 1);
for i = 1:length(episodes)
    if ischar(episodes(i).timestamp) || isstring(episodes(i).timestamp)
        % Convert ISO 8601 timestamp to datetime
        dt = datetime(episodes(i).timestamp, 'InputFormat', 'yyyy-MM-dd''T''HH:mm:ss.SSSSSSXXX', 'TimeZone', 'UTC');
        timestamps(i) = posixtime(dt);
    else
        timestamps(i) = episodes(i).timestamp;
    end
end

% Handle both quality_score and quality_scores
quality_scores = zeros(length(episodes), 1);
for i = 1:length(episodes)
    if isfield(episodes, 'quality_score')
        quality_scores(i) = episodes(i).quality_score;
    elseif isfield(episodes, 'quality_scores') && ~isempty(episodes(i).quality_scores)
        quality_scores(i) = mean(episodes(i).quality_scores);
    else
        quality_scores(i) = NaN;
    end
end

% Remove NaN values
valid_idx = ~isnan(quality_scores);
timestamps = timestamps(valid_idx);
quality_scores = quality_scores(valid_idx);

% Convert timestamps to hours since first episode
if ~isempty(timestamps)
    first_time = min(timestamps);
    hours = (timestamps - first_time) / 3600;
else
    hours = [];
end

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
