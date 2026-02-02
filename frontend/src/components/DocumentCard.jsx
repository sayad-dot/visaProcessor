import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  LinearProgress,
  Tooltip,
  Button
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  CloudUpload as CloudUploadIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Description as DescriptionIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';

/**
 * DocumentCard Component - Redesigned
 * Displays individual document with prominent upload button
 */
const DocumentCard = ({
  documentType,
  requiredDocument,
  uploadedDocument = null,
  onUpload,
  onDelete,
  onView,
  uploading = false,
  uploadProgress = 0
}) => {
  // Format document type for display
  const formatDocumentType = (type) => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Get status info
  const getStatusInfo = () => {
    if (uploadedDocument) {
      return {
        icon: <CheckCircleIcon />,
        color: 'success',
        label: 'Uploaded',
        bgColor: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
        borderColor: '#4caf50'
      };
    } else if (uploading) {
      return {
        icon: <CloudUploadIcon />,
        color: 'info',
        label: 'Uploading...',
        bgColor: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
        borderColor: '#2196f3'
      };
    } else if (requiredDocument?.is_mandatory) {
      return {
        icon: <ErrorIcon />,
        color: 'error',
        label: 'Required',
        bgColor: 'linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)',
        borderColor: '#f44336'
      };
    } else {
      return {
        icon: <CloudUploadIcon />,
        color: 'info',
        label: 'Optional',
        bgColor: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)',
        borderColor: '#ff9800'
      };
    }
  };

  const statusInfo = getStatusInfo();

  // Format file size
  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <Card
      sx={{
        display: 'flex',
        alignItems: 'stretch',
        position: 'relative',
        background: statusInfo.bgColor,
        border: `2px solid ${statusInfo.borderColor}`,
        borderRadius: 2,
        transition: 'all 0.3s ease',
        overflow: 'hidden',
        '&:hover': {
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          transform: 'translateY(-2px)'
        }
      }}
    >
      {/* Upload Progress Bar */}
      {uploading && (
        <LinearProgress
          variant="determinate"
          value={uploadProgress}
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4
          }}
        />
      )}

      {/* Left Section - Document Info */}
      <CardContent sx={{ flexGrow: 1, p: 2, display: 'flex', alignItems: 'center' }}>
        {/* Icon */}
        <Box
          sx={{
            width: 50,
            height: 50,
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255,255,255,0.7)',
            mr: 2,
            flexShrink: 0
          }}
        >
          <DescriptionIcon
            sx={{
              fontSize: 30,
              color: uploadedDocument ? 'success.main' : 'text.secondary'
            }}
          />
        </Box>

        {/* Document Name & Status */}
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 600, 
                fontSize: '1rem',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {formatDocumentType(documentType)}
            </Typography>
            <Chip
              icon={statusInfo.icon}
              label={statusInfo.label}
              color={statusInfo.color}
              size="small"
              sx={{ height: 24, fontSize: '0.7rem' }}
            />
          </Box>
          
          {/* Description or File Info */}
          {uploadedDocument ? (
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
              📎 {uploadedDocument.document_name} • {formatFileSize(uploadedDocument.file_size)}
            </Typography>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
              {requiredDocument?.description?.substring(0, 60) || 'Upload this document'}
              {requiredDocument?.description?.length > 60 ? '...' : ''}
            </Typography>
          )}
        </Box>
      </CardContent>

      {/* Right Section - Actions */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          px: 2,
          backgroundColor: 'rgba(255,255,255,0.3)',
          borderLeft: '1px solid rgba(0,0,0,0.1)'
        }}
      >
        {uploadedDocument ? (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="View Document">
              <IconButton
                color="primary"
                onClick={() => onView && onView(uploadedDocument)}
                sx={{
                  backgroundColor: 'rgba(25, 118, 210, 0.1)',
                  '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.2)' }
                }}
              >
                <VisibilityIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Document">
              <IconButton
                color="error"
                onClick={() => onDelete && onDelete(uploadedDocument)}
                disabled={uploading}
                sx={{
                  backgroundColor: 'rgba(244, 67, 54, 0.1)',
                  '&:hover': { backgroundColor: 'rgba(244, 67, 54, 0.2)' }
                }}
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 0.5 }}>
            <Button
              variant="contained"
              color={requiredDocument?.is_mandatory ? "error" : "primary"}
              size="large"
              startIcon={<CloudUploadIcon />}
              onClick={() => onUpload && onUpload(documentType)}
              disabled={uploading}
              sx={{
                minWidth: 140,
                height: 48,
                fontWeight: 600,
                fontSize: '0.9rem',
                borderRadius: 2,
                textTransform: 'none',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                '&:hover': {
                  boxShadow: '0 4px 12px rgba(0,0,0,0.25)',
                  transform: 'scale(1.02)'
                }
              }}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </Button>
            {requiredDocument?.can_be_generated && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <AIIcon sx={{ fontSize: 14, color: '#7b1fa2' }} />
                <Typography variant="caption" sx={{ color: '#7b1fa2', fontWeight: 500 }}>
                  or AI generates
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Card>
  );
};

export default DocumentCard;
