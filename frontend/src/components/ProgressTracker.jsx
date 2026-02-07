import React from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Grid,
  Chip
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as UncheckIcon,
  HourglassEmpty as PendingIcon,
  CloudUpload as UploadIcon,
  AutoAwesome as AIIcon,
  Assignment as RequiredIcon,
  AddCircleOutline as OptionalIcon
} from '@mui/icons-material';

/**
 * ProgressTracker Component - Redesigned
 * Shows upload progress in 3 clear categories:
 * 1. Required Documents (3)
 * 2. Optional Documents (13)
 * 3. AI Will Generate (remaining)
 */
const ProgressTracker = ({
  requiredDocuments = [],
  uploadedDocuments = [],
  showDetails = true
}) => {
  // Get mandatory and optional document counts from requiredDocuments
  const mandatoryDocs = requiredDocuments.filter(doc => doc.is_mandatory === true);
  const optionalDocs = requiredDocuments.filter(doc => doc.is_mandatory === false);
  const aiGeneratableDocs = requiredDocuments.filter(doc => doc.can_be_generated === true);
  
  const mandatoryCount = mandatoryDocs.length; // Should be 2 (passport_copy, nid_bangla)
  const optionalMaxCount = optionalDocs.length; // Should be 12 for business, 13 for job
  const totalDocuments = requiredDocuments.length; // Should be 14 for business, 15 for job
  
  // Count uploaded documents by category
  const uploadedTypes = Array.isArray(uploadedDocuments) 
    ? uploadedDocuments.map(doc => doc.document_type?.toLowerCase() || '')
    : [];
  
  // Count uploaded mandatory documents
  const mandatoryUploaded = mandatoryDocs.filter(doc => 
    uploadedTypes.includes(doc.document_type?.toLowerCase() || '')
  ).length;
  
  // Count uploaded optional documents
  const optionalUploaded = optionalDocs.filter(doc => 
    uploadedTypes.includes(doc.document_type?.toLowerCase() || '')
  ).length;
  
  // Total uploaded and AI to generate
  const totalUploaded = uploadedDocuments.length;
  const willGenerate = Math.max(0, totalDocuments - totalUploaded);
  
  // Progress percentage for mandatory documents
  const mandatoryProgress = (mandatoryUploaded / mandatoryCount) * 100;
  const allMandatoryComplete = mandatoryUploaded === mandatoryCount;

  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        mb: 3,
        background: allMandatoryComplete 
          ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderRadius: 3,
        transition: 'all 0.5s ease'
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          📄 Document Status
        </Typography>
        <Chip
          icon={allMandatoryComplete ? <CheckCircleIcon /> : <PendingIcon />}
          label={allMandatoryComplete ? 'Ready to Analyze' : 'Upload in Progress'}
          sx={{
            backgroundColor: 'rgba(255, 255, 255, 0.25)',
            color: 'white',
            fontWeight: 600,
            fontSize: '0.85rem',
            '& .MuiChip-icon': { color: 'white' }
          }}
        />
      </Box>

      {/* 3-Row Statistics Grid */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {/* Row 1: Mandatory Documents */}
        <Grid item xs={12}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              borderRadius: 2,
              backdropFilter: 'blur(10px)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <RequiredIcon sx={{ fontSize: 28 }} />
              <Box>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  Required Documents
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  {mandatoryDocs.length === 2 ? 'Passport, NID Bangla' : 'Passport, NID, Bank Solvency'}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" sx={{ fontWeight: 800 }}>
                {mandatoryUploaded}/{mandatoryCount}
              </Typography>
              {allMandatoryComplete && (
                <CheckCircleIcon sx={{ fontSize: 28, color: '#90EE90' }} />
              )}
            </Box>
          </Box>
        </Grid>

        {/* Row 2: Optional Documents */}
        <Grid item xs={12}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: 2
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <OptionalIcon sx={{ fontSize: 28 }} />
              <Box>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  Optional Documents
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  {optionalMaxCount} documents (upload what you have)
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" sx={{ fontWeight: 800 }}>
                {optionalUploaded}/{optionalMaxCount}
              </Typography>
              {optionalUploaded > 0 && (
                <CheckCircleIcon sx={{ fontSize: 24, color: 'rgba(255,255,255,0.7)' }} />
              )}
            </Box>
          </Box>
        </Grid>

        {/* Row 3: AI Will Generate */}
        <Grid item xs={12}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              borderRadius: 2,
              border: '1px dashed rgba(255, 255, 255, 0.3)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <AIIcon sx={{ fontSize: 28, color: '#FFD700' }} />
              <Box>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  AI Will Generate
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  AI creates remaining {aiGeneratableDocs.length} docs from your data
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" sx={{ fontWeight: 800, color: '#FFD700' }}>
                {willGenerate}/{totalDocuments}
              </Typography>
              <AIIcon sx={{ fontSize: 24, color: '#FFD700' }} />
            </Box>
          </Box>
        </Grid>
      </Grid>

      {/* Progress Bar for Required Documents */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Required Documents Progress
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 700 }}>
            {Math.round(mandatoryProgress)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={mandatoryProgress}
          sx={{
            height: 10,
            borderRadius: 5,
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: allMandatoryComplete ? '#90EE90' : 'white',
              borderRadius: 5,
              transition: 'transform 0.5s ease'
            }
          }}
        />
      </Box>

      {/* Summary Message */}
      <Box
        sx={{
          p: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.15)',
          borderRadius: 2,
          textAlign: 'center'
        }}
      >
        {allMandatoryComplete ? (
          <>
            <CheckCircleIcon sx={{ fontSize: 36, mb: 1 }} />
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              ✅ All required documents uploaded!
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              Click "Analyze Documents" to extract information.
            </Typography>
          </>
        ) : (
          <>
            <UploadIcon sx={{ fontSize: 36, mb: 1 }} />
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              Please upload {mandatoryCount - mandatoryUploaded} more required document(s)
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              {!uploadedTypes.includes('passport_copy') && '• Passport Copy '}
              {!uploadedTypes.includes('nid_bangla') && '• NID (Bangla) '}
              {!uploadedTypes.includes('bank_solvency') && '• Bank Solvency'}
            </Typography>
          </>
        )}
      </Box>
    </Paper>
  );
};

export default ProgressTracker;
