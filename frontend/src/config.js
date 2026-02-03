// API Configuration - centralized API URLs
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const API_ROOT = API_BASE_URL.replace('/api', '');

export { API_BASE_URL, API_ROOT };
