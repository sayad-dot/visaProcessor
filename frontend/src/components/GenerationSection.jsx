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
  FolderZip,
  AutoAwesome as AIIcon,
  HourglassEmpty,
  Download
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * GenerationSection Component - Enhanced
 * Beautiful visual progress per document
 */
const GenerationSection = ({ applicationId, applicantName = 'Applicant' }) => {
  const [status, setStatus] = useState('not_started');
  const [progress, setProgress] = useState(0);
  const [currentDocument, setCurrentDocument] = useState(null);
  const [documentsCompleted, setDocumentsCompleted] = useState(0);
  const [totalDocuments, setTotalDocuments] = useState(0); // Dynamic from backend
  const [completedDocuments, setCompletedDocuments] = useState([]);
  const [errors, setErrors] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  // All 16 document types for final ZIP
  const allDocumentTypes = [
    { key: 'passport_copy', name: 'Passport Copy', category: 'uploaded' },
    { key: 'visa_history', name: 'Visa History', category: 'uploaded' },
    { key: 'nid_english', name: 'NID English', category: 'generated' },
    { key: 'trade_license_english', name: 'Trade License (English)', category: 'generated' },
    { key: 'tin_certificate', name: 'TIN Certificate', category: 'uploaded' },
    { key: 'visiting_card', name: 'Visiting Card', category: 'generated' },
    { key: 'cover_letter', name: 'Cover Letter', category: 'generated' },
    { key: 'travel_itinerary', name: 'Travel Itinerary', category: 'generated' },
    { key: 'travel_history', name: 'Travel History', category: 'generated' },
    { key: 'air_ticket', name: 'Air Ticket Booking', category: 'uploaded' },
    { key: 'hotel_booking', name: 'Hotel Booking', category: 'uploaded' },
    { key: 'current_bank_statement', name: 'Current Account Statement', category: 'uploaded' },
    { key: 'current_bank_solvency', name: 'Current Account Solvency', category: 'uploaded' },
    { key: 'savings_bank_statement', name: 'Savings Account Statement', category: 'uploaded' },
    { key: 'savings_bank_solvency', name: 'Savings Account Solvency', category: 'uploaded' },
    { key: 'financial_statement', name: 'Financial Statement', category: 'generated' },
  ];

  // Document type display names for generation (ALL 13 AI-generatable documents)
  const docTypeNames = {
    cover_letter: 'Cover Letter',
    nid_english: 'NID English Translation',
    visiting_card: 'Visiting Card',
    financial_statement: 'Financial Statement',
    travel_itinerary: 'Travel Itinerary',
    travel_history: 'Travel History',
    home_tie_statement: 'Home Tie Statement',
    asset_valuation: 'Asset Valuation Certificate',
    tin_certificate: 'TIN Certificate',
    tax_certificate: 'Tax Certificate',
    trade_license: 'Trade License',
    hotel_booking: 'Hotel Booking',
    air_ticket: 'Air Ticket'
  };

  // Initial status check on component mount to get dynamic document count
  useEffect(() => {
    const fetchInitialStatus = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/generate/${applicationId}/status`
        );
        const data = response.data;
        setTotalDocuments(data.total_documents); // Get dynamic count on load
        if (data.status !== 'not_started') {
          setStatus(data.status);
          setProgress(data.progress);
          setDocumentsCompleted(data.documents_completed);
          setCompletedDocuments(data.completed_documents || []);
        }
      } catch (error) {
        console.error('Error fetching initial status:', error);
      }
    };
    
    fetchInitialStatus();
  }, [applicationId]);

  // Poll for status updates during generation
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
          setTotalDocuments(data.total_documents); // Get dynamic count from backend
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
      
      // Create download link with applicant name
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const fileName = applicantName.replace(/\s+/g, '_') || `Application_${applicationId}`;
      link.setAttribute('download', `${fileName}_Visa_Documents.zip`);
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
    <Paper 
      elevation={3} 
      sx={{ 
        p: 0, 
        mb: 4, 
        borderRadius: 3,
        overflow: 'hidden'
      }}
      data-section="generation"
    >
      {/* Header */}
      <Box
        sx={{
          p: 3,
          background: status === 'completed' 
            ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AIIcon sx={{ fontSize: 40 }} />
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              📄 AI Document Generation
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              {totalDocuments > 0 ? `Generate ${totalDocuments} professional documents with AI` : 'Loading document count...'}
            </Typography>
          </Box>
        </Box>
        
        {/* Stats */}
        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          <Chip
            icon={<CheckCircle />}
            label={`${documentsCompleted}/${totalDocuments} Generated`}
            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', '& .MuiChip-icon': { color: 'white' } }}
          />
          {status === 'completed' && (
            <Chip
              icon={<Download />}
              label="Ready to Download"
              sx={{ bgcolor: 'rgba(255,255,255,0.25)', color: 'white', '& .MuiChip-icon': { color: 'white' } }}
            />
          )}
        </Box>
      </Box>

      <Box sx={{ p: 3 }}>
        {/* Status Banner */}
        {status === 'not_started' && (
          <Alert 
            severity="info" 
            icon={<AIIcon />}
            sx={{ mb: 3, borderRadius: 2 }}
          >
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              Ready to generate {totalDocuments} professional visa documents using AI
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.5, opacity: 0.9 }}>
              All documents will be created based on your uploaded files and questionnaire responses.
            </Typography>
          </Alert>
        )}

        {status === 'generating' && (
          <Box sx={{ mb: 3 }}>
            {/* Progress bar */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  ✨ Generating: {currentDocument || 'Starting...'}
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 700 }}>
                  {progress}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ 
                  height: 12, 
                  borderRadius: 6,
                  bgcolor: 'rgba(102, 126, 234, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 6,
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                  }
                }} 
              />
            </Box>
          </Box>
        )}

        {status === 'completed' && (
          <Alert 
            severity="success" 
            icon={<CheckCircle />}
            sx={{ mb: 3, borderRadius: 2 }}
          >
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              ✅ All {documentsCompleted} documents generated successfully!
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.5 }}>
              Click the download button to get all documents in a ZIP file.
            </Typography>
          </Alert>
        )}

        {/* Document Generation List */}
        {(status === 'generating' || status === 'completed') && (
          <Card variant="outlined" sx={{ mb: 3, borderRadius: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Description color="primary" />
                Document Generation Progress
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={1}>
                {Object.keys(docTypeNames).map((docKey, index) => {
                  const isCompleted = completedDocuments.some(d => d.type === docKey);
                  const isCurrent = currentDocument === docTypeNames[docKey];
                  
                  return (
                    <Grid item xs={12} sm={6} key={docKey}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          p: 1.5,
                          borderRadius: 2,
                          bgcolor: isCompleted 
                            ? 'rgba(76, 175, 80, 0.1)' 
                            : isCurrent 
                              ? 'rgba(102, 126, 234, 0.1)'
                              : 'transparent',
                          border: '1px solid',
                          borderColor: isCompleted 
                            ? 'success.light' 
                            : isCurrent 
                              ? 'primary.light'
                              : 'divider',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        {isCompleted ? (
                          <CheckCircle color="success" />
                        ) : isCurrent ? (
                          <CircularProgress size={24} />
                        ) : (
                          <HourglassEmpty color="disabled" />
                        )}
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontWeight: isCompleted || isCurrent ? 600 : 400,
                            color: isCompleted ? 'success.dark' : isCurrent ? 'primary.dark' : 'text.secondary'
                          }}
                        >
                          {docTypeNames[docKey]}
                        </Typography>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          {status === 'not_started' && (
            <Button
              variant="contained"
              size="large"
              onClick={startGeneration}
              disabled={isGenerating}
              startIcon={<AIIcon />}
              sx={{
                px: 5,
                py: 1.5,
                fontSize: '1.1rem',
                textTransform: 'none',
                fontWeight: 700,
                borderRadius: 3,
                background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #5a6fd6 30%, #6a3f96 90%)',
                  boxShadow: '0 6px 20px rgba(102, 126, 234, 0.5)',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              🚀 Generate All Documents
            </Button>
          )}

          {status === 'completed' && (
            <Button
              variant="contained"
              size="large"
              onClick={downloadAllDocuments}
              disabled={isDownloading}
              startIcon={isDownloading ? <CircularProgress size={24} color="inherit" /> : <FolderZip />}
              sx={{
                px: 5,
                py: 1.5,
                fontSize: '1.1rem',
                textTransform: 'none',
                fontWeight: 700,
                borderRadius: 3,
                background: 'linear-gradient(45deg, #11998e 30%, #38ef7d 90%)',
                boxShadow: '0 4px 15px rgba(17, 153, 142, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #0e8377 30%, #2dd36f 90%)',
                  boxShadow: '0 6px 20px rgba(17, 153, 142, 0.5)',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              {isDownloading ? 'Preparing Download...' : `📦 Download All 16 Documents (ZIP)`}
            </Button>
          )}
        </Box>

        {/* Errors */}
        {errors.length > 0 && (
          <Alert severity="warning" sx={{ mt: 3, borderRadius: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              ⚠️ Some documents had issues:
            </Typography>
            {errors.map((error, index) => (
              <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                • {error}
              </Typography>
            ))}
          </Alert>
        )}

        {/* Info Cards for not_started state */}
        {status === 'not_started' && (
          <Grid container spacing={2} sx={{ mt: 3 }}>
            <Grid item xs={12} md={4}>
              <Card 
                variant="outlined" 
                sx={{ 
                  height: '100%', 
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)'
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
                    🤖 AI-Powered
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Uses Gemini 2.5 Flash for intelligent content generation based on your data
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card 
                variant="outlined" 
                sx={{ 
                  height: '100%', 
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, rgba(17, 153, 142, 0.05) 0%, rgba(56, 239, 125, 0.05) 100%)'
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ color: '#11998e', fontWeight: 600 }}>
                    ✅ Complete Set
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Generates all required documents for your Iceland visa application
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card 
                variant="outlined" 
                sx={{ 
                  height: '100%', 
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.05) 0%, rgba(255, 193, 7, 0.05) 100%)'
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ color: '#ff9800', fontWeight: 600 }}>
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
      </Box>
    </Paper>
  );
};

export default GenerationSection;
