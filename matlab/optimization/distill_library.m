function [optimized_patterns, stats] = distill_library(patterns, clusters, target_reduction)
% DISTILL_LIBRARY Reduce pattern library size by consolidating duplicates
%
% Consolidates similar patterns identified by clustering to reduce
% library size by 20%+ while maintaining quality (< 2% degradation).
%
% Inputs:
%   patterns - Structure array with pattern data
%   clusters - Clusters from cluster_patterns()
%   target_reduction - Target reduction % (default: 20)
%
% Outputs:
%   optimized_patterns - Consolidated pattern library
%   stats - Distillation statistics
%       .original_count - Original pattern count
%       .optimized_count - Optimized pattern count
%       .reduction_pct - Actual reduction percentage
%       .avg_quality_before - Average quality before
%       .avg_quality_after - Average quality after
%       .quality_degradation - Quality change percentage
%
% Example:
%   [clusters, ~] = cluster_patterns(patterns);
%   [opt_patterns, stats] = distill_library(patterns, clusters, 20);

% Validate inputs
if nargin < 3
    target_reduction = 20;
end

if isempty(patterns) || isempty(clusters)
    error('Patterns and clusters must be provided');
end

fprintf('\n=== Pattern Library Distillation ===\n');
fprintf('Original patterns: %d\n', length(patterns));
fprintf('Target reduction: %.1f%%\n', target_reduction);

% Calculate original average quality
original_qualities = [patterns.quality_score];
avg_quality_before = mean(original_qualities);

% Initialize optimized pattern list
optimized_patterns = [];

% Process each cluster
for i = 1:length(clusters)
    cluster_idx = clusters{i};
    
    if length(cluster_idx) == 1
        % Singleton cluster - keep as is
        optimized_patterns = [optimized_patterns, patterns(cluster_idx)];
    else
        % Multiple patterns - consolidate by selecting best
        cluster_patterns = patterns(cluster_idx);
        
        % Consolidation strategy: keep pattern with:
        % 1. Highest quality score
        % 2. Highest usage count (if quality tied)
        qualities = [cluster_patterns.quality_score];
        usage_counts = [cluster_patterns.usage_count];
        
        % Weighted score: 70% quality, 30% normalized usage
        max_usage = max(usage_counts);
        if max_usage > 0
            normalized_usage = usage_counts / max_usage;
        else
            normalized_usage = zeros(size(usage_counts));
        end
        
        composite_scores = 0.7 * qualities + 0.3 * normalized_usage;
        
        % Select best pattern
        [~, best_idx] = max(composite_scores);
        best_pattern = cluster_patterns(best_idx);
        
        % Update usage count to reflect consolidated usage
        best_pattern.usage_count = sum(usage_counts);
        
        % Add consolidated pattern IDs for tracking
        if isfield(best_pattern, 'consolidated_from')
            best_pattern.consolidated_from = {cluster_patterns.pattern_id};
        end
        
        optimized_patterns = [optimized_patterns, best_pattern];
    end
end

% Calculate statistics
optimized_count = length(optimized_patterns);
original_count = length(patterns);
reduction_pct = ((original_count - optimized_count) / original_count) * 100;

optimized_qualities = [optimized_patterns.quality_score];
avg_quality_after = mean(optimized_qualities);
quality_degradation = ((avg_quality_after - avg_quality_before) / avg_quality_before) * 100;

% Package statistics
stats = struct();
stats.original_count = original_count;
stats.optimized_count = optimized_count;
stats.patterns_removed = original_count - optimized_count;
stats.reduction_pct = reduction_pct;
stats.avg_quality_before = avg_quality_before;
stats.avg_quality_after = avg_quality_after;
stats.quality_degradation = quality_degradation;
stats.quality_maintained = abs(quality_degradation) < 2.0;
stats.target_met = reduction_pct >= target_reduction;

% Display results
fprintf('\nDistillation Results:\n');
fprintf('  Original patterns: %d\n', original_count);
fprintf('  Optimized patterns: %d\n', optimized_count);
fprintf('  Patterns removed: %d\n', stats.patterns_removed);
fprintf('  Reduction: %.1f%%\n', reduction_pct);
fprintf('\nQuality Impact:\n');
fprintf('  Avg quality before: %.4f\n', avg_quality_before);
fprintf('  Avg quality after: %.4f\n', avg_quality_after);
fprintf('  Quality change: %+.2f%%\n', quality_degradation);

% Status indicators
if stats.target_met
    fprintf('  ✓ Target reduction achieved\n');
else
    fprintf('  ✗ Target reduction not met (%.1f%% vs %.1f%%)\n', ...
            reduction_pct, target_reduction);
end

if stats.quality_maintained
    fprintf('  ✓ Quality maintained (< 2%% degradation)\n');
else
    fprintf('  ✗ Quality degraded by %.2f%%\n', abs(quality_degradation));
end

fprintf('====================================\n\n');

end
