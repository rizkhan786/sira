function optimize_patterns(patterns_file, episodes_file, output_file)
% OPTIMIZE_PATTERNS Pattern library optimization engine
%
% Performs comprehensive pattern library optimization including:
% 1. Pattern clustering to identify duplicates
% 2. Library distillation to reduce size
% 3. Gap analysis to identify improvement areas
%
% Inputs:
%   patterns_file - Path to patterns.mat file with pattern data
%   episodes_file - Path to episodes.mat file (optional for gap analysis)
%   output_file - Path to save optimized patterns (optional)
%
% Outputs:
%   Optimized pattern library saved to output_file
%   Console report with all optimization metrics
%
% Example:
%   optimize_patterns('patterns.mat', 'episodes.mat', 'optimized_patterns.mat');
%
% Requirements:
%   - MATLAB R2020a or later
%   - Statistics and Machine Learning Toolbox
%
% Author: SIRA Team
% Date: 2025-11-27

% Set defaults
if nargin < 1 || isempty(patterns_file)
    patterns_file = fullfile('data', 'matlab', 'patterns.mat');
end

if nargin < 2
    episodes_file = '';
end

if nargin < 3 || isempty(output_file)
    output_file = fullfile('data', 'matlab', 'patterns_optimized.mat');
end

fprintf('\n========================================\n');
fprintf('SIRA Pattern Optimization Engine\n');
fprintf('========================================\n\n');

%% 1. Load Pattern Data
fprintf('Loading patterns from: %s\n', patterns_file);
try
    data = load(patterns_file);
    if isfield(data, 'patterns')
        patterns = data.patterns;
    else
        % Assume the file contains the patterns directly
        patterns = data;
    end
    fprintf('✓ Loaded %d patterns\n\n', length(patterns));
catch ME
    error('Failed to load patterns: %s', ME.message);
end

% Load episodes if provided
episodes = [];
if ~isempty(episodes_file) && exist(episodes_file, 'file')
    fprintf('Loading episodes from: %s\n', episodes_file);
    try
        episodes = load_episodes(episodes_file);
        fprintf('✓ Loaded %d episodes\n\n', length(episodes));
    catch ME
        warning('Failed to load episodes: %s', ME.message);
    end
end

%% 2. Pattern Clustering
fprintf('Running pattern clustering...\n');
addpath('optimization');
[clusters, cluster_stats] = cluster_patterns(patterns, 0.9);

%% 3. Library Distillation
fprintf('Distilling pattern library...\n');
[optimized_patterns, distill_stats] = distill_library(patterns, clusters, 20);

%% 4. Gap Analysis
fprintf('Performing gap analysis...\n');
[gaps, recommendations] = gap_analysis(patterns, episodes, 5);

%% 5. Save Optimized Patterns
fprintf('Saving optimized patterns to: %s\n', output_file);
try
    save(output_file, 'optimized_patterns');
    fprintf('✓ Saved optimized pattern library\n\n');
catch ME
    warning('Failed to save optimized patterns: %s', ME.message);
end

%% 6. Generate Summary Report
fprintf('========================================\n');
fprintf('OPTIMIZATION SUMMARY\n');
fprintf('========================================\n\n');

fprintf('CLUSTERING:\n');
fprintf('  Total clusters: %d\n', cluster_stats.num_clusters);
fprintf('  Duplicate groups: %d\n', cluster_stats.num_duplicates);
fprintf('  Consolidation potential: %.1f%%\n\n', cluster_stats.consolidation_potential);

fprintf('DISTILLATION:\n');
fprintf('  Original patterns: %d\n', distill_stats.original_count);
fprintf('  Optimized patterns: %d\n', distill_stats.optimized_count);
fprintf('  Size reduction: %.1f%%\n', distill_stats.reduction_pct);
fprintf('  Quality change: %+.2f%%\n', distill_stats.quality_degradation);

if distill_stats.target_met && distill_stats.quality_maintained
    fprintf('  Status: ✓ All targets met\n\n');
elseif distill_stats.target_met
    fprintf('  Status: ⚠ Size target met, quality degraded\n\n');
elseif distill_stats.quality_maintained
    fprintf('  Status: ⚠ Quality maintained, size target not met\n\n');
else
    fprintf('  Status: ✗ Targets not met\n\n');
end

fprintf('GAP ANALYSIS:\n');
fprintf('  Total domains: %d\n', length(gaps.domain_coverage));
fprintf('  Underserved domains: %d\n', length(gaps.underserved_domains));
fprintf('  Coverage rate: %.1f%%\n', ...
        ((length(gaps.domain_coverage) - length(gaps.underserved_domains)) / ...
         length(gaps.domain_coverage)) * 100);
fprintf('  Priority recommendations: %d\n\n', length(recommendations));

fprintf('TOP RECOMMENDATIONS:\n');
for i = 1:min(3, length(recommendations))
    rec = recommendations{i};
    fprintf('  %d. [%s] %s\n', i, rec.priority, rec.action);
    fprintf('     %s\n', rec.rationale);
end

fprintf('\n========================================\n');
fprintf('Optimization complete!\n');
fprintf('========================================\n\n');

% Return summary struct if output argument requested
if nargout > 0
    summary = struct();
    summary.cluster_stats = cluster_stats;
    summary.distill_stats = distill_stats;
    summary.gaps = gaps;
    summary.recommendations = recommendations;
end

end
