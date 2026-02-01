import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  InsertDriveFile as FileIcon
} from '@mui/icons-material';

/**
 * Simple DocumentUploader for Demo
 * Just file selection, no actual upload
 */
const DocumentUploader = ({
  applicationId,
  documentType,
  onUploadSuccess,
  onUploadError,
  maxSize = 10 * 1024 * 1024,
  acceptedFileTypes = { 'application/pdf': ['.pdf'], 'image/*': ['.jpg', '.jpeg', '.png'] }
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null);

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

    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, [maxSize]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes,
    maxSize: maxSize,
    multiple: false
  });

  const handleUpload = () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    // Call success immediately for demo
    onUploadSuccess(selectedFile);
    setSelectedFile(null);
  };

  return (
    <Box>
      {/* Dropzone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          textAlign: 'center',
          mb: 2
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop file here' : 'Drag & drop or click to select'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          PDF or images (Max {maxSize / (1024 * 1024)}MB)
        </Typography>
      </Paper>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Selected File */}
      {selectedFile && (
        <Box sx={{ mb: 2 }}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <FileIcon color="primary" />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body1">{selectedFile.name}</Typography>
              <Typography variant="caption" color="text.secondary">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </Typography>
            </Box>
            <Button onClick={() => setSelectedFile(null)} size="small">
              Remove
            </Button>
          </Paper>
        </Box>
      )}

      {/* Upload Button */}
      <Button
        variant="contained"
        fullWidth
        onClick={handleUpload}
        disabled={!selectedFile}
        startIcon={<CloudUploadIcon />}
      >
        Upload Document
      </Button>
    </Box>
  );
};

export default DocumentUploader;
