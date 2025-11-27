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
        data = data.episodes;  % Return episodes array directly
        fprintf('Episode structure fields: ');
        if ~isempty(data)
            if iscell(data)
                fields = fieldnames(data{1});
            else
                fields = fieldnames(data(1));
            end
            fprintf('%s ', fields{:});
        end
        fprintf('\n');
    end
end
