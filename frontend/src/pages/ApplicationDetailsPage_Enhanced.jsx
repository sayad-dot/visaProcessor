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
  Alert,
  LinearProgress,
  Snackbar
} from '@mui/material'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import UploadIcon from '@mui/icons-material/Upload'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import WarningIcon from '@mui/icons-material/Warning'
import ErrorIcon from '@mui/icons-material/Error'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { applicationService, documentService } from '../services/apiService'
import ProgressTracker from '../components/ProgressTracker'
import DocumentList from '../components/DocumentList'
import DocumentUploader from '../components/DocumentUploader'
import AnalysisSection from '../components/AnalysisSection_Demo';
import QuestionnaireWizard from '../components/QuestionnaireWizard_Demo';
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
  
  // Demo-specific states
  const [uploadingDocuments, setUploadingDocuments] = useState({})
  const [storageUsed, setStorageUsed] = useState(0)
  const [showStorageWarning, setShowStorageWarning] = useState(false)
  const [analyzingProgress, setAnalyzingProgress] = useState(0)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState({ open: false, current: 0, total: 0, error: null })

  useEffect(() => {
    fetchApplicationData()
  }, [id])

  const fetchApplicationData = async () => {
    try {
      setLoading(true)
      
      // Fetch application details
      const appData = await applicationService.getApplication(id)
      setApplication(appData)
      
      // Fetch required documents
      const reqDocs = await applicationService.getRequiredDocuments(id)
      setRequiredDocuments(reqDocs)
      
      // Fetch uploaded documents
      const uploadedDocs = await documentService.getApplicationDocuments(id)
      setUploadedDocuments(uploadedDocs)
      
    } catch (error) {
      console.error('Error loading data:', error)
      if (!requiredDocuments.length) {
        setRequiredDocuments([])
      }
      if (!uploadedDocuments.length) {
        setUploadedDocuments([])
      }
    } finally {
      setLoading(false)
    }
  }

  const handleUploadClick = (documentType) => {
    setSelectedDocumentType(documentType)
    setUploadDialogOpen(true)
  }

  const simulateUpload = async (file, documentType) => {
    // Simulate upload with random progress
    setUploadingDocuments(prev => ({
      ...prev,
      [documentType]: { uploading: true, progress: 0, status: 'Uploading...' }
    }))

    // Upload phase (0-60%)
    for (let i = 0; i <= 60; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 100))
      setUploadingDocuments(prev => ({
        ...prev,
        [documentType]: { uploading: true, progress: i, status: 'Uploading...' }
      }))
    }

    // Extracting phase (60-100%)
    setUploadingDocuments(prev => ({
      ...prev,
      [documentType]: { uploading: true, progress: 60, status: 'Extracting text...' }
    }))
    
    for (let i = 65; i <= 100; i += 5) {
      await new Promise(resolve => setTimeout(resolve, 150))
      setUploadingDocuments(prev => ({
        ...prev,
        [documentType]: { uploading: true, progress: i, status: 'Extracting text...' }
      }))
    }

    // Complete
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // Add to uploaded documents
    const newDoc = {
      id: Date.now(),
      document_type: documentType,
      file_name: file.name,
      uploaded_at: new Date().toISOString(),
      extraction_status: 'completed'
    }
    
    setUploadedDocuments(prev => [...prev, newDoc])
    
    // Update storage
    const newStorage = storageUsed + 1
    setStorageUsed(newStorage)
    
    // Show storage warning after 5-6 uploads
    if (newStorage === 5 || newStorage === 6) {
      setTimeout(() => {
        setShowStorageWarning(true)
      }, 500)
    }
    
    // Clear uploading state
    setUploadingDocuments(prev => {
      const newState = { ...prev }
      delete newState[documentType]
      return newState
    })
    
    toast.success(`${file.name} uploaded successfully!`)
  }

  const handleUploadSuccess = async (file) => {
    setUploadDialogOpen(false)
    await simulateUpload(file, selectedDocumentType)
  }

  const handleUploadError = (error) => {
    toast.error(error.message || 'Upload failed')
  }

  const handleDeleteDocument = async (document) => {
    if (!window.confirm(`Are you sure you want to delete ${document.file_name}?`)) {
      return
    }

    try {
      // Remove from uploaded documents
      setUploadedDocuments(prev => prev.filter(doc => doc.id !== document.id))
      setStorageUsed(prev => Math.max(0, prev - 1))
      toast.success('Document deleted successfully')
    } catch (error) {
      toast.error('Failed to delete document')
      console.error(error)
    }
  }

  const handleAnalyzeDocuments = async () => {
    if (uploadedDocuments.length === 0) {
      toast.warning('Please upload at least one document before analyzing')
      return
    }

    setIsAnalyzing(true)
    setAnalyzingProgress(0)

    // Simulate analysis with progress
    toast.info('Starting document analysis...')
    
    // Extraction phase (0-98%)
    for (let i = 0; i <= 98; i += 2) {
      await new Promise(resolve => setTimeout(resolve, 80))
      setAnalyzingProgress(i)
      
      if (i === 30) {
        toast.info('Extracting text from documents...')
      } else if (i === 70) {
        toast.info('Analyzing document quality...')
      } else if (i === 90) {
        toast.info('Validating extracted data...')
      }
    }

    // Final completion
    await new Promise(resolve => setTimeout(resolve, 500))
    setAnalyzingProgress(98)
    
    await new Promise(resolve => setTimeout(resolve, 300))
    setAnalyzingProgress(100)
    
    await new Promise(resolve => setTimeout(resolve, 500))
    
    setIsAnalyzing(false)
    setAnalysisComplete(true)
    
    // Show score dialog
    const score = 87 + Math.floor(Math.random() * 6) // 87-92%
    toast.success(`Analysis complete! Overall score: ${score}%`)
    
    // Auto-open questionnaire
    setTimeout(() => {
      setQuestionnaireOpen(true)
    }, 1000)
  }

  const handleQuestionnaireComplete = () => {
    toast.success('Questionnaire completed! Ready for document generation.')
    setQuestionnaireOpen(false)
  }

  const handleGenerateDocuments = async () => {
    // Start download with progress
    setDownloadProgress({ open: true, current: 0, total: 8, error: null })
    
    const files = [
      'Cover Letter', 'Travel Itinerary', 'Financial Statement',
      'Home Ties Declaration', 'Asset Valuation', 'Travel History',
      'Air Ticket Booking', 'Hotel Reservation'
    ]
    
    for (let i = 0; i < files.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800))
      setDownloadProgress({ open: true, current: i + 1, total: 8, error: null })
      toast.info(`Generating: ${files[i]}...`)
      
      // After 2 files, show storage error
      if (i === 1) {
        await new Promise(resolve => setTimeout(resolve, 500))
        setDownloadProgress({
          open: true,
          current: 2,
          total: 8,
          error: 'Database storage limit exceeded. Cannot generate remaining documents.'
        })
        toast.error('Storage limit exceeded!', { autoClose: false })
        return
      }
    }
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
  const requiredCount = requiredDocuments.filter(doc => doc.is_mandatory && !doc.can_be_generated).length

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

        {/* Storage Warning Bar */}
        {storageUsed > 0 && (
          <Alert 
            severity={storageUsed >= 5 ? "warning" : "info"} 
            sx={{ mb: 3 }}
            icon={storageUsed >= 5 ? <WarningIcon /> : undefined}
          >
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Storage Usage: {storageUsed} / 10 documents ({(storageUsed * 10).toFixed(0)}%)
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={storageUsed * 10} 
                color={storageUsed >= 5 ? "warning" : "primary"}
                sx={{ height: 6, borderRadius: 1 }}
              />
            </Box>
          </Alert>
        )}

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
                  startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <AnalyticsIcon />}
                  onClick={handleAnalyzeDocuments}
                  disabled={uploadedCount === 0 || isAnalyzing}
                >
                  {isAnalyzing ? `Analyzing... ${analyzingProgress}%` : 'Analyze Documents'}
                </Button>
              </Box>
              
              {/* Analyzing Progress Bar */}
              {isAnalyzing && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Extracting and analyzing documents...
                  </Typography>
                  <LinearProgress variant="determinate" value={analyzingProgress} sx={{ height: 8, borderRadius: 1 }} />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                    {analyzingProgress < 30 ? 'Reading documents...' : 
                     analyzingProgress < 70 ? 'Extracting text...' : 
                     analyzingProgress < 90 ? 'Analyzing quality...' : 
                     'Finalizing results...'}
                  </Typography>
                </Box>
              )}
              
              <DocumentList
                requiredDocuments={requiredDocuments}
                uploadedDocuments={uploadedDocuments}
                onUpload={handleUploadClick}
                onDelete={handleDeleteDocument}
                uploadingDocuments={uploadingDocuments}
              />
            </Paper>
          </Grid>

          {/* Analysis Section */}
          {analysisComplete && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 2 }}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    Analysis Complete! Overall Score: 98%
                  </Typography>
                  <Typography variant="body2">
                    Documents successfully extracted and validated. Ready for questionnaire.
                  </Typography>
                </Alert>
                
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={() => setQuestionnaireOpen(true)}
                  fullWidth
                >
                  Fill Questionnaire
                </Button>
              </Paper>
            </Grid>
          )}

          {/* Document Generation Section */}
          {analysisComplete && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Generate Documents
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Generate required visa documents based on your uploaded documents and questionnaire responses.
                </Typography>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={handleGenerateDocuments}
                  disabled={downloadProgress.open}
                >
                  Generate & Download Documents
                </Button>
              </Paper>
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
          Upload: {selectedDocumentType?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
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
          <Button onClick={() => setUploadDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Storage Warning Dialog */}
      <Dialog open={showStorageWarning} onClose={() => setShowStorageWarning(false)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon color="warning" />
            Storage Warning
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            You have reached 50% of your storage limit ({storageUsed}/10 documents).
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Please consider deleting unnecessary documents or upgrading your plan.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowStorageWarning(false)} color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>

      {/* Download Progress Dialog */}
      <Dialog open={downloadProgress.open} onClose={() => {}} disableEscapeKeyDown>
        <DialogTitle>
          {downloadProgress.error ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ErrorIcon color="error" />
              Generation Failed
            </Box>
          ) : (
            'Generating Documents...'
          )}
        </DialogTitle>
        <DialogContent sx={{ minWidth: 400 }}>
          {downloadProgress.error ? (
            <Alert severity="error">
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                {downloadProgress.error}
              </Typography>
              <Typography variant="caption">
                Generated {downloadProgress.current} of {downloadProgress.total} documents before failure.
              </Typography>
            </Alert>
          ) : (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Generating file {downloadProgress.current} of {downloadProgress.total}...
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(downloadProgress.current / downloadProgress.total) * 100} 
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setDownloadProgress({ open: false, current: 0, total: 0, error: null })}
            color="primary"
          >
            {downloadProgress.error ? 'Close' : 'Cancel'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Questionnaire Wizard */}
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
