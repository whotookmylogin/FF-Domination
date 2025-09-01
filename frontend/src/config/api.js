/**
 * API Configuration for Fantasy Football Domination App
 * Handles dynamic API URL configuration, error handling, and request/response interceptors
 */

import axios from 'axios';

/**
 * Determines the appropriate API base URL based on environment
 * @returns {string} The base URL for API requests
 */
const getApiBaseUrl = () => {
  // Check for custom environment variable first
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Determine based on NODE_ENV and hostname
  const { hostname } = window.location;
  
  // Production environment detection
  if (process.env.NODE_ENV === 'production') {
    // Add production URL when deployed
    return process.env.REACT_APP_PRODUCTION_API_URL || 'https://your-production-api.com';
  }
  
  // Development environment
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return process.env.REACT_APP_DEV_API_URL || 'http://localhost:8000';
  }
  
  // Default fallback
  return 'http://localhost:8000';
};

/**
 * API Configuration object with all settings
 */
export const apiConfig = {
  baseURL: getApiBaseUrl(),
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '30000', 10),
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  retryAttempts: parseInt(process.env.REACT_APP_API_RETRY_ATTEMPTS || '3', 10),
  retryDelay: parseInt(process.env.REACT_APP_API_RETRY_DELAY || '1000', 10)
};

/**
 * Creates and configures axios instance with interceptors
 * @param {Object} customConfig - Custom configuration to override defaults
 * @returns {Object} Configured axios instance
 */
const createApiInstance = (customConfig = {}) => {
  const instance = axios.create({
    baseURL: apiConfig.baseURL,
    timeout: apiConfig.timeout,
    headers: apiConfig.headers,
    ...customConfig  // Allow overriding default config
  });

  /**
   * Request interceptor to add authentication headers and handle common request setup
   */
  instance.interceptors.request.use(
    (config) => {
      // Add authentication token if available
      const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      // Add request timestamp for debugging
      config.metadata = { startTime: new Date().getTime() };
      
      // Log request in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      }
      
      return config;
    },
    (error) => {
      console.error('❌ Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  /**
   * Response interceptor to handle common response processing and error handling
   */
  instance.interceptors.response.use(
    (response) => {
      // Calculate request duration
      const duration = new Date().getTime() - response.config.metadata.startTime;
      
      // Log response in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`);
      }
      
      // Handle different response formats
      if (response.data && typeof response.data === 'object') {
        // Check for API error in successful HTTP response
        if (response.data.status === 'error') {
          throw new Error(response.data.message || 'API returned error status');
        }
        
        // Return data directly if it has expected structure
        if (response.data.status === 'success' && response.data.data !== undefined) {
          return response.data.data;
        }
      }
      
      return response.data;
    },
    async (error) => {
      const originalRequest = error.config;
      
      // Log error in development
      if (process.env.NODE_ENV === 'development') {
        console.error(`❌ API Error: ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`, error);
      }
      
      // Handle different error scenarios
      if (error.response) {
        // Server responded with error status
        const { status, data } = error.response;
        
        switch (status) {
          case 401:
            // Unauthorized - clear auth tokens and redirect to login
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');
            // You might want to dispatch a logout action here
            throw new Error('Authentication required. Please log in again.');
            
          case 403:
            throw new Error('Access forbidden. You don\'t have permission for this action.');
            
          case 404:
            throw new Error('Requested resource not found.');
            
          case 429:
            throw new Error('Too many requests. Please try again later.');
            
          case 500:
            throw new Error('Server error. Please try again later.');
            
          default:
            // Use error message from response if available
            const errorMessage = data?.message || data?.error || `HTTP ${status} error`;
            throw new Error(errorMessage);
        }
      } else if (error.request) {
        // Network error or no response received
        if (error.code === 'ECONNABORTED') {
          throw new Error('Request timeout. Please check your connection and try again.');
        }
        
        throw new Error('Network error. Please check your internet connection.');
      } else {
        // Request configuration error
        throw new Error('Request configuration error: ' + error.message);
      }
    }
  );

  return instance;
};

/**
 * Main API instance with all interceptors configured
 */
export const apiClient = createApiInstance();

/**
 * Special API instance for AI operations with extended timeout
 */
export const aiApiClient = createApiInstance({
  timeout: 120000 // 2 minutes for AI operations
});

// Log the timeout to verify it's set correctly
console.log('🤖 AI API Client initialized with timeout:', aiApiClient.defaults.timeout, 'ms');

/**
 * Utility function to create requests with retry logic
 * @param {Function} requestFn - Function that returns a Promise for the API request
 * @param {number} maxRetries - Maximum number of retry attempts
 * @param {number} delay - Delay between retries in milliseconds
 * @returns {Promise} Promise that resolves with the API response
 */
export const withRetry = async (requestFn, maxRetries = apiConfig.retryAttempts, delay = apiConfig.retryDelay) => {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx) except 408, 429
      if (error.response && error.response.status >= 400 && error.response.status < 500) {
        if (error.response.status !== 408 && error.response.status !== 429) {
          throw error;
        }
      }
      
      // Don't retry on the last attempt
      if (attempt === maxRetries) {
        break;
      }
      
      // Wait before retrying with exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
  
  throw lastError;
};

/**
 * Health check function to test API connectivity
 * @returns {Promise<boolean>} Promise that resolves to true if API is healthy
 */
export const checkApiHealth = async () => {
  try {
    // Check the root endpoint since /health doesn't exist
    const response = await apiClient.get('/');
    // The backend returns {"message":"Fantasy Football Domination API - Phase 3"}
    return response && (response.message || response.status === 'healthy' || response === 'OK') ? true : false;
  } catch (error) {
    console.warn('API health check failed:', error.message);
    return false;
  }
};

/**
 * Export configuration for use in other modules
 */
export default {
  apiClient,
  apiConfig,
  withRetry,
  checkApiHealth,
  getApiBaseUrl
};