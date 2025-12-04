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
  timeout: 300000, // 5 minute timeout for complex reasoning queries
});

/**
 * Submit a query to SIRA
 * @param {string} query - The query text
 * @param {string} sessionId - Optional session ID
 * @returns {Promise} Response with reasoning result
 */
export const submitQuery = async (query, sessionId = null) => {
  try {
    const response = await apiClient.post('/query', {
      query,
      session_id: sessionId,
    });
    return response.data;
  } catch (error) {
    // Enhanced error handling
    if (error.code === 'ECONNABORTED') {
      throw new Error(
        'Request timeout (5 minutes). This query is taking too long. Try a simpler query or check if SIRA is running.'
      );
    } else if (error.response) {
      // Server responded with error
      const serverMessage = error.response.data?.error || error.response.data?.detail || 'Server error';
      throw new Error(`Server error: ${serverMessage}`);
    } else if (error.request) {
      // Request made but no response
      throw new Error(
        'No response from server. Is SIRA API running on http://localhost:8080?'
      );
    } else {
      // Something else happened
      throw new Error(`Request failed: ${error.message}`);
    }
  }
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
