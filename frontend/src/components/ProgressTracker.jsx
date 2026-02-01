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
  // Document type categorization
  const MANDATORY_TYPES = ['passport_copy', 'nid_bangla', 'bank_solvency'];
  const OPTIONAL_TYPES = [
    'visa_history', 'tin_certificate', 'income_tax_3years', 'hotel_booking',
    'air_ticket', 'trade_license', 'savings_account_statement', 'savings_account_solvency',
    'current_account_statement', 'current_account_solvency', 'asset_valuation',
    'nid_english', 'visiting_card'
  ];
  
  // Count uploaded documents by category
  const uploadedTypes = Array.isArray(uploadedDocuments) 
    ? uploadedDocuments.map(doc => doc.document_type?.toLowerCase() || '')
    : [];
  
  // Mandatory: 3 required
  const mandatoryCount = 3;
  const mandatoryUploaded = MANDATORY_TYPES.filter(type => 
    uploadedTypes.includes(type)
  ).length;
  
  // Optional: rest of uploads that aren't mandatory
  const optionalMaxCount = 13;
  const optionalUploaded = uploadedTypes.filter(type => 
    !MANDATORY_TYPES.includes(type)
  ).length;
  
  // Total documents for visa = 16
  const totalDocuments = 16;
  const totalUploaded = mandatoryUploaded + optionalUploaded;
  const willGenerate = totalDocuments - totalUploaded;
  
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
                  Passport, NID, Bank Solvency
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
                  TIN, Tax, Hotel, Air Ticket, etc.
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
                  Cover Letter, Itinerary, Statements
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
