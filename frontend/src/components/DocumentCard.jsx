import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  CloudUpload as CloudUploadIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';

/**
 * DocumentCard Component
 * Displays individual document status with upload progress and actions
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

  // Get status icon and color
  const getStatusInfo = () => {
    if (uploadedDocument) {
      return {
        icon: <CheckCircleIcon />,
        color: 'success',
        label: 'Uploaded',
        bgColor: '#e8f5e9'
      };
    } else if (uploading) {
      return {
        icon: <CloudUploadIcon />,
        color: 'info',
        label: 'Uploading...',
        bgColor: '#e3f2fd'
      };
    } else if (requiredDocument?.can_be_generated) {
      // AI will generate this document - not required to upload
      return {
        icon: <DescriptionIcon />,
        color: 'default',
        label: 'AI Generated',
        bgColor: '#f5f5f5'
      };
    } else {
      // User must upload this document
      return {
        icon: <ErrorIcon />,
        color: 'warning',
        label: 'Required',
        bgColor: '#fff8e1'
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
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        backgroundColor: statusInfo.bgColor,
        border: uploadedDocument ? '2px solid #4caf50' : '1px solid #e0e0e0',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: 3,
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

      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        {/* Document Icon and Type */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <DescriptionIcon
            sx={{
              fontSize: 40,
              color: uploadedDocument ? 'success.main' : 'text.secondary',
              mr: 1.5
            }}
          />
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 600, fontSize: '1rem' }}>
              {formatDocumentType(documentType)}
            </Typography>
            <Chip
              icon={statusInfo.icon}
              label={statusInfo.label}
              color={statusInfo.color}
              size="small"
              sx={{ mt: 0.5 }}
            />
          </Box>
        </Box>

        {/* Document Description */}
        {requiredDocument && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {requiredDocument.description || 'Please upload this required document'}
          </Typography>
        )}

        {/* Uploaded File Info */}
        {uploadedDocument && (
          <Box
            sx={{
              mt: 2,
              p: 1.5,
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              borderRadius: 1,
              border: '1px solid #e0e0e0'
            }}
          >
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
              File: {uploadedDocument.document_name}
            </Typography>
            {uploadedDocument.file_size && (
              <Typography variant="caption" color="text.secondary">
                Size: {formatFileSize(uploadedDocument.file_size)}
              </Typography>
            )}
            {uploadedDocument.created_at && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                Uploaded: {new Date(uploadedDocument.created_at).toLocaleString()}
              </Typography>
            )}
          </Box>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2, gap: 1 }}>
          {uploadedDocument ? (
            <>
              <Tooltip title="View Document">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={() => onView && onView(uploadedDocument)}
                >
                  <VisibilityIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete Document">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => onDelete && onDelete(uploadedDocument)}
                  disabled={uploading}
                >
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
            </>
          ) : (
            <Tooltip title="Upload Document">
              <IconButton
                size="small"
                color="primary"
                onClick={() => onUpload && onUpload(documentType)}
                disabled={uploading}
              >
                <CloudUploadIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default DocumentCard;
