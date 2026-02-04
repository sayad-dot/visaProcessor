import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  LinearProgress,
  Alert
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  InsertDriveFile as FileIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { documentService } from '../services/apiService';

/**
 * DocumentUploader Component
 * Drag-and-drop file uploader with validation and progress tracking
 */
const DocumentUploader = ({
  applicationId,
  documentType,
  onUploadSuccess,
  onUploadError,
  maxSize = 10 * 1024 * 1024, // 10MB default
  acceptedFileTypes = { 'application/pdf': ['.pdf'], 'image/*': ['.jpg', '.jpeg', '.png'] }
}) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analyzeProgress, setAnalyzeProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Handle file drop
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null);
    setSuccess(false);

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0].code === 'file-too-large') {
        setError(`File is too large. Maximum size is ${maxSize / (1024 * 1024)}MB`);
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        setError('Invalid file type. Please upload PDF or image files');
      } else {
        setError(rejection.errors[0].message);
      }
      return;
    }

    // Add accepted files
    if (acceptedFiles.length > 0) {
      setFiles(acceptedFiles);
    }
  }, [maxSize]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes,
    maxSize: maxSize,
    multiple: false // Single file upload
  });

  // Remove file
  const removeFile = () => {
    setFiles([]);
    setError(null);
    setSuccess(false);
    setUploading(false);
    setAnalyzing(false);
    setUploadProgress(0);
    setAnalyzeProgress(0);
  };

  // Upload file
  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setAnalyzing(false);
    setError(null);
    setSuccess(false);
    setUploadProgress(0);
    setAnalyzeProgress(0);

    try {
      const file = files[0];

      // Simulate upload progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const data = await documentService.uploadDocument(applicationId, documentType, file);

      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Show "Analyzing..." stage (hardcoded for professional UX)
      setUploading(false);
      setAnalyzing(true);
      
      // Generate random target between 90-100% for realistic variation
      const randomTarget = Math.floor(Math.random() * 11) + 90; // 90-100%
      
      // Simulate analysis progress with random increments
      const analyzeInterval = setInterval(() => {
        setAnalyzeProgress((prev) => {
          if (prev >= randomTarget) {
            clearInterval(analyzeInterval);
            return randomTarget;
          }
          // Random increment between 15-25% for natural feel
          const increment = Math.floor(Math.random() * 11) + 15;
          return Math.min(prev + increment, randomTarget);
        });
      }, 250);
      
      // Wait for analysis animation to complete (1.5-2 seconds random)
      const waitTime = Math.floor(Math.random() * 500) + 1500;
      await new Promise(resolve => setTimeout(resolve, waitTime));
      clearInterval(analyzeInterval);
      setAnalyzeProgress(randomTarget);
      
      setAnalyzing(false);
      setSuccess(true);

      // Clear files after successful upload
      setTimeout(() => {
        setFiles([]);
        setUploadProgress(0);
        setAnalyzeProgress(0);
        if (onUploadSuccess) {
          onUploadSuccess(data);
        }
      }, 1500);

    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to upload document');
      setAnalyzing(false);
      if (onUploadError) {
        onUploadError(err);
      }
    } finally {
      setUploading(false);
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    const mb = bytes / (1024 * 1024);
    if (mb < 1) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Dropzone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover'
          }
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop file here' : 'Drag & drop file here'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          or click to browse
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          Maximum file size: {maxSize / (1024 * 1024)}MB
        </Typography>
      </Paper>

      {/* Selected Files */}
      {files.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <List>
            {files.map((file, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  !uploading && !success && (
                    <IconButton edge="end" onClick={removeFile}>
                      <DeleteIcon />
                    </IconButton>
                  )
                }
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1
                }}
              >
                <ListItemIcon>
                  {success ? <CheckCircleIcon color="success" /> : <FileIcon />}
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={formatFileSize(file.size)}
                />
              </ListItem>
            ))}
          </List>

          {/* Upload Progress */}
          {uploading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} color="primary" />
              <Typography variant="caption" sx={{ mt: 0.5, display: 'block' }}>
                📤 Uploading: {uploadProgress}%
              </Typography>
            </Box>
          )}
          
          {/* Analyzing Progress */}
          {analyzing && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={analyzeProgress} color="success" />
              <Typography variant="caption" sx={{ mt: 0.5, display: 'block', color: 'success.main' }}>
                🔍 Analyzing document: {analyzeProgress}%
              </Typography>
            </Box>
          )}

          {/* Upload Button - Prominent */}
          {!uploading && !analyzing && !success && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <button
                onClick={handleUpload}
                style={{
                  padding: '16px 48px',
                  backgroundColor: '#1976d2',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
                  transition: 'all 0.3s ease',
                  letterSpacing: '0.5px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#1565c0';
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 6px 16px rgba(25, 118, 210, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#1976d2';
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 12px rgba(25, 118, 210, 0.3)';
                }}
              >
                📤 Upload Document
              </button>
            </Box>
          )}
        </Box>
      )}

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Success Message */}
      {success && (
        <Alert severity="success" sx={{ mt: 2 }}>
          ✅ Document uploaded and analyzed successfully!
        </Alert>
      )}
    </Box>
  );
};

export default DocumentUploader;
