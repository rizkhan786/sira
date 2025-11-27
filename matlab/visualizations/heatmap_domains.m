function fig = heatmap_domains(heatmap_data)
% HEATMAP_DOMAINS Create heatmap of domain-pattern effectiveness
%
% Visualizes quality scores across domain-pattern combinations
% as a color-coded heatmap.
%
% Inputs:
%   heatmap_data - Structure from pattern_effectiveness()
%       .quality_matrix - Quality scores matrix
%       .domain_labels - Domain names
%       .pattern_labels - Pattern type names
%
% Outputs:
%   fig - Figure handle
%
% Example:
%   [~, hmap] = pattern_effectiveness(episodes);
%   fig = heatmap_domains(hmap);

% Extract data
quality_matrix = heatmap_data.quality_matrix;
domain_labels = heatmap_data.domain_labels;
pattern_labels = heatmap_data.pattern_labels;

% Create figure
fig = figure('Position', [100, 100, 900, 600]);

% Create heatmap
h = heatmap(pattern_labels, domain_labels, quality_matrix);

% Customize appearance
h.Title = 'Pattern Effectiveness by Domain';
h.XLabel = 'Pattern Type';
h.YLabel = 'Domain';
h.Colormap = parula;
h.ColorbarVisible = 'on';
h.MissingDataColor = [0.8 0.8 0.8];
h.MissingDataLabel = 'No Data';
h.GridVisible = 'on';

% Set color limits for better contrast
h.ColorLimits = [0 1];

% Add title with statistics
n_cells = numel(quality_matrix);
n_populated = sum(~isnan(quality_matrix(:)));
coverage_pct = (n_populated / n_cells) * 100;

subtitle_str = sprintf('Coverage: %.1f%% (%d/%d combinations)', ...
                       coverage_pct, n_populated, n_cells);
subtitle(subtitle_str);

end
