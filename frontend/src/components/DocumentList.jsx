import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper
} from '@mui/material';
import DocumentCard from './DocumentCard';

/**
 * DocumentList Component
 * Displays a grid of document cards for all required documents
 */
const DocumentList = ({
  requiredDocuments = [],
  uploadedDocuments = [],
  onUpload,
  onDelete,
  onView,
  uploadingDocuments = {}
}) => {
  // Find uploaded document for a given type
  const findUploadedDocument = (documentType) => {
    return uploadedDocuments.find(
      doc => doc.document_type.toLowerCase() === documentType.toLowerCase()
    );
  };

  // Check if document is currently uploading
  const isDocumentUploading = (documentType) => {
    return uploadingDocuments[documentType] || false;
  };

  // Get upload progress for a document
  const getUploadProgress = (documentType) => {
    const uploadInfo = uploadingDocuments[documentType];
    return uploadInfo?.progress || 0;
  };

  if (!requiredDocuments || requiredDocuments.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No required documents found
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        Required Documents
      </Typography>
      
      {/* Minimal Column Layout */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {requiredDocuments.map((requiredDoc) => {
          const documentType = requiredDoc.document_type.toLowerCase();
          const uploadedDoc = findUploadedDocument(documentType);
          const isUploading = isDocumentUploading(documentType);
          const uploadProgress = getUploadProgress(documentType);

          return (
            <Box key={requiredDoc.id}>
              <DocumentCard
                documentType={documentType}
                requiredDocument={requiredDoc}
                uploadedDocument={uploadedDoc}
                onUpload={onUpload}
                onDelete={onDelete}
                onView={onView}
                uploading={isUploading}
                uploadProgress={uploadProgress}
              />
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

export default DocumentList;
