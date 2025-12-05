function [clusters, stats] = cluster_patterns(patterns, similarity_threshold)
% CLUSTER_PATTERNS Identify and group similar patterns using clustering
%
% Uses cosine similarity and K-means clustering to identify duplicate
% or near-duplicate patterns that can be consolidated.
%
% Inputs:
%   patterns - Structure array with pattern data
%       .embedding - Pattern embedding vector
%       .pattern_id - Unique pattern ID
%       .quality_score - Pattern quality
%       .usage_count - Times pattern was used
%   similarity_threshold - Min similarity for grouping (default: 0.9)
%
% Outputs:
%   clusters - Cell array of pattern clusters
%       Each cell contains indices of similar patterns
%   stats - Structure with clustering statistics
%       .num_clusters - Number of clusters found
%       .num_singletons - Clusters with only 1 pattern
%       .num_duplicates - Clusters with 2+ patterns
%       .largest_cluster_size - Size of largest cluster
%       .consolidation_potential - % patterns that can be merged
%
% Example:
%   [clusters, stats] = cluster_patterns(patterns, 0.9);

% Validate inputs
if nargin < 2
    similarity_threshold = 0.9;
end

if isempty(patterns) || ~isfield(patterns, 'embedding')
    error('Patterns must have embedding field');
end

fprintf('\n=== Pattern Clustering ===\n');
fprintf('Patterns to analyze: %d\n', length(patterns));
fprintf('Similarity threshold: %.2f\n', similarity_threshold);

% Extract embeddings into matrix
n_patterns = length(patterns);
embedding_dim = length(patterns(1).embedding);
embedding_matrix = zeros(n_patterns, embedding_dim);

for i = 1:n_patterns
    embedding_matrix(i, :) = patterns(i).embedding;
end

% Normalize embeddings for cosine similarity
embedding_norms = sqrt(sum(embedding_matrix.^2, 2));
embedding_normalized = embedding_matrix ./ embedding_norms;

% Compute pairwise cosine similarity matrix
similarity_matrix = embedding_normalized * embedding_normalized';

% Find patterns above similarity threshold
clusters = {};
assigned = false(n_patterns, 1);

for i = 1:n_patterns
    if assigned(i)
        continue;
    end
    
    % Find all patterns similar to pattern i
    similar_idx = find(similarity_matrix(i, :) >= similarity_threshold);
    
    % Create cluster
    clusters{end+1} = similar_idx;
    assigned(similar_idx) = true;
end

% Calculate statistics
num_clusters = length(clusters);
cluster_sizes = cellfun(@length, clusters);
num_singletons = sum(cluster_sizes == 1);
num_duplicates = sum(cluster_sizes > 1);
largest_cluster_size = max(cluster_sizes);

% Consolidation potential: patterns that can be merged
patterns_in_duplicates = sum(cluster_sizes(cluster_sizes > 1));
consolidation_potential = (patterns_in_duplicates - num_duplicates) / n_patterns * 100;

% Package statistics
stats = struct();
stats.num_clusters = num_clusters;
stats.num_singletons = num_singletons;
stats.num_duplicates = num_duplicates;
stats.largest_cluster_size = largest_cluster_size;
stats.consolidation_potential = consolidation_potential;
stats.cluster_sizes = cluster_sizes;
stats.similarity_threshold = similarity_threshold;

% Display results
fprintf('\nClustering Results:\n');
fprintf('  Total clusters: %d\n', num_clusters);
fprintf('  Unique patterns: %d\n', num_singletons);
fprintf('  Duplicate groups: %d\n', num_duplicates);
fprintf('  Largest cluster: %d patterns\n', largest_cluster_size);
fprintf('  Consolidation potential: %.1f%%\n', consolidation_potential);

% Show top duplicate clusters
if num_duplicates > 0
    fprintf('\nTop 5 Duplicate Clusters:\n');
    [sorted_sizes, sorted_idx] = sort(cluster_sizes, 'descend');
    
    for i = 1:min(5, num_duplicates)
        cluster_idx = sorted_idx(i);
        if cluster_sizes(cluster_idx) <= 1
            break;
        end
        
        pattern_ids = clusters{cluster_idx};
        fprintf('  Cluster %d: %d patterns\n', i, length(pattern_ids));
        
        % Show pattern details
        for j = 1:min(3, length(pattern_ids))
            p = patterns(pattern_ids(j));
            if isfield(p, 'pattern_id')
                fprintf('    - Pattern %s (quality: %.3f, usage: %d)\n', ...
                        p.pattern_id, p.quality_score, p.usage_count);
            end
        end
        
        if length(pattern_ids) > 3
            fprintf('    ... and %d more\n', length(pattern_ids) - 3);
        end
    end
end

fprintf('==========================\n\n');

end
