import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Grid,
  Card,
  CardContent,
  IconButton,
  Collapse
} from '@mui/material';
import {
  Psychology as AnalyzeIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';
import { analysisService } from '../services/apiService';

/**
 * DEMO VERSION - AnalysisSection with Real Mock API
 */
const AnalysisSection = ({ applicationId, uploadedDocuments, onAnalysisComplete }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [error, setError] = useState(null);
  const [showResultDialog, setShowResultDialog] = useState(false);
  const [currentMessage, setCurrentMessage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  // Demo progress messages
  const progressMessages = [
    "🔍 Scanning uploaded documents...",
    "🤖 Extracting text and data...",
    "📊 Analyzing document quality...",
    "✨ Processing with AI...",
    "📋 Generating confidence scores...",
    "✅ Analysis complete!"
  ];

  // Mock analysis results
  const [demoResults, setDemoResults] = useState(null);

  const startAnalysis = async () => {
    if (uploadedDocuments.length === 0) {
      setError('Please upload at least one document before analysis');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setProgress(0);
    setCurrentMessage(0);

    // Progress messages
    const messageInterval = setInterval(() => {
      setCurrentMessage(prev => {
        if (prev < progressMessages.length - 1) {
          return prev + 1;
        }
        clearInterval(messageInterval);
        return prev;
      });
    }, 1000);

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 2;
      });
    }, 100);

    // Call mock API
    try {
      const results = await analysisService.analyzeDocuments(applicationId);
      setDemoResults(results);
      setAnalysisResults(results);
      setIsAnalyzing(false);
      setShowResultDialog(true);
    } catch (err) {
      setError('Analysis failed. Please try again.');
      setIsAnalyzing(false);
    }
  };

  const handleResultDialogClose = () => {
    setShowResultDialog(false);
    if (onAnalysisComplete) {
      onAnalysisComplete(analysisResults);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    if (score >= 50) return 'info';
    return 'error';
  };

  const getScoreMessage = (score) => {
    if (score >= 85) return { title: "Excellent!", message: "Your documents are of high quality and ready for processing." };
    if (score >= 70) return { title: "Good!", message: "Your documents are acceptable. Consider uploading additional documents for better results." };
    if (score >= 50) return { title: "Average", message: "Your documents need improvement. Please upload clearer scans or additional documents." };
    return { title: "Poor", message: "Your documents quality is below acceptable standards. Please re-upload with better quality." };
  };

  const ResultDialog = () => {
    const score = analysisResults?.overall_score || 0;
    const scoreInfo = getScoreMessage(score);
    const scoreColor = getScoreColor(score);

    return (
      <Dialog 
        open={showResultDialog} 
        onClose={handleResultDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{
          background: scoreColor === 'success' ? 'linear-gradient(135deg, #4caf50, #81c784)' :
                     scoreColor === 'warning' ? 'linear-gradient(135deg, #ff9800, #ffb74d)' :
                     scoreColor === 'info' ? 'linear-gradient(135deg, #2196f3, #64b5f6)' :
                     'linear-gradient(135deg, #f44336, #e57373)',
          color: 'white',
          textAlign: 'center'
        }}>
          <Box display="flex" alignItems="center" justifyContent="center" gap={2}>
            {scoreColor === 'success' && <CheckCircleIcon fontSize="large" />}
            {scoreColor === 'warning' && <WarningIcon fontSize="large" />}
            {scoreColor === 'error' && <ErrorIcon fontSize="large" />}
            <Typography variant="h5">{scoreInfo.title}</Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          {/* Score Display */}
          <Box textAlign="center" mb={3}>
            <Typography variant="h2" color={scoreColor === 'success' ? 'success.main' : 
                                           scoreColor === 'warning' ? 'warning.main' :
                                           scoreColor === 'info' ? 'info.main' : 'error.main'}>
              {score}%
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              {scoreInfo.message}
            </Typography>
          </Box>

          {/* Analysis Summary */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h4" color="primary">{analysisResults?.uploaded_documents || 0}</Typography>
                  <Typography variant="body2" color="textSecondary">Documents Processed</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h4" color="secondary">{16 - (analysisResults?.uploaded_documents || 0)}</Typography>
                  <Typography variant="body2" color="textSecondary">Documents Remaining</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Document Quality Details */}
          <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="h6">Document Quality Details</Typography>
              <IconButton onClick={() => setShowDetails(!showDetails)}>
                {showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            
            <Collapse in={showDetails}>
              <List dense>
                {Object.entries(analysisResults?.extracted_data || {}).map(([docType, data]) => (
                  <ListItem key={docType}>
                    <ListItemIcon>
                      {data.confidence >= 90 ? <CheckCircleIcon color="success" /> : 
                       data.confidence >= 70 ? <WarningIcon color="warning" /> : 
                       <ErrorIcon color="error" />}
                    </ListItemIcon>
                    <ListItemText 
                      primary={docType.replace(/_/g, ' ').toUpperCase()}
                      secondary={`${data.confidence}% confidence - ${data.status}`}
                    />
                    <Chip 
                      label={`${data.confidence}%`}
                      size="small"
                      color={data.confidence >= 90 ? 'success' : 
                             data.confidence >= 70 ? 'warning' : 'error'}
                    />
                  </ListItem>
                ))}
              </List>
            </Collapse>
          </Paper>

          {/* Issues and Recommendations */}
          {analysisResults?.issues?.length > 0 && (
            <Box mb={2}>
              <Typography variant="h6" gutterBottom>Issues Found:</Typography>
              {analysisResults.issues.map((issue, index) => (
                <Alert 
                  key={index} 
                  severity={issue.type} 
                  sx={{ mb: 1 }}
                >
                  {issue.message}
                </Alert>
              ))}
            </Box>
          )}

          {analysisResults?.recommendations?.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>Recommendations:</Typography>
              <List dense>
                {analysisResults.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <TrendingUpIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleResultDialogClose} variant="contained" size="large">
            Continue to Questionnaire
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <AIIcon color="primary" />
        AI Document Analysis
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!isAnalyzing && !analysisResults && (
        <Box>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Click the button below to analyze your uploaded documents with AI. 
            This will extract information and check document quality.
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            startIcon={<AnalyzeIcon />}
            onClick={startAnalysis}
            disabled={uploadedDocuments.length === 0}
            sx={{ minWidth: 200 }}
          >
            Analyze Documents
          </Button>
          
          {uploadedDocuments.length === 0 && (
            <Typography variant="caption" display="block" color="textSecondary" sx={{ mt: 1 }}>
              Upload at least one document to start analysis
            </Typography>
          )}
        </Box>
      )}

      {isAnalyzing && (
        <Box>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <CircularProgress size={24} />
            <Typography variant="body1">
              {progressMessages[currentMessage]}
            </Typography>
          </Box>
          
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
          
          <Typography variant="caption" display="block" sx={{ mt: 1, textAlign: 'center' }}>
            {Math.round(progress)}% complete
          </Typography>
        </Box>
      )}

      {analysisResults && !isAnalyzing && (
        <Box>
          <Alert severity="success" sx={{ mb: 2 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography>
                Analysis completed! Overall score: {analysisResults.overall_score}%
              </Typography>
              <Button 
                size="small" 
                onClick={() => setShowResultDialog(true)}
                variant="outlined"
              >
                View Details
              </Button>
            </Box>
          </Alert>

          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={() => {
                setAnalysisResults(null);
                setError(null);
              }}
            >
              Analyze Again
            </Button>
          </Box>
        </Box>
      )}

      <ResultDialog />
    </Paper>
  );
};

export default AnalysisSection;