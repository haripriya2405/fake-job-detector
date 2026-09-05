import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s timeout to allow multi-modal and OCR extraction
});

// Attach Authorization Bearer token to outgoing requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sentinel_auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for consistent and graceful user-facing error normalization
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected network error occurred. Please try again.';

    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;

      // Extract detail or message from FastAPI response
      if (data?.detail) {
        if (typeof data.detail === 'string') {
          message = data.detail;
        } else if (Array.isArray(data.detail)) {
          // Pydantic validation error array
          message = data.detail.map((err) => err.msg || JSON.stringify(err)).join('; ');
        } else if (typeof data.detail === 'object') {
          message = data.detail.message || JSON.stringify(data.detail);
        }
      } else if (data?.message) {
        message = data.message;
      } else if (status === 401) {
        message = 'Authentication required or session expired. Please sign in again.';
        localStorage.removeItem('sentinel_auth_token');
        localStorage.removeItem('sentinel_user');
      } else if (status === 403) {
        message = 'Access denied. You do not have permission to perform this action.';
      } else if (status === 404) {
        message = 'Requested analysis resource not found.';
      } else if (status === 413) {
        message = 'Uploaded file exceeds maximum allowed size (10 MB).';
      } else if (status === 422) {
        message = 'Input validation failed. Please check your submission format.';
      } else if (status >= 500) {
        message = 'SentinelJob backend service encountered an issue. Please retry.';
      }
    } else if (error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'))) {
      message = 'Request timed out while analyzing content. Please try again.';
    } else if (error.message && error.message.toLowerCase().includes('network error')) {
      message = 'Cannot connect to SentinelJob AI API. Please verify the backend is running.';
    }

    const customError = new Error(message);
    customError.status = error.response?.status;
    customError.data = error.response?.data;
    customError.originalError = error;

    return Promise.reject(customError);
  }
);

export default apiClient;
