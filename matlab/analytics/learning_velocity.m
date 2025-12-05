function [velocity, stats] = learning_velocity(episodes)
% LEARNING_VELOCITY Compute quality improvement rate over time
%
% Calculates the learning velocity of SIRA by measuring the rate of
% quality improvement across episodes. Uses linear regression to fit
% a trend line to quality scores over time.
%
% Inputs:
%   episodes - Structure array with episode data
%       .timestamp - Episode timestamp
%       .quality_score - Quality score (0-1)
%
% Outputs:
%   velocity - Learning velocity (quality units per hour)
%   stats - Structure with detailed statistics
%       .slope - Regression slope (quality/hour)
%       .intercept - Y-intercept
%       .r_squared - R² goodness of fit
%       .improvement_pct - Percentage improvement
%       .avg_quality_early - Average quality first 10%
%       .avg_quality_late - Average quality last 10%
%       .num_episodes - Total episodes analyzed
%
% Example:
%   episodes = load_episodes('data/matlab/episodes.mat');
%   [vel, stats] = learning_velocity(episodes);
%   fprintf('Learning velocity: %.4f quality/hour\n', vel);

% Validate input
if isempty(episodes)
    error('No episodes provided');
end

if ~isfield(episodes, 'timestamp')
    error('Episodes must have timestamp field');
end

% Handle both quality_score (singular) and quality_scores (plural/array)
if ~isfield(episodes, 'quality_score') && ~isfield(episodes, 'quality_scores')
    error('Episodes must have quality_score or quality_scores field');
end

% Extract timestamps and quality scores
timestamps = [episodes.timestamp]';

% Extract quality scores - handle both formats
if isfield(episodes, 'quality_score')
    quality_scores = [episodes.quality_score]';
else
    % quality_scores is an array - take the mean
    quality_scores = zeros(length(episodes), 1);
    for i = 1:length(episodes)
        if ~isempty(episodes(i).quality_scores)
            quality_scores(i) = mean(episodes(i).quality_scores);
        else
            quality_scores(i) = NaN;
        end
    end
end

% Convert timestamps to hours since first episode
first_time = min(timestamps);
hours_elapsed = (timestamps - first_time) / 3600; % seconds to hours

% Remove invalid quality scores
valid_idx = ~isnan(quality_scores) & quality_scores >= 0 & quality_scores <= 1;
hours_clean = hours_elapsed(valid_idx);
quality_clean = quality_scores(valid_idx);

if length(quality_clean) < 2
    warning('Insufficient valid data points for regression');
    velocity = 0;
    stats = struct();
    return;
end

% Linear regression: quality = slope * hours + intercept
n = length(quality_clean);
mean_hours = mean(hours_clean);
mean_quality = mean(quality_clean);

numerator = sum((hours_clean - mean_hours) .* (quality_clean - mean_quality));
denominator = sum((hours_clean - mean_hours).^2);

if denominator == 0
    slope = 0;
else
    slope = numerator / denominator;
end

intercept = mean_quality - slope * mean_hours;

% Calculate R²
quality_pred = slope * hours_clean + intercept;
ss_res = sum((quality_clean - quality_pred).^2);
ss_tot = sum((quality_clean - mean_quality).^2);

if ss_tot == 0
    r_squared = 0;
else
    r_squared = 1 - (ss_res / ss_tot);
end

% Calculate average quality for early and late periods
n_episodes = length(quality_clean);
n_early = max(1, floor(n_episodes * 0.1));
n_late = max(1, floor(n_episodes * 0.1));

avg_quality_early = mean(quality_clean(1:n_early));
avg_quality_late = mean(quality_clean(end-n_late+1:end));

% Calculate improvement percentage
if avg_quality_early > 0
    improvement_pct = ((avg_quality_late - avg_quality_early) / avg_quality_early) * 100;
else
    improvement_pct = 0;
end

% Return velocity (slope in quality/hour)
velocity = slope;

% Package statistics
stats = struct();
stats.slope = slope;
stats.intercept = intercept;
stats.r_squared = r_squared;
stats.improvement_pct = improvement_pct;
stats.avg_quality_early = avg_quality_early;
stats.avg_quality_late = avg_quality_late;
stats.num_episodes = n_episodes;
stats.time_span_hours = max(hours_clean) - min(hours_clean);
stats.avg_quality_overall = mean_quality;

% Display summary
fprintf('\n=== Learning Velocity Analysis ===\n');
fprintf('Episodes analyzed: %d\n', n_episodes);
fprintf('Time span: %.2f hours\n', stats.time_span_hours);
fprintf('Learning velocity: %.6f quality/hour\n', velocity);
fprintf('R² (fit quality): %.4f\n', r_squared);
fprintf('Avg quality (early 10%%): %.4f\n', avg_quality_early);
fprintf('Avg quality (late 10%%): %.4f\n', avg_quality_late);
fprintf('Improvement: %.2f%%\n', improvement_pct);
fprintf('==================================\n\n');

end
