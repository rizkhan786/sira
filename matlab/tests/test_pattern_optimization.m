% TEST_PATTERN_OPTIMIZATION Test cases for DEL-032
%
% Tests for AC-073, AC-074, AC-075:
%   AC-073: Pattern clustering identifies similar patterns (cosine similarity > 0.9)
%   AC-074: Pattern distillation reduces library by 20%+ without >2% quality loss
%   AC-075: Gap analysis identifies underserved domains (< 5 patterns)
%
% Author: SIRA Team
% Date: 2025-11-27

function test_pattern_optimization()
    fprintf('\n========================================\n');
    fprintf('TEST: MATLAB Pattern Optimization Engine\n');
    fprintf('========================================\n\n');
    
    % Track test results
    results = struct();
    results.total = 0;
    results.passed = 0;
    results.failed = 0;
    
    %% Setup test data
    fprintf('Setting up test data...\n');
    [patterns, episodes] = setup_test_data();
    fprintf('✓ Created %d test patterns and %d test episodes\n\n', ...
            length(patterns), length(episodes));
    
    %% Test AC-073: Pattern Clustering
    fprintf('Testing AC-073: Pattern clustering...\n');
    try
        addpath('optimization');
        [clusters, cluster_stats] = cluster_patterns(patterns, 0.9);
        
        % Verify clustering works
        assert(~isempty(clusters), 'Clusters should not be empty');
        assert(cluster_stats.num_clusters >= 0, 'Cluster count must be non-negative');
        assert(cluster_stats.consolidation_potential >= 0, 'Consolidation potential must be >= 0');
        
        % Verify we found expected duplicate groups (patterns 2 and 3 are duplicates)
        assert(cluster_stats.num_duplicates >= 1, 'Should find at least 1 duplicate group');
        
        fprintf('✓ AC-073 PASSED: Found %d clusters, %d duplicate groups\n', ...
                cluster_stats.num_clusters, cluster_stats.num_duplicates);
        results.passed = results.passed + 1;
    catch ME
        fprintf('✗ AC-073 FAILED: %s\n', ME.message);
        results.failed = results.failed + 1;
    end
    results.total = results.total + 1;
    fprintf('\n');
    
    %% Test AC-074: Pattern Distillation
    fprintf('Testing AC-074: Pattern distillation...\n');
    try
        [optimized_patterns, distill_stats] = distill_library(patterns, clusters, 20);
        
        % Verify distillation reduces size
        assert(distill_stats.optimized_count < distill_stats.original_count, ...
               'Optimized count should be less than original');
        
        % Check if reduction target was met
        if distill_stats.target_met
            fprintf('  ✓ Size reduction target met: %.1f%% (target: 20%%)\n', ...
                    distill_stats.reduction_pct);
        else
            fprintf('  ⚠ Size reduction target not met: %.1f%% (target: 20%%)\n', ...
                    distill_stats.reduction_pct);
        end
        
        % Verify quality maintained (< 2% degradation)
        assert(distill_stats.quality_degradation < 2.0, ...
               sprintf('Quality degradation %.2f%% exceeds 2%% threshold', ...
                       distill_stats.quality_degradation));
        fprintf('  ✓ Quality maintained: %.2f%% degradation (threshold: 2%%)\n', ...
                distill_stats.quality_degradation);
        
        % Verify targets met
        assert(distill_stats.target_met, 'Size reduction target should be met');
        assert(distill_stats.quality_maintained, 'Quality should be maintained');
        
        fprintf('✓ AC-074 PASSED: Reduced %d → %d patterns (%.1f%%), quality: %+.2f%%\n', ...
                distill_stats.original_count, distill_stats.optimized_count, ...
                distill_stats.reduction_pct, distill_stats.quality_degradation);
        results.passed = results.passed + 1;
    catch ME
        fprintf('✗ AC-074 FAILED: %s\n', ME.message);
        results.failed = results.failed + 1;
    end
    results.total = results.total + 1;
    fprintf('\n');
    
    %% Test AC-075: Gap Analysis
    fprintf('Testing AC-075: Gap analysis...\n');
    try
        [gaps, recommendations] = gap_analysis(patterns, episodes, 5);
        
        % Verify gap analysis identifies underserved domains
        assert(~isempty(gaps.underserved_domains), ...
               'Should identify underserved domains');
        
        % Verify domain coverage stats
        assert(isfield(gaps, 'domain_coverage'), 'Should have domain_coverage');
        assert(isfield(gaps, 'domain_quality'), 'Should have domain_quality');
        assert(isfield(gaps, 'domain_demand'), 'Should have domain_demand');
        
        % Verify recommendations generated
        assert(~isempty(recommendations), 'Should generate recommendations');
        
        % Check that recommendations have required fields
        for i = 1:length(recommendations)
            rec = recommendations{i};
            assert(isfield(rec, 'priority'), 'Recommendation should have priority');
            assert(isfield(rec, 'action'), 'Recommendation should have action');
            assert(isfield(rec, 'rationale'), 'Recommendation should have rationale');
            
            % Verify priority is valid
            valid_priorities = {'HIGH', 'MEDIUM', 'LOW'};
            assert(ismember(rec.priority, valid_priorities), ...
                   'Priority must be HIGH, MEDIUM, or LOW');
        end
        
        fprintf('  ✓ Identified %d underserved domains\n', length(gaps.underserved_domains));
        fprintf('  ✓ Generated %d recommendations\n', length(recommendations));
        
        fprintf('✓ AC-075 PASSED: Gap analysis complete\n');
        results.passed = results.passed + 1;
    catch ME
        fprintf('✗ AC-075 FAILED: %s\n', ME.message);
        results.failed = results.failed + 1;
    end
    results.total = results.total + 1;
    fprintf('\n');
    
    %% Test Integration: Full Optimization Pipeline
    fprintf('Testing integration: Full optimization pipeline...\n');
    try
        % Save test data
        test_patterns_file = 'test_patterns.mat';
        test_episodes_file = 'test_episodes.mat';
        test_output_file = 'test_optimized.mat';
        
        save(test_patterns_file, 'patterns');
        save(test_episodes_file, 'episodes');
        
        % Run full optimization
        optimize_patterns(test_patterns_file, test_episodes_file, test_output_file);
        
        % Verify output file created
        assert(exist(test_output_file, 'file') > 0, 'Output file should be created');
        
        % Load and verify optimized patterns
        opt_data = load(test_output_file);
        assert(isfield(opt_data, 'optimized_patterns'), ...
               'Output should contain optimized_patterns');
        
        fprintf('✓ INTEGRATION PASSED: Full pipeline executed successfully\n');
        results.passed = results.passed + 1;
        
        % Cleanup
        delete(test_patterns_file);
        delete(test_episodes_file);
        delete(test_output_file);
    catch ME
        fprintf('✗ INTEGRATION FAILED: %s\n', ME.message);
        results.failed = results.failed + 1;
    end
    results.total = results.total + 1;
    fprintf('\n');
    
    %% Print Summary
    fprintf('========================================\n');
    fprintf('TEST SUMMARY\n');
    fprintf('========================================\n');
    fprintf('Total:  %d\n', results.total);
    fprintf('Passed: %d (%.1f%%)\n', results.passed, ...
            (results.passed / results.total) * 100);
    fprintf('Failed: %d (%.1f%%)\n', results.failed, ...
            (results.failed / results.total) * 100);
    fprintf('========================================\n\n');
    
    if results.failed == 0
        fprintf('✓ ALL TESTS PASSED\n\n');
    else
        fprintf('✗ SOME TESTS FAILED\n\n');
        error('Test suite failed');
    end
