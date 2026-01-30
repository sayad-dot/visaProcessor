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
  Paper
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Description as DescriptionIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { documentService } from '../services/apiService';

/**
 * AnalysisSection Component
 * Handles document analysis - start, progress tracking, and results display
 */
const AnalysisSection = ({ applicationId, onAnalysisComplete }) => {
  const [analysisStatus, setAnalysisStatus] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [polling, setPolling] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);

  // Check if analysis already exists
  useEffect(() => {
    checkExistingAnalysis();
  }, [applicationId]);

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
      const response = await fetch(`http://localhost:8000/api/analysis/status/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysisStatus(data);

        // If completed, fetch results
        if (data.status === 'completed') {
          fetchAnalysisResults();
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
        }
        // Otherwise, silently handle - no analysis exists yet (this is normal)
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

      const response = await fetch(`http://localhost:8000/api/analysis/start/${applicationId}`, {
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
        const response = await fetch(`http://localhost:8000/api/analysis/status/${applicationId}`);
        if (response.ok) {
          const data = await response.json();
          setAnalysisStatus(data);

          // Stop polling if completed or failed
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
            setPolling(null);
            setIsAnalyzing(false);

            if (data.status === 'completed') {
              fetchAnalysisResults();
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

  const fetchAnalysisResults = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/analysis/results/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysisResults(data);
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

  const isComplete = analysisStatus?.status === 'completed';
  const isInProgress = analysisStatus?.status === 'analyzing' || analysisStatus?.status === 'started';

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
                p: 2,
                bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: 2,
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress
                  size={40}
                  thickness={4}
                  sx={{
                    mr: 2,
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    }
                  }}
                />
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
                    🔍 AI Analysis in Progress
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Extracting information from your documents...
                  </Typography>
                </Box>
              </Box>
              <Chip
                label={`${analysisStatus?.progress_percentage || 0}%`}
                color="primary"
                sx={{
                  fontSize: '16px',
                  fontWeight: 700,
                  height: 40,
                  px: 2
                }}
              />
            </Box>

            {/* Progress Bar with Animation */}
            <Box sx={{ mb: 3 }}>
              <LinearProgress
                variant="determinate"
                value={analysisStatus?.progress_percentage || 0}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  bgcolor: 'rgba(25, 118, 210, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 6,
                    background: 'linear-gradient(90deg, #1976d2 0%, #2196f3 100%)',
                    boxShadow: '0 2px 8px rgba(25, 118, 210, 0.3)'
                  }
                }}
              />
            </Box>

            {/* Current Document Info */}
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                bgcolor: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: 2
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: '#10b981',
                    mr: 1,
                    animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                    '@keyframes pulse': {
                      '0%, 100%': {
                        opacity: 1,
                      },
                      '50%': {
                        opacity: 0.5,
                      },
                    },
                  }}
                />
                <Typography variant="body1" sx={{ fontWeight: 600, color: '#1e293b' }}>
                  Currently Processing
                </Typography>
              </Box>
              <Typography variant="body1" color="primary" sx={{ fontWeight: 500, mb: 1 }}>
                📄 {analysisStatus.current_document || 'Starting analysis...'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ✅ {analysisStatus.documents_analyzed} of {analysisStatus.total_documents} documents analyzed
              </Typography>
            </Paper>

            {/* Info Message */}
            <Alert
              severity="info"
              icon={false}
              sx={{
                mt: 3,
                bgcolor: '#eff6ff',
                border: '1px solid #bfdbfe',
                '& .MuiAlert-message': {
                  width: '100%'
                }
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
            <Alert severity="success" sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CheckCircleIcon sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    Analysis Complete! {analysisStatus.completeness_score}% information extracted
                  </Typography>
                </Box>
                <Button
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={startAnalysis}
                >
                  Re-analyze
                </Button>
              </Box>
            </Alert>

            {/* Results Summary */}
            {analysisResults && (
              <Collapse in={showResults}>
                <Card variant="outlined" sx={{ mt: 2, bgcolor: 'grey.50' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Extracted Information Summary
                    </Typography>
                    <List dense>
                      {Object.entries(analysisResults.extracted_data || {}).map(([docType, data]) => (
                        <ListItem key={docType}>
                          <ListItemIcon>
                            <DescriptionIcon color="primary" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText
                            primary={docType.replace(/_/g, ' ').toUpperCase()}
                            secondary={`Confidence: ${data.confidence || 0}%`}
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
        {!isInProgress && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'info.50', borderRadius: 1, display: 'flex', alignItems: 'start' }}>
            <InfoIcon color="info" sx={{ mr: 1, mt: 0.5 }} fontSize="small" />
            <Typography variant="caption" color="text.secondary">
              The AI will extract information like names, dates, financial details, and travel plans from your documents.
              This process takes 1-2 minutes depending on document count.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AnalysisSection;
