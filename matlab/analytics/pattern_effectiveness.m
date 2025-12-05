function [effectiveness, heatmap_data] = pattern_effectiveness(episodes)
% PATTERN_EFFECTIVENESS Analyze quality improvement by domain and pattern type
%
% Calculates how effective different pattern types are across domains
% by measuring average quality scores and improvement rates.
%
% Inputs:
%   episodes - Structure array with episode data
%       .domain - Domain name (string)
%       .patterns_used - Cell array of pattern types
%       .quality_score - Quality score (0-1)
%
% Outputs:
%   effectiveness - Structure with effectiveness metrics
%       .by_domain - Map of domain -> avg quality
%       .by_pattern - Map of pattern -> avg quality
%       .best_combinations - Top domain-pattern combinations
%   heatmap_data - Matrix for heatmap visualization
%       .quality_matrix - Domains x Patterns quality matrix
%       .domain_labels - Domain names
%       .pattern_labels - Pattern type names
%
% Example:
%   [eff, hmap] = pattern_effectiveness(episodes);

% Validate input
if isempty(episodes)
    error('No episodes provided');
end

% Extract unique domains and pattern types
% Handle missing domain field gracefully
all_domains = cell(1, length(episodes));
for i = 1:length(episodes)
    if isfield(episodes, 'domain') && ~isempty(episodes(i).domain)
        all_domains{i} = episodes(i).domain;
    else
        all_domains{i} = 'unknown';
    end
end

all_patterns = {};
for i = 1:length(episodes)
    if isfield(episodes(i), 'patterns_used') && ~isempty(episodes(i).patterns_used)
        all_patterns = [all_patterns, episodes(i).patterns_used];
    elseif isfield(episodes(i), 'pattern_ids') && ~isempty(episodes(i).pattern_ids)
        % Use pattern_ids if patterns_used not available
        all_patterns = [all_patterns, episodes(i).pattern_ids];
    end
end

unique_domains = unique(all_domains);
unique_patterns = unique(all_patterns);

% Initialize quality matrix
n_domains = length(unique_domains);
n_patterns = length(unique_patterns);
quality_matrix = nan(n_domains, n_patterns);
count_matrix = zeros(n_domains, n_patterns);

% Fill quality matrix
for i = 1:length(episodes)
    domain = all_domains{i};
    
    % Handle both quality_score and quality_scores
    if isfield(episodes, 'quality_score')
        quality = episodes(i).quality_score;
    elseif isfield(episodes, 'quality_scores') && ~isempty(episodes(i).quality_scores)
        quality = mean(episodes(i).quality_scores);
    else
        quality = NaN;
    end
    
    domain_idx = find(strcmp(unique_domains, domain));
    
    if isfield(episodes(i), 'patterns_used') && ~isempty(episodes(i).patterns_used)
        patterns = episodes(i).patterns_used;
        for j = 1:length(patterns)
            pattern_idx = find(strcmp(unique_patterns, patterns{j}));
            if ~isempty(pattern_idx)
                if isnan(quality_matrix(domain_idx, pattern_idx))
                    quality_matrix(domain_idx, pattern_idx) = quality;
                    count_matrix(domain_idx, pattern_idx) = 1;
                else
                    % Running average
                    n = count_matrix(domain_idx, pattern_idx);
                    quality_matrix(domain_idx, pattern_idx) = ...
                        (quality_matrix(domain_idx, pattern_idx) * n + quality) / (n + 1);
                    count_matrix(domain_idx, pattern_idx) = n + 1;
                end
            end
        end
    end
end

% Calculate by-domain effectiveness
by_domain = containers.Map();
for i = 1:n_domains
    domain = unique_domains{i};
    domain_quality = quality_matrix(i, ~isnan(quality_matrix(i,:)));
    if ~isempty(domain_quality)
        by_domain(domain) = mean(domain_quality);
    else
        by_domain(domain) = 0;
    end
end

% Calculate by-pattern effectiveness
by_pattern = containers.Map();
for j = 1:n_patterns
    pattern = unique_patterns{j};
    pattern_quality = quality_matrix(~isnan(quality_matrix(:,j)), j);
    if ~isempty(pattern_quality)
        by_pattern(pattern) = mean(pattern_quality);
    else
        by_pattern(pattern) = 0;
    end
end

% Find best combinations
combinations = [];
for i = 1:n_domains
    for j = 1:n_patterns
        if ~isnan(quality_matrix(i,j))
            combinations(end+1).domain = unique_domains{i};
            combinations(end).pattern = unique_patterns{j};
            combinations(end).quality = quality_matrix(i,j);
            combinations(end).count = count_matrix(i,j);
        end
    end
end

% Sort by quality (descending)
if ~isempty(combinations)
    [~, sorted_idx] = sort([combinations.quality], 'descend');
    best_combinations = combinations(sorted_idx);
else
    best_combinations = [];
end

% Package results
effectiveness = struct();
effectiveness.by_domain = by_domain;
effectiveness.by_pattern = by_pattern;
effectiveness.best_combinations = best_combinations;

heatmap_data = struct();
heatmap_data.quality_matrix = quality_matrix;
heatmap_data.count_matrix = count_matrix;
heatmap_data.domain_labels = unique_domains;
heatmap_data.pattern_labels = unique_patterns;

% Display summary
fprintf('\n=== Pattern Effectiveness Analysis ===\n');
fprintf('Domains analyzed: %d\n', n_domains);
fprintf('Pattern types: %d\n', n_patterns);
fprintf('\nTop 5 Domain-Pattern Combinations:\n');
for i = 1:min(5, length(best_combinations))
    fprintf('  %d. %s + %s: %.4f (n=%d)\n', i, ...
        best_combinations(i).domain, ...
        best_combinations(i).pattern, ...
        best_combinations(i).quality, ...
        best_combinations(i).count);
end
fprintf('======================================\n\n');

end