end

function [patterns, episodes] = setup_test_data()
    % Create test patterns with embeddings and usage data
    patterns = struct([]);
    
    % Pattern 1: Math pattern, high quality
    patterns(1).id = 'pat-001';
    patterns(1).name = 'mathematical-analysis';
    patterns(1).domain = 'math';
    patterns(1).content = 'Analyze problem mathematically';
    patterns(1).embedding = randn(768, 1);  % Random embedding
    patterns(1).quality = 0.85;
    patterns(1).usage_count = 25;
    
    % Pattern 2: Similar to pattern 1 (should be clustered together)
    patterns(2).id = 'pat-002';
    patterns(2).name = 'math-reasoning';
    patterns(2).domain = 'math';
    patterns(2).content = 'Use mathematical reasoning';
    patterns(2).embedding = patterns(1).embedding + 0.01 * randn(768, 1);  % Very similar
    patterns(2).quality = 0.83;
    patterns(2).usage_count = 20;
    
    % Pattern 3: Another similar to pattern 1
    patterns(3).id = 'pat-003';
    patterns(3).name = 'quantitative-analysis';
    patterns(3).domain = 'math';
    patterns(3).content = 'Apply quantitative analysis';
    patterns(3).embedding = patterns(1).embedding + 0.02 * randn(768, 1);  % Very similar
    patterns(3).quality = 0.80;
    patterns(3).usage_count = 15;
    
    % Pattern 4: Science pattern, different embedding
    patterns(4).id = 'pat-004';
    patterns(4).name = 'scientific-method';
    patterns(4).domain = 'science';
    patterns(4).content = 'Apply scientific method';
    patterns(4).embedding = randn(768, 1);  % Different embedding
    patterns(4).quality = 0.78;
    patterns(4).usage_count = 10;
    
    % Pattern 5: History pattern, different embedding
    patterns(5).id = 'pat-005';
    patterns(5).name = 'historical-context';
    patterns(5).domain = 'history';
    patterns(5).content = 'Consider historical context';
    patterns(5).embedding = randn(768, 1);  % Different embedding
    patterns(5).quality = 0.75;
    patterns(5).usage_count = 8;
    
    % Normalize embeddings for cosine similarity
    for i = 1:length(patterns)
        patterns(i).embedding = patterns(i).embedding / norm(patterns(i).embedding);
    end
    
    % Create test episodes with domain distribution
    episodes = struct([]);
    
    % Math-heavy episodes
    for i = 1:3
        episodes(i).id = sprintf('ep-%03d', i);
        episodes(i).domain = 'math';
        episodes(i).quality = 0.8 + 0.05 * rand();
        episodes(i).patterns_used = {patterns(1).id, patterns(2).id};
    end
    
    % Science episodes
    for i = 4:5
        episodes(i).id = sprintf('ep-%03d', i);
        episodes(i).domain = 'science';
        episodes(i).quality = 0.75 + 0.05 * rand();
        episodes(i).patterns_used = {patterns(4).id};
    end
    
    % Geography episodes (underserved - no patterns available)
    for i = 6:8
        episodes(i).id = sprintf('ep-%03d', i);
        episodes(i).domain = 'geography';
        episodes(i).quality = 0.65 + 0.05 * rand();
        episodes(i).patterns_used = {};  % No patterns available
    end
end
