function [gaps, recommendations] = gap_analysis(patterns, episodes, min_patterns_threshold)
% GAP_ANALYSIS Identify underserved domains and recommend priorities
%
% Analyzes pattern coverage across domains to identify gaps where
% more patterns are needed. Recommends priority areas for improvement.
%
% Inputs:
%   patterns - Structure array with pattern data
%       .domain - Domain name
%       .quality_score - Pattern quality
%   episodes - Structure array with episode data (optional)
%       .domain - Domain name
%   min_patterns_threshold - Min patterns for coverage (default: 5)
%
% Outputs:
%   gaps - Structure with gap analysis
%       .underserved_domains - Domains with < threshold patterns
%       .domain_coverage - Map of domain -> pattern count
%       .domain_quality - Map of domain -> avg quality
%       .domain_demand - Map of domain -> query count
%   recommendations - Prioritized list of improvement actions
%
% Example:
%   [gaps, recs] = gap_analysis(patterns, episodes, 5);

% Validate inputs
if nargin < 3
    min_patterns_threshold = 5;
end

if isempty(patterns)
    error('Patterns must be provided');
end

fprintf('\n=== Gap Analysis ===\n');
fprintf('Patterns analyzed: %d\n', length(patterns));
fprintf('Min patterns threshold: %d\n', min_patterns_threshold);

% Analyze pattern coverage by domain
all_domains = {patterns.domain};
unique_domains = unique(all_domains);

domain_coverage = containers.Map();
domain_quality = containers.Map();

for i = 1:length(unique_domains)
    domain = unique_domains{i};
    
    % Count patterns in this domain
    domain_patterns = patterns(strcmp({patterns.domain}, domain));
    pattern_count = length(domain_patterns);
    domain_coverage(domain) = pattern_count;
    
    % Calculate average quality
    if pattern_count > 0
        avg_quality = mean([domain_patterns.quality_score]);
        domain_quality(domain) = avg_quality;
    else
        domain_quality(domain) = 0;
    end
end

% Identify underserved domains
underserved = {};
for i = 1:length(unique_domains)
    domain = unique_domains{i};
    if domain_coverage(domain) < min_patterns_threshold
        underserved{end+1} = domain;
    end
end

% Analyze demand (if episodes provided)
domain_demand = containers.Map();
if nargin >= 2 && ~isempty(episodes)
    episode_domains = {episodes.domain};
    for i = 1:length(unique_domains)
        domain = unique_domains{i};
        demand = sum(strcmp(episode_domains, domain));
        domain_demand(domain) = demand;
    end
end

% Package gaps
gaps = struct();
gaps.underserved_domains = underserved;
gaps.domain_coverage = domain_coverage;
gaps.domain_quality = domain_quality;
gaps.domain_demand = domain_demand;
gaps.min_threshold = min_patterns_threshold;

% Generate recommendations
recommendations = generate_recommendations(gaps, unique_domains);

% Display results
fprintf('\nGap Analysis Results:\n');
fprintf('  Total domains: %d\n', length(unique_domains));
fprintf('  Underserved domains: %d\n', length(underserved));
fprintf('  Coverage rate: %.1f%%\n', ...
        ((length(unique_domains) - length(underserved)) / length(unique_domains)) * 100);

if ~isempty(underserved)
    fprintf('\nUnderserved Domains (< %d patterns):\n', min_patterns_threshold);
    for i = 1:min(10, length(underserved))
        domain = underserved{i};
        count = domain_coverage(domain);
        quality = domain_quality(domain);
        
        if ~isempty(domain_demand) && domain_demand.isKey(domain)
            demand = domain_demand(domain);
            fprintf('  - %s: %d patterns, %.3f quality, %d queries\n', ...
                    domain, count, quality, demand);
        else
            fprintf('  - %s: %d patterns, %.3f quality\n', ...
                    domain, count, quality);
        end
    end
    
    if length(underserved) > 10
        fprintf('  ... and %d more\n', length(underserved) - 10);
    end
end

fprintf('\n====================\n\n');

end


function recommendations = generate_recommendations(gaps, all_domains)
% Generate prioritized recommendations based on gap analysis

recommendations = {};

% Priority 1: High demand, low coverage
if ~isempty(gaps.domain_demand)
    priority_domains = {};
    for i = 1:length(gaps.underserved_domains)
        domain = gaps.underserved_domains{i};
        if gaps.domain_demand.isKey(domain)
            demand = gaps.domain_demand(domain);
            if demand > 10  % Significant demand
                priority_domains{end+1} = domain;
            end
        end
    end
    
    if ~isempty(priority_domains)
        rec = struct();
        rec.priority = 'HIGH';
        rec.action = 'Add patterns to high-demand underserved domains';
        rec.domains = priority_domains;
        rec.rationale = sprintf('%d domains with high query volume need more patterns', ...
                                length(priority_domains));
        recommendations{end+1} = rec;
    end
end

% Priority 2: Zero or very low coverage
zero_coverage = {};
for i = 1:length(gaps.underserved_domains)
    domain = gaps.underserved_domains{i};
    if gaps.domain_coverage(domain) <= 1
        zero_coverage{end+1} = domain;
    end
end

if ~isempty(zero_coverage)
    rec = struct();
    rec.priority = 'HIGH';
    rec.action = 'Create initial patterns for uncovered domains';
    rec.domains = zero_coverage;
    rec.rationale = sprintf('%d domains have minimal/no pattern coverage', ...
                            length(zero_coverage));
    recommendations{end+1} = rec;
end

% Priority 3: Low quality patterns
low_quality_domains = {};
for i = 1:length(all_domains)
    domain = all_domains{i};
    if gaps.domain_quality.isKey(domain)
        quality = gaps.domain_quality(domain);
        if quality < 0.6 && gaps.domain_coverage(domain) >= gaps.min_threshold
            low_quality_domains{end+1} = domain;
        end
    end
end

if ~isempty(low_quality_domains)
    rec = struct();
    rec.priority = 'MEDIUM';
    rec.action = 'Improve pattern quality in low-performing domains';
    rec.domains = low_quality_domains;
    rec.rationale = sprintf('%d domains have patterns with quality < 0.6', ...
                            length(low_quality_domains));
    recommendations{end+1} = rec;
end

% Priority 4: General coverage improvement
if length(gaps.underserved_domains) > length(zero_coverage)
    rec = struct();
    rec.priority = 'LOW';
    rec.action = 'Increase pattern diversity in underserved domains';
    rec.domains = setdiff(gaps.underserved_domains, zero_coverage);
    rec.rationale = 'Additional patterns would improve coverage';
    recommendations{end+1} = rec;
end

% Display recommendations
fprintf('Recommendations:\n');
for i = 1:length(recommendations)
    rec = recommendations{i};
    fprintf('  %d. [%s] %s\n', i, rec.priority, rec.action);
    fprintf('     Domains: %d affected\n', length(rec.domains));
    fprintf('     Rationale: %s\n', rec.rationale);
    if length(rec.domains) <= 5
        fprintf('     Specific: %s\n', strjoin(rec.domains, ', '));
    end
    fprintf('\n');
end

end
