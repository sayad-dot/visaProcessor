import api from './api'

export const applicationService = {
  // Create new application
  createApplication: async (data) => {
    const response = await api.post('/applications/', data)
    return response.data
  },

  // Get all applications
  getApplications: async () => {
    const response = await api.get('/applications/')
    return response.data
  },

  // Get single application
  getApplication: async (id) => {
    const response = await api.get(`/applications/${id}`)
    return response.data
  },

  // Delete application
  deleteApplication: async (id) => {
    const response = await api.delete(`/applications/${id}`)
    return response.data
  },

  // Get required documents for application
  getRequiredDocuments: async (id) => {
    const response = await api.get(`/applications/${id}/required-documents`)
    return response.data
  },
}

export const documentService = {
  // Upload document
  uploadDocument: async (applicationId, documentType, file) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('document_type', documentType)

    const response = await api.post(
      `/documents/upload/${applicationId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  // Get documents for application
  getApplicationDocuments: async (applicationId) => {
    const response = await api.get(`/documents/application/${applicationId}`)
    return response.data
  },

  // Delete document
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/documents/${documentId}`)
    return response.data
  },

  // Process documents
  processDocuments: async (applicationId) => {
    const response = await api.post(`/documents/process/${applicationId}`)
    return response.data
  },

  // Get required documents for a country and visa type
  getRequiredDocuments: async (country, visaType) => {
    const response = await api.get(`/required-documents/${country}/${visaType}`)
    return response.data
  },
}

export const generateService = {
  // Analyze documents and identify missing info
  analyzeDocuments: async (applicationId) => {
    const response = await api.post(`/generate/${applicationId}/analyze`)
    return response.data
  },

  // Generate missing documents
  generateDocuments: async (applicationId) => {
    const response = await api.post(`/generate/${applicationId}/generate`)
    return response.data
  },

  // Download all documents
  downloadAllDocuments: async (applicationId) => {
    const response = await api.get(`/generate/${applicationId}/download-all`, {
      responseType: 'blob',
    })
    return response.data
  },
}
