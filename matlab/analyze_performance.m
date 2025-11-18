% analyze_performance.m
% Analyze SIRA performance from episode logs
%
% Usage:
%   analyze_performance()
%   analyze_performance('path/to/episodes.mat')

function results = analyze_performance(filepath)
    % Load episodes
    if nargin < 1
        data = load_episodes();
    else
        data = load_episodes(filepath);
    end
    
    if ~isfield(data, 'episodes') || isempty(data.episodes)
        error('No episodes found in data');
    end
    
    episodes = data.episodes;
    n_episodes = length(episodes);
    
    fprintf('\n=== SIRA Performance Analysis ===\n\n');
    
    % Extract metrics
    quality_scores = zeros(n_episodes, 1);
    iteration_counts = zeros(n_episodes, 1);
    patterns_retrieved = zeros(n_episodes, 1);
    processing_times = zeros(n_episodes, 1);
    
    for i = 1:n_episodes
        ep = episodes{i};
        
        % Get final quality score
        if isfield(ep, 'quality_scores') && ~isempty(ep.quality_scores)
            quality_scores(i) = ep.quality_scores(end);
        end
        
        % Get iteration count
        if isfield(ep, 'iteration_count')
            iteration_counts(i) = ep.iteration_count;
        end
        
        % Get patterns retrieved
        if isfield(ep, 'patterns_retrieved')
            patterns_retrieved(i) = ep.patterns_retrieved;
        end
        
        % Get processing time
        if isfield(ep, 'timing_ms') && isfield(ep.timing_ms, 'total')
            processing_times(i) = ep.timing_ms.total;
        end
    end
    
    % Calculate statistics
    fprintf('Quality Metrics:\n');
    fprintf('  Mean quality: %.3f\n', mean(quality_scores));
    fprintf('  Std quality: %.3f\n', std(quality_scores));
    fprintf('  Min quality: %.3f\n', min(quality_scores));
    fprintf('  Max quality: %.3f\n', max(quality_scores));
    
    fprintf('\nIteration Metrics:\n');
    fprintf('  Mean iterations: %.2f\n', mean(iteration_counts));
    fprintf('  Refinement rate: %.1f%%\n', sum(iteration_counts > 1) / n_episodes * 100);
    
    fprintf('\nPattern Usage:\n');
    fprintf('  Mean patterns per query: %.2f\n', mean(patterns_retrieved));
    fprintf('  Pattern usage rate: %.1f%%\n', sum(patterns_retrieved > 0) / n_episodes * 100);
    
    fprintf('\nPerformance:\n');
    fprintf('  Mean processing time: %.0f ms\n', mean(processing_times));
    fprintf('  Std processing time: %.0f ms\n', std(processing_times));
    
    % Create visualizations
    figure('Name', 'SIRA Performance Analysis');
    
    % Quality over time
    subplot(2, 2, 1);
    plot(quality_scores, 'b-', 'LineWidth', 1.5);
    hold on;
    plot(smooth(quality_scores, 5), 'r-', 'LineWidth', 2);
    xlabel('Episode');
    ylabel('Quality Score');
    title('Quality Score Progression');
    legend('Raw', 'Smoothed (5-point)');
    grid on;
    
    % Quality distribution
    subplot(2, 2, 2);
    histogram(quality_scores, 20);
    xlabel('Quality Score');
    ylabel('Frequency');
    title('Quality Score Distribution');
    grid on;
    
    % Iteration counts
    subplot(2, 2, 3);
    histogram(iteration_counts, 'BinEdges', 0.5:1:max(iteration_counts)+0.5);
    xlabel('Iteration Count');
    ylabel('Frequency');
    title('Refinement Iterations');
    grid on;
    
    % Processing time vs quality
    subplot(2, 2, 4);
    scatter(processing_times / 1000, quality_scores, 50, 'filled');
    xlabel('Processing Time (s)');
    ylabel('Quality Score');
    title('Processing Time vs Quality');
    grid on;
    
    % Return results
    results = struct();
    results.mean_quality = mean(quality_scores);
    results.std_quality = std(quality_scores);
    results.mean_iterations = mean(iteration_counts);
    results.refinement_rate = sum(iteration_counts > 1) / n_episodes;
    results.pattern_usage_rate = sum(patterns_retrieved > 0) / n_episodes;
    results.mean_time_ms = mean(processing_times);
    
    fprintf('\nAnalysis complete.\n');
end
