import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for large file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API functions
export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Get version information
  getVersion: () => api.get('/version'),

  // File upload
  uploadFile: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5 minutes for large file uploads and analysis
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },

  // Get upload status
  getUploadStatus: (fileId) => api.get(`/upload/status/${fileId}`),

  // Clean up uploaded file
  cleanupFile: (fileId) => api.delete(`/upload/cleanup/${fileId}`),

  // Get network interfaces
  getInterfaces: () => api.get('/interfaces'),

  // Get system status
  getSystemStatus: () => api.get('/system/status'),

  // Get system capabilities
  getSystemCapabilities: () => api.get('/system/capabilities'),

  // Replay operations
  startReplay: (config) => api.post('/replay/start', config),
  
  stopReplay: () => api.post('/replay/stop'),
  
  getReplayStatus: () => api.get('/replay/status'),
  
  getReplayHistory: (limit = 20, offset = 0, search = '', status = 'ALL') => {
    const params = new URLSearchParams({ limit, offset });
    if (search && search.trim()) {
      params.append('search', search.trim());
    }
    if (status && status !== 'ALL') {
      params.append('status', status);
    }
    return api.get(`/replay/history?${params.toString()}`);
  },
  
  validateReplayConfig: (config) => api.post('/replay/validate', config),

  // Log operations
  getRecentLogs: (count = 100) => api.get(`/logs/recent?count=${count}`),
  
  getLogStats: () => api.get('/logs/stats'),
};

// Utility functions
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDuration = (seconds) => {
  if (!seconds || seconds < 0) return '0s';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

export const formatSpeed = (speed, unit) => {
  switch (unit) {
    case 'pps':
      return `${speed} PPS`;
    case 'mbps':
      return `${speed} Mbps`;
    case 'gbps':
      return `${speed} Gbps`;
    case 'multiplier':
    default:
      return `${speed}x`;
  }
};

export default api;
