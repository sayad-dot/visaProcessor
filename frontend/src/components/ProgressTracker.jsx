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
  HourglassEmpty as PendingIcon
} from '@mui/icons-material';

/**
 * ProgressTracker Component
 * Shows overall upload progress and statistics
 */
const ProgressTracker = ({
  totalDocuments = 0,
  uploadedDocuments = 0,
  requiredDocuments = 0,
  showDetails = true
}) => {
  // Calculate progress percentage
  const progressPercentage = requiredDocuments > 0
    ? Math.round((uploadedDocuments / requiredDocuments) * 100)
    : 0;

  // Determine status
  const isComplete = uploadedDocuments === requiredDocuments && requiredDocuments > 0;
  const inProgress = uploadedDocuments > 0 && uploadedDocuments < requiredDocuments;

  // Get status color
  const getStatusColor = () => {
    if (isComplete) return 'success';
    if (inProgress) return 'warning';
    return 'default';
  };

  // Get status icon
  const getStatusIcon = () => {
    if (isComplete) return <CheckCircleIcon />;
    if (inProgress) return <PendingIcon />;
    return <UncheckIcon />;
  };

  // Get status text
  const getStatusText = () => {
    if (isComplete) return 'All Documents Uploaded';
    if (inProgress) return 'Upload In Progress';
    return 'No Documents Uploaded';
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        mb: 3,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          Upload Progress
        </Typography>
        <Chip
          icon={getStatusIcon()}
          label={getStatusText()}
          color={getStatusColor()}
          sx={{
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            color: 'white',
            fontWeight: 600,
            '& .MuiChip-icon': {
              color: 'white'
            }
          }}
        />
      </Box>

      {/* Progress Bar */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2">
            {uploadedDocuments} of {requiredDocuments} documents uploaded
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {progressPercentage}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={progressPercentage}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: 'rgba(255, 255, 255, 0.3)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: 'white',
              borderRadius: 4
            }
          }}
        />
      </Box>

      {/* Statistics */}
      {showDetails && (
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {requiredDocuments}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.9 }}>
                Required
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {uploadedDocuments}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.9 }}>
                Uploaded
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {requiredDocuments - uploadedDocuments}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.9 }}>
                Remaining
              </Typography>
            </Box>
          </Grid>
        </Grid>
      )}

      {/* Completion Message */}
      {isComplete && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            borderRadius: 1,
            textAlign: 'center'
          }}
        >
          <CheckCircleIcon sx={{ fontSize: 40, mb: 1 }} />
          <Typography variant="body1" sx={{ fontWeight: 600 }}>
            Great! All required documents have been uploaded.
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
            You can now proceed to analyze your documents.
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default ProgressTracker;
