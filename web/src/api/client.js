/**
 * API client for SIRA backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60s timeout for reasoning queries
});

/**
 * Submit a query to SIRA
 * @param {string} query - The query text
 * @param {string} sessionId - Optional session ID
 * @returns {Promise} Response with reasoning result
 */
export const submitQuery = async (query, sessionId = null) => {
  const response = await apiClient.post('/query', {
    query,
    session_id: sessionId,
  });
  return response.data;
};

/**
 * Get metrics summary
 * @returns {Promise} Metrics data
 */
export const getMetrics = async () => {
  const response = await apiClient.get('/metrics/summary');
  return response.data;
};

/**
 * Get core metrics
 * @param {string} tier - Tier filter (tier1, tier2, tier3, all)
 * @returns {Promise} Core metrics data
 */
export const getCoreMetrics = async (tier = 'all') => {
  const response = await apiClient.get(`/metrics/core?tier=${tier}`);
  return response.data;
};

/**
 * Get session history
 * @param {string} sessionId - Session ID
 * @returns {Promise} Session data
 */
export const getSession = async (sessionId) => {
  const response = await apiClient.get(`/session/${sessionId}`);
  return response.data;
};

/**
 * Health check
 * @returns {Promise} Health status
 */
export const healthCheck = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;
