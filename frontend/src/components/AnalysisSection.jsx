import React, { useState, useEffect } from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Button,
  Box,
  LinearProgress,
  Typography,
  Alert,
  Chip,
  CircularProgress,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Description as DescriptionIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Star as StarIcon,
  CloudUpload as UploadIcon,
  QuestionAnswer as QuestionIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';
import { documentService } from '../services/apiService';
import { API_BASE_URL } from '../config';

/**
 * AnalysisSection Component - Redesigned
 * Beautiful analysis with score-based results popup
 */
const AnalysisSection = ({ applicationId, onAnalysisComplete, onOpenQuestionnaire }) => {
  const [analysisStatus, setAnalysisStatus] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [polling, setPolling] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [showResultDialog, setShowResultDialog] = useState(false);
  const [worstDocuments, setWorstDocuments] = useState([]);
  const [questionnaireComplete, setQuestionnaireComplete] = useState(false);

  // Rotating messages during analysis
  const analysisMessages = [
    "🔍 Reading your passport details...",
    "📊 Analyzing bank statements...",
    "🆔 Extracting NID information...",
    "📝 Processing document content...",
    "🤖 AI is understanding your documents...",
    "✨ Almost done..."
  ];
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);

  // Check if analysis already exists
  useEffect(() => {
    checkExistingAnalysis();
  }, [applicationId]);

  // Rotate messages during analysis
  useEffect(() => {
    let messageInterval;
    if (isAnalyzing) {
      messageInterval = setInterval(() => {
        setCurrentMessageIndex((prev) => (prev + 1) % analysisMessages.length);
      }, 3000);
    }
    return () => {
      if (messageInterval) clearInterval(messageInterval);
    };
  }, [isAnalyzing]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (polling) {
        clearInterval(polling);
      }
    };
  }, [polling]);

  const checkExistingAnalysis = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/analysis/status/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysisStatus(data);

        // If completed, fetch results but DON'T auto-show popup
        // Popup will only show when user clicks analyze/re-analyze
        if (data.status === 'completed') {
          fetchAnalysisResults(false); // false = don't show popup
        }
        // If analyzing, start polling
        else if (data.status === 'analyzing' || data.status === 'started') {
          startPolling();
        }
      } else if (response.status === 404) {
        const errorData = await response.json();
        // Check if it's "No analysis session found" (normal) vs application not found (error)
        if (errorData.detail && errorData.detail.includes('Application not found')) {
          setError('Application not found. Please check the application ID.');
          console.error('Application not found:', applicationId);
        } else {
          // No analysis exists yet - reset to clean state
          setAnalysisStatus(null);
          setAnalysisResults(null);
        }
      }
    } catch (err) {
      // Network error or other issues - silently handle
      console.error('Error checking analysis status:', err);
    }
  };

  const startAnalysis = async () => {
    try {
      setError(null);
      setIsAnalyzing(true);

      const response = await fetch(`${API_BASE_URL}/analysis/start/${applicationId}`, {
        method: 'POST'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start analysis');
      }

      const data = await response.json();
      setAnalysisStatus(data);

      // Start polling for status updates
      startPolling();
    } catch (err) {
      setError(err.message);
      setIsAnalyzing(false);
    }
  };

  const startPolling = () => {
    // Clear existing polling
    if (polling) {
      clearInterval(polling);
    }

    // Poll every 2 seconds
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/analysis/status/${applicationId}`);
        if (response.ok) {
          const data = await response.json();
          setAnalysisStatus(data);

          // Stop polling if completed or failed
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
            setPolling(null);
            setIsAnalyzing(false);

            if (data.status === 'completed') {
              fetchAnalysisResults(true); // true = show popup
              if (onAnalysisComplete) {
                onAnalysisComplete(data);
              }
            } else if (data.status === 'failed') {
              setError('Analysis failed. Please try again.');
            }
          }
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 2000);

    setPolling(interval);
  };

  const fetchAnalysisResults = async (showPopup = true) => {
    try {
      const response = await fetch(`${API_BASE_URL}/analysis/results/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysisResults(data);
        
        // Check if questionnaire is already complete
        try {
          const questionnaireResponse = await fetch(`${API_BASE_URL}/questionnaire/responses/${applicationId}`);
          if (questionnaireResponse.ok) {
            const questionnaireData = await questionnaireResponse.json();
            if (questionnaireData && Object.keys(questionnaireData).length > 0) {
              setQuestionnaireComplete(true);
            }
          }
        } catch (error) {
          console.log('No questionnaire responses yet');
        }
        
        // Calculate worst performing documents
        if (data.extracted_data) {
          const docScores = Object.entries(data.extracted_data)
            .map(([docType, docData]) => ({
              docType: docType.replace(/_/g, ' ').toUpperCase(),
              confidence: docData.confidence || 0
            }))
            .sort((a, b) => a.confidence - b.confidence);
          
          // Get 2-3 worst documents
          const score = data.overall_completeness || data.completeness_score || 0;
          let worstCount = 2;
          if (score < 70) worstCount = 3;
          if (score < 50) worstCount = docScores.length;
          
          setWorstDocuments(docScores.slice(0, worstCount).filter(d => d.confidence < 85));
        }
        
        // Show result dialog only if requested
        if (showPopup) {
          setShowResultDialog(true);
        }
      }
    } catch (err) {
      console.error('Error fetching results:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'analyzing':
      case 'started': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  // Get score category info
  const getScoreInfo = (score) => {
    if (score >= 85) {
      return {
        level: 'excellent',
        title: '🎉 Excellent Analysis!',
        subtitle: 'Your documents were extracted with high accuracy.',
        color: '#4caf50',
        bgGradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        icon: <StarIcon sx={{ fontSize: 60, color: '#FFD700' }} />,
        suggestion: null
      };
    } else if (score >= 70) {
      return {
        level: 'good',
        title: '👍 Good Analysis',
        subtitle: 'Most information extracted successfully.',
        color: '#ff9800',
        bgGradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        icon: <CheckCircleIcon sx={{ fontSize: 60, color: 'white' }} />,
        suggestion: 'Consider re-uploading these documents with better quality for improved accuracy:'
      };
    } else if (score >= 50) {
      return {
        level: 'average',
        title: '⚠️ Average Analysis',
        subtitle: 'Some documents need better quality.',
        color: '#ff5722',
        bgGradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        icon: <WarningIcon sx={{ fontSize: 60, color: 'white' }} />,
        suggestion: 'Please re-upload these documents with better quality before proceeding:'
      };
    } else {
      return {
        level: 'poor',
        title: '❌ Poor Analysis',
        subtitle: 'Document quality is too low.',
        color: '#f44336',
        bgGradient: 'linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)',
        icon: <ErrorIcon sx={{ fontSize: 60, color: 'white' }} />,
        suggestion: 'Please re-upload ALL documents in clear PDF format and try again:'
      };
    }
  };

  const isComplete = analysisStatus?.status === 'completed';
  const isInProgress = analysisStatus?.status === 'analyzing' || analysisStatus?.status === 'started';
  const completenessScore = analysisStatus?.completeness_score || analysisResults?.overall_completeness || 0;
  const scoreInfo = getScoreInfo(completenessScore);

  return (
    <Card sx={{ mb: 3 }}>
      <CardHeader
        title="Document Analysis"
        avatar={<AnalyticsIcon color="primary" />}
        action={
          isComplete && (
            <IconButton onClick={() => setShowResults(!showResults)}>
              <ExpandMoreIcon sx={{ transform: showResults ? 'rotate(180deg)' : 'rotate(0deg)', transition: '0.3s' }} />
            </IconButton>
          )
        }
      />
      <CardContent>
        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Not Started */}
        {!analysisStatus && !isAnalyzing && (
          <Box>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              Start AI analysis to extract information from your uploaded documents.
              This will analyze all uploaded documents and extract structured data.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AnalyticsIcon />}
              onClick={startAnalysis}
              size="large"
            >
              Analyze Documents
            </Button>
          </Box>
        )}

        {/* In Progress - Beautiful Analysis UI */}
        {isInProgress && (
          <Box>
            {/* Animated Header */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 3,
                p: 2.5,
                borderRadius: 3,
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)',
                border: '1px solid rgba(102, 126, 234, 0.3)'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress
                  size={50}
                  thickness={4}
                  sx={{
                    mr: 2,
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    }
                  }}
                />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#1976d2' }}>
                    🔍 AI Analysis in Progress
                  </Typography>
                  <Typography 
                    variant="body1" 
                    color="text.secondary"
                    sx={{
                      animation: 'fadeInOut 3s ease-in-out infinite',
                      '@keyframes fadeInOut': {
                        '0%, 100%': { opacity: 0.5 },
                        '50%': { opacity: 1 },
                      }
                    }}
                  >
                    {analysisMessages[currentMessageIndex]}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="h3" sx={{ fontWeight: 800, color: '#1976d2', lineHeight: 1 }}>
                  {analysisStatus?.progress_percentage || 0}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {analysisStatus?.documents_analyzed || 0}/{analysisStatus?.total_documents || 0} docs
                </Typography>
              </Box>
            </Box>

            {/* Progress Bar with Animation */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Analyzing: {analysisStatus?.current_document || 'Starting...'}
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {analysisStatus?.documents_analyzed || 0} of {analysisStatus?.total_documents || 0}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={analysisStatus?.progress_percentage || 0}
                sx={{
                  height: 16,
                  borderRadius: 8,
                  bgcolor: 'rgba(25, 118, 210, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 8,
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                    boxShadow: '0 2px 10px rgba(102, 126, 234, 0.4)',
                    transition: 'transform 0.8s ease'
                  }
                }}
              />
            </Box>

            {/* Document Steps */}
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                bgcolor: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: 2
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 2, color: '#1e293b' }}>
                📋 Processing Queue:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {[...Array(analysisStatus?.total_documents || 3)].map((_, idx) => (
                  <Chip
                    key={idx}
                    size="small"
                    label={`Doc ${idx + 1}`}
                    color={
                      idx < (analysisStatus?.documents_analyzed || 0) 
                        ? 'success' 
                        : idx === (analysisStatus?.documents_analyzed || 0)
                          ? 'primary'
                          : 'default'
                    }
                    icon={
                      idx < (analysisStatus?.documents_analyzed || 0) 
                        ? <CheckCircleIcon /> 
                        : idx === (analysisStatus?.documents_analyzed || 0)
                          ? <CircularProgress size={12} color="inherit" />
                          : undefined
                    }
                    sx={{
                      transition: 'all 0.3s ease',
                      ...(idx === (analysisStatus?.documents_analyzed || 0) && {
                        animation: 'pulse 1.5s ease-in-out infinite',
                      })
                    }}
                  />
                ))}
              </Box>
            </Paper>

            {/* Info Message */}
            <Alert
              severity="info"
              icon={false}
              sx={{
                mt: 3,
                bgcolor: '#eff6ff',
                border: '1px solid #bfdbfe',
                '& .MuiAlert-message': { width: '100%' }
              }}
            >
              <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center' }}>
                <InfoIcon sx={{ mr: 1, fontSize: 20 }} />
                Please wait while our AI extracts names, dates, financial details, and travel information from your documents.
              </Typography>
            </Alert>
          </Box>
        )}

        {/* Completed */}
        {isComplete && (
          <Box>
            {/* Success Banner */}
            <Paper
              sx={{
                p: 3,
                mb: 2,
                background: scoreInfo.bgGradient,
                color: 'white',
                borderRadius: 3,
                textAlign: 'center'
              }}
            >
              {scoreInfo.icon}
              <Typography variant="h5" sx={{ fontWeight: 700, mt: 1 }}>
                {scoreInfo.title}
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9, mt: 0.5 }}>
                {scoreInfo.subtitle}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 2 }}>
                <Chip
                  label={`${completenessScore}% Extracted`}
                  sx={{
                    backgroundColor: 'rgba(255,255,255,0.25)',
                    color: 'white',
                    fontWeight: 700,
                    fontSize: '1rem',
                    height: 36
                  }}
                />
                <Chip
                  label={`${analysisStatus?.documents_analyzed || 0} Documents`}
                  sx={{
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    fontWeight: 600
                  }}
                />
              </Box>
            </Paper>

            {/* Suggestions for low scores */}
            {scoreInfo.suggestion && worstDocuments.length > 0 && (
              <Alert
                severity={scoreInfo.level === 'poor' ? 'error' : 'warning'}
                icon={<WarningIcon />}
                sx={{ mb: 2 }}
              >
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                  {scoreInfo.suggestion}
                </Typography>
                <Box sx={{ pl: 1 }}>
                  {worstDocuments.map((doc, idx) => (
                    <Typography key={idx} variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      • {doc.docType} ({doc.confidence}% confidence)
                    </Typography>
                  ))}
                </Box>
              </Alert>
            )}

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={startAnalysis}
                sx={{ borderRadius: 2 }}
              >
                Re-analyze
              </Button>
              {!questionnaireComplete ? (
                <Button
                  variant="contained"
                  startIcon={<QuestionIcon />}
                  onClick={() => {
                    if (onOpenQuestionnaire) {
                      onOpenQuestionnaire();
                    } else if (onAnalysisComplete) {
                      onAnalysisComplete(analysisResults);
                    }
                  }}
                  size="large"
                  sx={{
                    borderRadius: 2,
                    px: 4,
                    background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #5a6fd6 30%, #6a3f96 90%)',
                    }
                  }}
                >
                  Continue to Questionnaire
                </Button>
              ) : (
                <Button
                  variant="contained"
                  startIcon={<CheckCircleIcon />}
                  size="large"
                  disabled
                  sx={{
                    borderRadius: 2,
                    px: 4,
                    background: 'linear-gradient(45deg, #4caf50 30%, #45a049 90%)',
                  }}
                >
                  Questionnaire Completed ✓
                </Button>
              )}
            </Box>

            {/* Results Summary */}
            {analysisResults && (
              <Collapse in={showResults}>
                <Card variant="outlined" sx={{ mt: 2, bgcolor: 'grey.50' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📊 Extracted Information Summary
                    </Typography>
                    <List dense>
                      {Object.entries(analysisResults.extracted_data || {}).map(([docType, data]) => (
                        <ListItem key={docType}>
                          <ListItemIcon>
                            <DescriptionIcon 
                              color={(data.confidence || 0) >= 80 ? 'success' : (data.confidence || 0) >= 60 ? 'warning' : 'error'} 
                              fontSize="small" 
                            />
                          </ListItemIcon>
                          <ListItemText
                            primary={docType.replace(/_/g, ' ').toUpperCase()}
                            secondary={`Confidence: ${data.confidence || 0}%`}
                          />
                          <Chip
                            size="small"
                            label={`${data.confidence || 0}%`}
                            color={(data.confidence || 0) >= 80 ? 'success' : (data.confidence || 0) >= 60 ? 'warning' : 'error'}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Collapse>
            )}
          </Box>
        )}

        {/* Info Note */}
        {!isInProgress && !isComplete && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'info.50', borderRadius: 1, display: 'flex', alignItems: 'start' }}>
            <InfoIcon color="info" sx={{ mr: 1, mt: 0.5 }} fontSize="small" />
            <Typography variant="caption" color="text.secondary">
              The AI will extract information like names, dates, financial details, and travel plans from your documents.
              This process takes 1-2 minutes depending on document count.
            </Typography>
          </Box>
        )}
      </CardContent>

      {/* Analysis Result Dialog */}
      <Dialog
        open={showResultDialog}
        onClose={() => setShowResultDialog(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            overflow: 'hidden'
          }
        }}
      >
        <Box
          sx={{
            p: 4,
            background: scoreInfo.bgGradient,
            color: 'white',
            textAlign: 'center'
          }}
        >
          {scoreInfo.icon}
          <Typography variant="h4" sx={{ fontWeight: 700, mt: 2 }}>
            {scoreInfo.title}
          </Typography>
          <Typography variant="h2" sx={{ fontWeight: 800, my: 2 }}>
            {completenessScore}%
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9 }}>
            {scoreInfo.subtitle}
          </Typography>
        </Box>
        
        <DialogContent sx={{ pt: 3 }}>
          {scoreInfo.suggestion && worstDocuments.length > 0 && (
            <Alert 
              severity={scoreInfo.level === 'poor' ? 'error' : 'warning'}
              sx={{ mb: 2 }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                💡 {scoreInfo.suggestion}
              </Typography>
              {worstDocuments.map((doc, idx) => (
                <Typography key={idx} variant="body2">
                  • {doc.docType} ({doc.confidence}%)
                </Typography>
              ))}
            </Alert>
          )}
          
          <Typography variant="body1" sx={{ textAlign: 'center', color: 'text.secondary' }}>
            {questionnaireComplete
              ? '🎉 Perfect! Now generate the remaining documents using our system. Click the button below to proceed.'
              : scoreInfo.level === 'poor' 
                ? 'Re-upload your documents for better results before proceeding.'
                : 'Now let\'s gather some additional information to generate your visa documents!'
            }
          </Typography>
        </DialogContent>
        
        <DialogActions sx={{ p: 3, justifyContent: 'center', gap: 2 }}>
          {scoreInfo.level === 'poor' && (
            <Button 
              variant="outlined" 
              onClick={() => setShowResultDialog(false)}
              startIcon={<UploadIcon />}
            >
              Re-upload Documents
            </Button>
          )}
          {!questionnaireComplete ? (
            <Button
              variant="contained"
              onClick={() => {
                setShowResultDialog(false);
                if (onOpenQuestionnaire) {
                  onOpenQuestionnaire();
                } else if (onAnalysisComplete) {
                  onAnalysisComplete(analysisResults);
                }
              }}
              size="large"
              startIcon={<QuestionIcon />}
              sx={{
                px: 4,
                background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
              }}
            >
              Continue to Questionnaire
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={() => {
                setShowResultDialog(false);
                // Scroll to generation section
                setTimeout(() => {
                  const generationSection = document.querySelector('[data-section="generation"]');
                  if (generationSection) {
                    generationSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }
                }, 300);
              }}
              size="large"
              startIcon={<AIIcon />}
              sx={{
                px: 4,
                background: 'linear-gradient(45deg, #4caf50 30%, #45a049 90%)',
              }}
            >
              Generate Documents Now
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Analyzing Progress Dialog */}
      <Dialog
        open={isAnalyzing}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            overflow: 'hidden'
          }
        }}
      >
        {/* Animated Header */}
        <Box
          sx={{
            p: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            textAlign: 'center'
          }}
        >
          <CircularProgress 
            size={60} 
            thickness={4}
            sx={{ color: 'white', mb: 2 }}
          />
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
            🔍 Analyzing Your Documents
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            AI is extracting information from your files
          </Typography>
        </Box>

        <DialogContent sx={{ p: 3 }}>
          {/* Progress Bar */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Analysis Progress
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 700, color: 'primary.main' }}>
                {analysisStatus?.progress || 0}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={analysisStatus?.progress || 0}
              sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)'
                }
              }}
            />
          </Box>

          {/* Rotating Messages */}
          <Box
            sx={{
              p: 2,
              bgcolor: '#f5f5f5',
              borderRadius: 2,
              textAlign: 'center',
              minHeight: '60px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: 500,
                animation: 'fadeIn 0.5s ease-in-out'
              }}
            >
              {analysisMessages[currentMessageIndex]}
            </Typography>
          </Box>

          {/* Documents Status */}
          {analysisStatus?.documents_analyzed !== undefined && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                Documents Processed: {analysisStatus.documents_analyzed} / {analysisStatus.total_documents || 0}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {[...Array(analysisStatus.total_documents || 0)].map((_, idx) => (
                  <Chip
                    key={idx}
                    label={idx + 1}
                    size="small"
                    color={idx < analysisStatus.documents_analyzed ? 'success' : 'default'}
                    icon={idx < analysisStatus.documents_analyzed ? <CheckCircleIcon /> : undefined}
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Note */}
          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="body2">
              This usually takes 30-60 seconds. Please don't close this window.
            </Typography>
          </Alert>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export default AnalysisSection;
