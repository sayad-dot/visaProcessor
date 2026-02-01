import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  Chip,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert
} from '@mui/material'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import UploadIcon from '@mui/icons-material/Upload'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import { applicationService, documentService } from '../services/apiService'
import ProgressTracker from '../components/ProgressTracker'
import DocumentList from '../components/DocumentList'
import DocumentUploader from '../components/DocumentUploader'
import AnalysisSection from '../components/AnalysisSection'
import QuestionnaireWizard from '../components/QuestionnaireWizard'
import GenerationSection from '../components/GenerationSection'

const ApplicationDetailsPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [application, setApplication] = useState(null)
  const [requiredDocuments, setRequiredDocuments] = useState([])
  const [uploadedDocuments, setUploadedDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [selectedDocumentType, setSelectedDocumentType] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [questionnaireOpen, setQuestionnaireOpen] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)

  useEffect(() => {
    fetchApplicationData()
  }, [id])

  const fetchApplicationData = async () => {
    try {
      setLoading(true)
      
      // Fetch application details
      const appData = await applicationService.getApplication(id)
      setApplication(appData)
      
      // Fetch required documents for Iceland tourist visa
      const reqDocs = await documentService.getRequiredDocuments('iceland', 'tourist')
      setRequiredDocuments(reqDocs)
      
      // Fetch uploaded documents
      const uploadedDocs = await documentService.getApplicationDocuments(id)
      setUploadedDocuments(uploadedDocs)
      
    } catch (error) {
      toast.error('Failed to load application data')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadClick = (documentType) => {
    setSelectedDocumentType(documentType)
    setUploadDialogOpen(true)
  }

  const handleUploadSuccess = async (uploadedDoc) => {
    toast.success('Document uploaded successfully!')
    setUploadDialogOpen(false)
    
    // Refresh uploaded documents
    try {
      const uploadedDocs = await documentService.getApplicationDocuments(id)
      setUploadedDocuments(uploadedDocs)
    } catch (error) {
      console.error('Error refreshing documents:', error)
    }
  }

  const handleUploadError = (error) => {
    toast.error(error.message || 'Upload failed')
  }

  const handleDeleteDocument = async (document) => {
    if (!window.confirm(`Are you sure you want to delete ${document.document_name}?`)) {
      return
    }

    try {
      await documentService.deleteDocument(document.id)
      toast.success('Document deleted successfully')
      
      // Refresh uploaded documents
      const uploadedDocs = await documentService.getApplicationDocuments(id)
      setUploadedDocuments(uploadedDocs)
    } catch (error) {
      toast.error('Failed to delete document')
      console.error(error)
    }
  }

  const handleViewDocument = (document) => {
    // Open document in new tab
    window.open(`http://localhost:8000${document.file_path}`, '_blank')
  }

  const handleProcessDocuments = async () => {
    if (uploadedDocuments.length === 0) {
      toast.warning('Please upload documents before processing')
      return
    }

    if (!window.confirm('This will analyze all uploaded documents. Continue?')) {
      return
    }

    try {
      setProcessing(true)
      await documentService.processDocuments(id)
      toast.success('Documents processed successfully!')
      
      // Refresh application data
      await fetchApplicationData()
    } catch (error) {
      toast.error('Failed to process documents')
      console.error(error)
    } finally {
      setProcessing(false)
    }
  }

  const handleAnalysisComplete = (data) => {
    setAnalysisComplete(true)
    toast.success('Analysis complete! You can now fill the questionnaire.')
    // Optionally open questionnaire automatically
    setTimeout(() => {
      setQuestionnaireOpen(true)
    }, 1000)
  }

  const handleQuestionnaireComplete = () => {
    toast.success('Questionnaire completed! Ready for document generation.')
    fetchApplicationData()
  }

  const getStatusColor = (status) => {
    const colors = {
      draft: 'default',
      documents_uploaded: 'info',
      analyzing: 'warning',
      generating: 'warning',
      completed: 'success',
      failed: 'error',
    }
    return colors[status] || 'default'
  }

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (!application) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">Application not found</Alert>
          <Button onClick={() => navigate('/')} sx={{ mt: 2 }}>
            Back to Applications
          </Button>
        </Box>
      </Container>
    )
  }

  const uploadedCount = uploadedDocuments.length
  
  // Count only MANDATORY documents (not optional, not AI-generated)
  const mandatoryDocuments = requiredDocuments.filter(doc => 
    doc.is_mandatory === true && doc.can_be_generated === false
  )
  const requiredCount = mandatoryDocuments.length
  
  // Count how many mandatory documents have been uploaded
  const uploadedMandatoryCount = mandatoryDocuments.filter(reqDoc => 
    uploadedDocuments.some(upDoc => upDoc.document_type === reqDoc.document_type)
  ).length
  
  // All mandatory documents uploaded
  const allDocumentsUploaded = uploadedMandatoryCount === requiredCount && requiredCount > 0

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Application Details
          </Typography>
          <Button variant="outlined" onClick={() => navigate('/')}>
            Back to Applications
          </Button>
        </Box>

        {/* Progress Tracker */}
        <ProgressTracker
          requiredDocuments={requiredDocuments}
          uploadedDocuments={uploadedDocuments}
        />

        <Grid container spacing={3}>
          {/* Application Information */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Application Information
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Application Number
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {application.application_number}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Status
                    </Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <Chip
                        label={application.status.replace('_', ' ').toUpperCase()}
                        color={getStatusColor(application.status)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Country
                    </Typography>
                    <Typography variant="body1">
                      {application.country}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Visa Type
                    </Typography>
                    <Typography variant="body1">
                      {application.visa_type}
                    </Typography>
                  </Grid>
                  
                  {application.applicant_name && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Applicant Name
                      </Typography>
                      <Typography variant="body1">
                        {application.applicant_name}
                      </Typography>
                    </Grid>
                  )}
                  
                  {application.applicant_email && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Email
                      </Typography>
                      <Typography variant="body1">
                        {application.applicant_email}
                      </Typography>
                    </Grid>
                  )}
                  
                  {application.applicant_phone && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Phone
                      </Typography>
                      <Typography variant="body1">
                        {application.applicant_phone}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            </Paper>
          </Grid>

          {/* Documents Section */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Documents Management
                </Typography>
                <Button
                  variant="contained"
                  startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <AnalyticsIcon />}
                  onClick={handleProcessDocuments}
                  disabled={!allDocumentsUploaded || processing}
                >
                  {processing ? 'Processing...' : 'Analyze Documents'}
                </Button>
              </Box>
              
              <DocumentList
                requiredDocuments={requiredDocuments}
                uploadedDocuments={uploadedDocuments}
                onUpload={handleUploadClick}
                onDelete={handleDeleteDocument}
                onView={handleViewDocument}
              />
            </Paper>
          </Grid>

          {/* Analysis Section - Show only if documents uploaded */}
          {uploadedDocuments.length > 0 && (
            <Grid item xs={12}>
              <AnalysisSection
                applicationId={id}
                onAnalysisComplete={handleAnalysisComplete}
                onOpenQuestionnaire={() => setQuestionnaireOpen(true)}
              />
            </Grid>
          )}

          {/* Questionnaire Button - Show only if analysis complete */}
          {analysisComplete && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Next Step: Complete Questionnaire
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Please answer the questions to provide additional information for your visa application.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={() => setQuestionnaireOpen(true)}
                >
                  Fill Questionnaire
                </Button>
              </Paper>
            </Grid>
          )}

          {/* Document Generation Section - Show after questionnaire */}
          {analysisComplete && (
            <Grid item xs={12}>
              <GenerationSection 
                applicationId={id} 
                applicantName={application?.applicant_name || ''}
              />
            </Grid>
          )}
        </Grid>
      </Box>

      {/* Upload Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Upload Document: {selectedDocumentType?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <DocumentUploader
              applicationId={id}
              documentType={selectedDocumentType}
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Questionnaire Wizard Dialog */}
      <QuestionnaireWizard
        open={questionnaireOpen}
        onClose={() => setQuestionnaireOpen(false)}
        applicationId={id}
        onComplete={handleQuestionnaireComplete}
      />
    </Container>
  )
}

export default ApplicationDetailsPage
