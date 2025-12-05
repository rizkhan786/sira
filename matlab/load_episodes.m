% load_episodes.m
% Load SIRA episode logs from .mat file
%
% Usage:
%   data = load_episodes()
%   data = load_episodes('path/to/episodes.mat')

function data = load_episodes(filepath)
    % Default filepath if not provided
    if nargin < 1
        filepath = '../data/matlab/episodes.mat';
    end
    
    % Check if file exists
    if ~isfile(filepath)
        error('Episode file not found: %s', filepath);
    end
    
    % Load the .mat file
    fprintf('Loading episodes from: %s\n', filepath);
    data = load(filepath);
    
    % Display summary
    if isfield(data, 'episode_count')
        fprintf('Episodes loaded: %d\n', data.episode_count);
    end
    
    if isfield(data, 'export_timestamp')
        fprintf('Export timestamp: %s\n', data.export_timestamp);
    end
    
    % Extract episodes array if available
    if isfield(data, 'episodes')
        episodes_raw = data.episodes;
        
        % Convert cell array to struct array for easier processing
        if iscell(episodes_raw)
            data = [episodes_raw{:}]';
        else
            data = episodes_raw;
        end
        
        fprintf('Episode structure fields: ');
        if ~isempty(data)
            fields = fieldnames(data(1));
            fprintf('%s ', fields{:});
        end
        fprintf('\n');
    end
end
