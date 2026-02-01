import api from './api'
import mockApi from './mockApi'

// DEMO MODE - Set to true for demo branch
const DEMO_MODE = true

export const applicationService = {
  // Create new application
  createApplication: async (data) => {
    if (DEMO_MODE) return mockApi.createApplication(data)
    const response = await api.post('/applications/', data)
    return response.data
  },

  // Get all applications
  getApplications: async () => {
    if (DEMO_MODE) return mockApi.getApplications()
    const response = await api.get('/applications/')
    return response.data
  },

  // Get single application
  getApplication: async (id) => {
    if (DEMO_MODE) return mockApi.getApplication(id)
    const response = await api.get(`/applications/${id}`)
    return response.data
  },

  // Delete application
  deleteApplication: async (id) => {
    if (DEMO_MODE) return { success: true }
    const response = await api.delete(`/applications/${id}`)
    return response.data
  },

  // Get required documents for application
  getRequiredDocuments: async (id) => {
    if (DEMO_MODE) {
      // Return all 16 document types with proper document_type field
      return [
        { id: 1, name: 'Passport', document_type: 'passport', is_mandatory: true, is_uploaded: false, can_be_generated: false },
        { id: 2, name: 'Bank Statement', document_type: 'bank_statement', is_mandatory: true, is_uploaded: false, can_be_generated: false },
        { id: 3, name: 'Employment Certificate', document_type: 'employment_certificate', is_mandatory: true, is_uploaded: false, can_be_generated: false },
        { id: 4, name: 'Photo', document_type: 'photo', is_mandatory: false, is_uploaded: false, can_be_generated: false },
        { id: 5, name: 'Travel History', document_type: 'travel_history', is_mandatory: false, is_uploaded: false, can_be_generated: false },
        { id: 6, name: 'Cover Letter', document_type: 'cover_letter', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 7, name: 'Travel Itinerary', document_type: 'travel_itinerary', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 8, name: 'Financial Documents', document_type: 'financial_documents', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 9, name: 'Home Ties Statement', document_type: 'home_ties', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 10, name: 'Asset Valuation', document_type: 'asset_valuation', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 11, name: 'Previous Travel History', document_type: 'previous_travel', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 12, name: 'Air Ticket', document_type: 'air_ticket', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 13, name: 'Hotel Booking', document_type: 'hotel_booking', is_mandatory: false, is_uploaded: false, can_be_generated: true },
        { id: 14, name: 'TIN Certificate', document_type: 'tin_certificate', is_mandatory: false, is_uploaded: false, can_be_generated: false },
        { id: 15, name: 'Trade License', document_type: 'trade_license', is_mandatory: false, is_uploaded: false, can_be_generated: false },
        { id: 16, name: 'Tax Certificate', document_type: 'tax_certificate', is_mandatory: false, is_uploaded: false, can_be_generated: false }
      ]
    }
    const response = await api.get(`/applications/${id}/required-documents`)
    return response.data
  },
}

export const documentService = {
  // Upload document
  uploadDocument: async (applicationId, documentType, file) => {
    if (DEMO_MODE) return mockApi.uploadDocument(applicationId, file, documentType)
    
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
    if (DEMO_MODE) return mockApi.getDocuments(applicationId)
    const response = await api.get(`/documents/application/${applicationId}`)
    return response.data
  },

  // Delete document
  deleteDocument: async (documentId) => {
    if (DEMO_MODE) return mockApi.deleteDocument(documentId)
    const response = await api.delete(`/documents/${documentId}`)
    return response.data
  },

  // Process documents
  processDocuments: async (applicationId) => {
    if (DEMO_MODE) return mockApi.analyzeDocuments(applicationId)
    const response = await api.post(`/documents/process/${applicationId}`)
    return response.data
  },
}

// Analysis Service
export const analysisService = {
  analyzeDocuments: async (applicationId) => {
    if (DEMO_MODE) return mockApi.analyzeDocuments(applicationId)
    const response = await api.post(`/api/analysis/analyze/${applicationId}`)
    return response.data
  },
  
  getAnalysisResults: async (applicationId) => {
    if (DEMO_MODE) return mockApi.analyzeDocuments(applicationId)
    const response = await api.get(`/api/analysis/results/${applicationId}`)
    return response.data
  }
}

// Questionnaire Service
export const questionnaireService = {
  getQuestionnaire: async (applicationId) => {
    if (DEMO_MODE) return mockApi.getQuestionnaire(applicationId)
    const response = await api.get(`/api/questionnaire/generate/${applicationId}`)
    return response.data
  },
  
  saveResponses: async (applicationId, responses) => {
    if (DEMO_MODE) return mockApi.saveQuestionnaireResponses(applicationId, responses)
    const response = await api.post(`/api/questionnaire/response/${applicationId}`, { responses })
    return response.data
  }
}

// Document Generation Service
export const generationService = {
  generateDocuments: async (applicationId) => {
    if (DEMO_MODE) return mockApi.generateDocuments(applicationId)
    const response = await api.post(`/api/generate/${applicationId}`)
    return response.data
  },
  
  downloadZip: async (applicationId) => {
    if (DEMO_MODE) return mockApi.downloadZip(applicationId)
    const response = await api.get(`/api/generate/download/${applicationId}`, { responseType: 'blob' })
    return response.data
  }
}

export const requiredDocumentsService = {
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
