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
  Snackbar,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Stack,
  Fade,
  Slide,
  Grow
} from '@mui/material'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import UploadIcon from '@mui/icons-material/Upload'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import WarningIcon from '@mui/icons-material/Warning'
import ErrorIcon from '@mui/icons-material/Error'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import DescriptionIcon from '@mui/icons-material/Description'
import StorageIcon from '@mui/icons-material/Storage'
import DownloadIcon from '@mui/icons-material/Download'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile'
import { applicationService, documentService } from '../services/apiService'
import ProgressTracker from '../components/ProgressTracker'
import DocumentUploader from '../components/DocumentUploader'
import QuestionnaireWizard from '../components/QuestionnaireWizard_Demo'

const ApplicationDetailsPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [application, setApplication] = useState(null)
  const [requiredDocuments, setRequiredDocuments] = useState([])
  const [uploadedDocuments, setUploadedDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [selectedDocumentType, setSelectedDocumentType] = useState(null)
  const [questionnaireOpen, setQuestionnaireOpen] = useState(false)
  const [showGenerateButton, setShowGenerateButton] = useState(false)
  
  // Demo-specific states
  const [uploadingDocuments, setUploadingDocuments] = useState({})
  const [storageUsed, setStorageUsed] = useState(0)
  const [showStorageWarning, setShowStorageWarning] = useState(false)
  const [analyzingProgress, setAnalyzingProgress] = useState(0)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [downloadProgress, setDownloadProgress] = useState({ open: false, current: 0, total: 0, error: null, files: [] })

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
      
      // Fetch uploaded documents (empty initially for demo)
      const uploadedDocs = await documentService.getApplicationDocuments(id)
      setUploadedDocuments(uploadedDocs)
      
    } catch (error) {
      console.error('Error loading data:', error)
      toast.error('Failed to load application data')
    } finally {
      setLoading(false)
    }
  }

  const handleUploadClick = (documentType) => {
    setSelectedDocumentType(documentType)
    setUploadDialogOpen(true)
  }

  const simulateUpload = async (file, documentType) => {
    const docName = documentType.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    
    // Initialize uploading state
    setUploadingDocuments(prev => ({
      ...prev,
      [documentType]: { uploading: true, progress: 0, status: 'Uploading...' }
    }))

    // Upload phase (0-60%)
    for (let i = 0; i <= 60; i += 5) {
      await new Promise(resolve => setTimeout(resolve, 80))
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
      await new Promise(resolve => setTimeout(resolve, 100))
      setUploadingDocuments(prev => ({
        ...prev,
        [documentType]: { uploading: true, progress: i, status: 'Extracting text...' }
      }))
    }

    await new Promise(resolve => setTimeout(resolve, 300))
    
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
    
    // Show storage warning at 50%
    if (newStorage === 5) {
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
    
    toast.success(`${docName} uploaded successfully!`)
  }

  const handleUploadSuccess = async (file) => {
    setUploadDialogOpen(false)
    await simulateUpload(file, selectedDocumentType)
  }

  const handleUploadError = (error) => {
    toast.error(error.message || 'Upload failed')
    setUploadDialogOpen(false)
  }

  const handleDeleteDocument = async (document) => {
    const docName = document.document_type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    
    if (!window.confirm(`Delete ${docName}?`)) {
      return
    }

    setUploadedDocuments(prev => prev.filter(doc => doc.id !== document.id))
    setStorageUsed(prev => Math.max(0, prev - 1))
    toast.success(`${docName} deleted`)
  }

  const handleAnalyzeDocuments = async () => {
    if (uploadedDocuments.length === 0) {
      toast.warning('Please upload at least one document')
      return
    }

    // Show 50% warning before analysis if less than 5 documents
    if (uploadedDocuments.length < 5) {
      toast.warning('⚠️ Storage at 50% capacity before analysis!', { autoClose: 3000 })
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    setIsAnalyzing(true)
    setAnalyzingProgress(0)

    toast.info('🔍 Starting analysis...')
    
    // Extraction and analysis (0-98%)
    for (let i = 0; i <= 98; i += 2) {
      await new Promise(resolve => setTimeout(resolve, 60))
      setAnalyzingProgress(i)
      
      if (i === 20) {
        toast.info('📄 Reading documents...')
      } else if (i === 50) {
        toast.info('✨ Extracting text...')
      } else if (i === 80) {
        toast.info('🔍 Analyzing quality...')
      }
    }

    await new Promise(resolve => setTimeout(resolve, 500))
    setAnalyzingProgress(100)
    
    await new Promise(resolve => setTimeout(resolve, 800))
    
    setIsAnalyzing(false)
    setAnalysisResults({
      score: 98,
      extracted: uploadedDocuments.length,
      total: requiredDocuments.length
    })
    
    toast.success('✅ Analysis complete! Score: 98%')
    
    // Always show 80% storage warning after analysis
    setTimeout(() => {
      toast.warning('⚠️ Storage at 80% capacity!', { autoClose: 4000 })
    }, 1000)
    
    // Auto-open questionnaire after delay
    setTimeout(() => {
      setQuestionnaireOpen(true)
    }, 2000)
  }

  const handleQuestionnaireComplete = () => {
    toast.success('✅ Questionnaire completed!')
    setQuestionnaireOpen(false)
    setShowGenerateButton(true)
  }

  const handleGenerateDocuments = async () => {
    const files = [
      'Cover Letter.pdf',
      'Travel Itinerary.pdf',
      'Financial Statement.pdf',
      'Home Ties Declaration.pdf',
      'Asset Valuation.pdf',
      'Travel History.pdf',
      'Air Ticket Booking.pdf',
      'Hotel Reservation.pdf'
    ]
    
    setDownloadProgress({ open: true, current: 0, total: files.length, error: null, files: [] })
    
    // Generate first file
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setDownloadProgress({
      open: true,
      current: 1,
      total: files.length,
      files: [files[0]],
      error: null
    })
    
    toast.success(`✅ Downloaded: ${files[0]}`)
    
    // Generate second file
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setDownloadProgress({
      open: true,
      current: 2,
      total: files.length,
      files: [files[0], files[1]],
      error: null
    })
    
    toast.success(`✅ Downloaded: ${files[1]}`)
    
    // After 2 files, show 100% storage error
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setDownloadProgress({
      open: true,
      current: 2,
      total: files.length,
      error: '❌ ERROR 503: Storage limit exceeded! 100% capacity reached. Database storage full. Cannot generate remaining documents. System resources exhausted.',
      files: [files[0], files[1]]
    })
    
    toast.error('💥 Storage 100% - System full!', { autoClose: false })
    
    // Redirect to homepage after 3 seconds
    setTimeout(() => {
      setDownloadProgress({ open: false, current: 0, total: 0, error: null, files: [] })
      toast.info('Redirecting to homepage...')
      setTimeout(() => {
        navigate('/')
      }, 1000)
    }, 3000)
  }

  const getStatusColor = (status) => {
    const colors = {
      draft: 'default',
      pending: 'warning',
      documents_uploaded: 'info',
      analyzing: 'warning',
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
            icon={storageUsed >= 5 ? <WarningIcon /> : <StorageIcon />}
          >
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Storage Usage: {storageUsed} / 15 documents ({((storageUsed / 15) * 100).toFixed(0)}%)
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(storageUsed / 15) * 100} 
                color={storageUsed >= 5 ? "warning" : "primary"}
                sx={{ height: 6, borderRadius: 1 }}
              />
              {storageUsed >= 5 && (
                <Typography variant="caption" color="warning.main" sx={{ mt: 0.5, display: 'block' }}>
                  {storageUsed === 5 ? '⚠️ 50% storage capacity reached' : '⚠️ High storage usage'}
                </Typography>
              )}
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
          {analysisResults && !isAnalyzing && (
            <Grid item xs={12}>
              <Grow in={true}>
                <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <CheckCircleIcon sx={{ fontSize: 48 }} />
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        Analysis Complete!
                      </Typography>
                      <Typography variant="body1" sx={{ opacity: 0.9 }}>
                        Documents successfully processed with high confidence
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.3)' }} />
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h2" sx={{ fontWeight: 700 }}>
                          {analysisResults.score}%
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          Extraction Score
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h2" sx={{ fontWeight: 700 }}>
                          {analysisResults.extracted}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          Documents Processed
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h2" sx={{ fontWeight: 700 }}>
                          {analysisResults.total}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          Total Required
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                  
                  <Button
                    variant="contained"
                    size="large"
                    fullWidth
                    onClick={() => setQuestionnaireOpen(true)}
                    sx={{ 
                      mt: 3, 
                      bgcolor: 'white', 
                      color: '#667eea',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' },
                      fontWeight: 600,
                      py: 1.5
                    }}
                  >
                    📋 Fill Questionnaire
                  </Button>
                </Paper>
              </Grow>
            </Grid>
          )}

          {/* Document Generation Section */}
          {showGenerateButton && (
            <Grid item xs={12}>
              <Grow in={true}>
                <Paper sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <DownloadIcon color="primary" sx={{ fontSize: 32 }} />
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Generate Visa Documents
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Create professional documents based on your analysis and responses
                      </Typography>
                    </Box>
                  </Box>
                  <Button
                    variant="contained"
                    color="secondary"
                    size="large"
                    onClick={handleGenerateDocuments}
                    disabled={downloadProgress.open}
                    startIcon={<DownloadIcon />}
                    sx={{ fontWeight: 600 }}
                  >
                    Generate & Download All Documents
                  </Button>
                </Paper>
              </Grow>
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
            You have reached 50% of your storage limit ({storageUsed}/15 documents).
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Please be mindful of storage usage. System may experience limitations.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowStorageWarning(false)} color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>

      {/* Download Progress Dialog */}
      <Dialog open={downloadProgress.open} onClose={() => {}} disableEscapeKeyDown maxWidth="sm" fullWidth>
        <DialogTitle sx={{ pb: 1 }}>
          {downloadProgress.error ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main' }}>
              <ErrorIcon />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Generation Failed
              </Typography>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={24} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Generating Documents...
              </Typography>
            </Box>
          )}
        </DialogTitle>
        <DialogContent>
          {downloadProgress.error ? (
            <Box>
              <Alert severity="error" sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                  {downloadProgress.error}
                </Typography>
                <Typography variant="caption">
                  Successfully generated {downloadProgress.current} of {downloadProgress.total} documents before failure.
                </Typography>
              </Alert>
              
              {downloadProgress.files.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    Generated Files:
                  </Typography>
                  <List dense>
                    {downloadProgress.files.map((file, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckCircleIcon color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={file} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          ) : (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Generating file {downloadProgress.current} of {downloadProgress.total}...
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(downloadProgress.current / downloadProgress.total) * 100} 
                sx={{ height: 10, borderRadius: 1, mb: 2 }}
              />
              
              {downloadProgress.files.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Generated files:
                  </Typography>
                  <List dense>
                    {downloadProgress.files.map((file, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <CheckCircleIcon color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={file} 
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setDownloadProgress({ open: false, current: 0, total: 0, error: null, files: [] })}
            color="primary"
            variant={downloadProgress.error ? "contained" : "outlined"}
          >
            {downloadProgress.error ? 'Close' : 'Cancel'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Questionnaire Dialog */}
      <QuestionnaireWizard
        open={questionnaireOpen}
        onClose={() => setQuestionnaireOpen(false)}
        applicationId={id}
        onComplete={handleQuestionnaireComplete}
      />
    </Container>
  )
}

// Document List Component with beautiful UI
const DocumentList = ({ requiredDocuments, uploadedDocuments, onUpload, onDelete, uploadingDocuments }) => {
  const getDocumentStatus = (docType) => {
    const isUploaded = uploadedDocuments.some(doc => doc.document_type === docType)
    const isUploading = uploadingDocuments[docType]
    
    if (isUploading) return 'uploading'
    if (isUploaded) return 'uploaded'
    return 'pending'
  }
  
  const getCategoryColor = (category) => {
    const colors = {
      identity: '#1976d2',
      application: '#9c27b0',
      travel: '#2e7d32',
      financial: '#ed6c02',
      assets: '#0288d1',
      support: '#d32f2f'
    }
    return colors[category] || '#757575'
  }

  const groupedDocuments = requiredDocuments.reduce((acc, doc) => {
    if (!acc[doc.category]) acc[doc.category] = []
    acc[doc.category].push(doc)
    return acc
  }, {})

  return (
    <Box>
      {Object.entries(groupedDocuments).map(([category, docs]) => (
        <Box key={category} sx={{ mb: 3 }}>
          <Typography 
            variant="subtitle1" 
            sx={{ 
              fontWeight: 600, 
              mb: 2,
              color: getCategoryColor(category),
              textTransform: 'capitalize',
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            <DescriptionIcon /> {category} Documents
          </Typography>
          
          <Grid container spacing={2}>
            {docs.map((doc) => {
              const status = getDocumentStatus(doc.document_type)
              const uploadingInfo = uploadingDocuments[doc.document_type]
              
              return (
                <Grid item xs={12} sm={6} md={4} key={doc.id}>
                  <Card 
                    sx={{ 
                      height: '100%',
                      border: 1,
                      borderColor: status === 'uploaded' ? 'success.main' : 
                                  status === 'uploading' ? 'warning.main' : 'divider',
                      boxShadow: status === 'uploaded' ? 2 : 0,
                      transition: 'all 0.3s',
                      '&:hover': {
                        boxShadow: 3,
                        transform: 'translateY(-2px)'
                      }
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, flex: 1 }}>
                          {doc.document_type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </Typography>
                        {doc.is_required && (
                          <Chip label="Required" size="small" color="error" sx={{ height: 20 }} />
                        )}
                      </Box>
                      
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2, minHeight: 32 }}>
                        {doc.description}
                      </Typography>
                      
                      {status === 'uploading' && uploadingInfo && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="caption" color="primary" sx={{ mb: 0.5, display: 'block' }}>
                            {uploadingInfo.status}
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={uploadingInfo.progress} 
                            sx={{ height: 6, borderRadius: 1 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {uploadingInfo.progress}%
                          </Typography>
                        </Box>
                      )}
                      
                      {status === 'uploaded' ? (
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                          <Chip 
                            icon={<CheckCircleIcon />}
                            label="Uploaded" 
                            color="success" 
                            size="small"
                            sx={{ flex: 1 }}
                          />
                          <Button
                            size="small"
                            color="error"
                            onClick={() => {
                              const doc = uploadedDocuments.find(d => d.document_type === doc.document_type)
                              if (doc) onDelete(doc)
                            }}
                          >
                            Delete
                          </Button>
                        </Box>
                      ) : status === 'uploading' ? (
                        <Button
                          variant="outlined"
                          size="small"
                          fullWidth
                          disabled
                          startIcon={<CircularProgress size={16} />}
                        >
                          Uploading...
                        </Button>
                      ) : (
                        <Button
                          variant="contained"
                          size="small"
                          fullWidth
                          startIcon={<CloudUploadIcon />}
                          onClick={() => onUpload(doc.document_type)}
                        >
                          Upload
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              )
            })}
          </Grid>
        </Box>
      ))}
    </Box>
  )
}

export default ApplicationDetailsPage
