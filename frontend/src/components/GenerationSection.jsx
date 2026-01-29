import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  CloudDownload,
  CheckCircle,
  Description,
  Autorenew,
  Error as ErrorIcon,
  FolderZip
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const GenerationSection = ({ applicationId }) => {
  const [status, setStatus] = useState('not_started');
  const [progress, setProgress] = useState(0);
  const [currentDocument, setCurrentDocument] = useState(null);
  const [documentsCompleted, setDocumentsCompleted] = useState(0);
  const [totalDocuments, setTotalDocuments] = useState(8);
  const [completedDocuments, setCompletedDocuments] = useState([]);
  const [errors, setErrors] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  // Document type display names
  const docTypeNames = {
    cover_letter: 'Cover Letter',
    nid_english: 'NID English Translation',
    visiting_card: 'Visiting Card',
    financial_statement: 'Financial Statement',
    travel_itinerary: 'Travel Itinerary',
    travel_history: 'Travel History',
    home_tie_statement: 'Home Tie Statement',
    asset_valuation: 'Asset Valuation Certificate'
  };

  // Poll for status updates
  useEffect(() => {
    let interval;
    
    if (isGenerating) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(
            `${API_BASE_URL}/generate/${applicationId}/status`
          );
          
          const data = response.data;
          setStatus(data.status);
          setProgress(data.progress);
          setCurrentDocument(data.current_document);
          setDocumentsCompleted(data.documents_completed);
          setCompletedDocuments(data.completed_documents || []);
          setErrors(data.errors || []);
          
          // Stop polling if completed or failed
          if (data.status === 'completed' || data.status === 'failed') {
            setIsGenerating(false);
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error fetching generation status:', error);
        }
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isGenerating, applicationId]);

  const startGeneration = async () => {
    try {
      setIsGenerating(true);
      setStatus('started');
      setProgress(0);
      setErrors([]);
      
      await axios.post(`${API_BASE_URL}/generate/${applicationId}/start`);
    } catch (error) {
      console.error('Error starting generation:', error);
      setIsGenerating(false);
      setErrors(['Failed to start generation. Please try again.']);
    }
  };

  const downloadAllDocuments = async () => {
    try {
      setIsDownloading(true);
      
      const response = await axios.get(
        `${API_BASE_URL}/generate/${applicationId}/download-all`,
        {
          responseType: 'blob'
        }
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Visa_Application_${applicationId}_All_Documents.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setIsDownloading(false);
    } catch (error) {
      console.error('Error downloading documents:', error);
      setIsDownloading(false);
      alert('Failed to download documents. Please try again.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        📄 AI Document Generation
      </Typography>

      {/* Status Banner */}
      {status === 'not_started' && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Ready to generate 8 professional visa documents using AI
          </Typography>
          <Typography variant="body2" sx={{ mt: 1, opacity: 0.8 }}>
            All documents will be created based on your uploaded files and questionnaire responses.
          </Typography>
        </Alert>
      )}

      {status === 'generating' && (
        <Alert severity="info" icon={<Autorenew className="rotating-icon" />} sx={{ mb: 3 }}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            {currentDocument ? `Generating: ${currentDocument}...` : 'Generating documents...'}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {documentsCompleted} of {totalDocuments} documents completed
          </Typography>
        </Alert>
      )}

      {status === 'completed' && (
        <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 3 }}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            ✅ All documents generated successfully!
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {completedDocuments.length} documents ready for download
          </Typography>
        </Alert>
      )}

      {status === 'failed' && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Generation failed. Please try again.
          </Typography>
        </Alert>
      )}

      {/* Progress Bar */}
      {(status === 'generating' || status === 'completed') && (
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Generation Progress
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600 }}>
              {progress}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ 
              height: 10, 
              borderRadius: 5,
              backgroundColor: 'rgba(0, 123, 255, 0.1)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 5,
                backgroundColor: status === 'completed' ? '#4caf50' : '#007bff'
              }
            }} 
          />
        </Box>
      )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        {status === 'not_started' && (
          <Button
            variant="contained"
            size="large"
            onClick={startGeneration}
            disabled={isGenerating}
            startIcon={<Description />}
            sx={{
              px: 4,
              py: 1.5,
              fontSize: '1rem',
              textTransform: 'none',
              fontWeight: 600,
              background: 'linear-gradient(45deg, #007bff 30%, #0056b3 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #0056b3 30%, #003d82 90%)',
              }
            }}
          >
            Generate All Documents
          </Button>
        )}

        {status === 'completed' && (
          <Button
            variant="contained"
            size="large"
            onClick={downloadAllDocuments}
            disabled={isDownloading}
            startIcon={isDownloading ? <CircularProgress size={20} color="inherit" /> : <FolderZip />}
            sx={{
              px: 4,
              py: 1.5,
              fontSize: '1rem',
              textTransform: 'none',
              fontWeight: 600,
              background: 'linear-gradient(45deg, #28a745 30%, #1e7e34 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #1e7e34 30%, #155724 90%)',
              }
            }}
          >
            {isDownloading ? 'Preparing Download...' : 'Download All Documents (ZIP)'}
          </Button>
        )}
      </Box>

      {/* Completed Documents List */}
      {completedDocuments.length > 0 && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle color="success" />
              Completed Documents
            </Typography>
            <Divider sx={{ my: 2 }} />
            <List dense>
              {completedDocuments.map((doc, index) => (
                <ListItem key={index} sx={{ py: 1 }}>
                  <ListItemIcon>
                    <Description color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {doc.name}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="body2" color="text.secondary">
                        {formatFileSize(doc.size)}
                      </Typography>
                    }
                  />
                  <Chip
                    label="Completed"
                    color="success"
                    size="small"
                    icon={<CheckCircle />}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Errors */}
      {errors.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
            Some documents had issues:
          </Typography>
          {errors.map((error, index) => (
            <Typography key={index} variant="body2" sx={{ ml: 2 }}>
              • {error}
            </Typography>
          ))}
        </Alert>
      )}

      {/* Info Cards */}
      {status === 'not_started' && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card variant="outlined" sx={{ height: '100%', backgroundColor: 'rgba(0, 123, 255, 0.05)' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  🤖 AI-Powered
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Uses Gemini 2.5 Flash for intelligent content generation based on your data
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card variant="outlined" sx={{ height: '100%', backgroundColor: 'rgba(40, 167, 69, 0.05)' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="success">
                  ✅ Complete Set
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Generates all 8 required documents for your Iceland visa application
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card variant="outlined" sx={{ height: '100%', backgroundColor: 'rgba(255, 193, 7, 0.05)' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: '#ff9800' }}>
                  📦 Easy Download
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Download all 16 documents (uploaded + generated) in one ZIP file
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* CSS for rotating icon */}
      <style>
        {`
          @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          .rotating-icon {
            animation: rotate 2s linear infinite;
          }
        `}
      </style>
    </Paper>
  );
};

export default GenerationSection;
