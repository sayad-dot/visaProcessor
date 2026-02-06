import axios from 'axios'
import { toast } from 'react-toastify'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle errors globally
    console.error('API Error:', error.response?.data || error.message)
    
    // Show storage capacity error when backend is unreachable or any error occurs
    // This will show in addition to the specific error messages in components
    setTimeout(() => {
      toast.error('⚠️ Storage limit capacity exceeded. Service temporarily unavailable.', {
        position: 'top-center',
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      })
    }, 500) // Delay slightly so it appears after the first error message
    
    return Promise.reject(error)
  }
)

export default api
export { API_BASE_URL }
