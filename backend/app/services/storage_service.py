"""
Storage Service - File management utilities for uploaded documents
"""
import os
import uuid
import shutil
from typing import Optional, Tuple
from pathlib import Path
from loguru import logger

from app.config import settings


class StorageService:
    """Service for managing file storage operations"""
    
    def __init__(self):
        """Initialize storage service and ensure directories exist"""
        self.upload_dir = Path(settings.UPLOAD_FOLDER)
        self.generated_dir = Path(settings.GENERATED_FOLDER)
        
        # Ensure directories exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
    
    def save_file(
        self,
        file_content: bytes,
        original_filename: str,
        application_number: str,
        document_type: str
    ) -> Tuple[str, str]:
        """
        Save uploaded file to storage
        
        Args:
            file_content: Binary content of the file
            original_filename: Original name of the uploaded file
            application_number: Application number for organizing files
            document_type: Type of document (passport_copy, nid_bangla, etc.)
            
        Returns:
            Tuple of (file_path, unique_filename)
        """
        try:
            # Extract file extension
            file_extension = self._get_file_extension(original_filename)
            
            # Generate unique filename
            unique_id = uuid.uuid4().hex[:8]
            unique_filename = f"{application_number}_{document_type}_{unique_id}{file_extension}"
            
            # Full file path
            file_path = self.upload_dir / unique_filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"File saved: {unique_filename} ({len(file_content)} bytes)")
            
            return str(file_path), unique_filename
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def get_file_path(self, filename: str, is_generated: bool = False) -> str:
        """
        Get full path for a filename
        
        Args:
            filename: Name of the file
            is_generated: Whether file is in generated folder
            
        Returns:
            Full path to the file
        """
        base_dir = self.generated_dir if is_generated else self.upload_dir
        return str(base_dir / filename)
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes, 0 if file doesn't exist
        """
        try:
            if self.file_exists(file_path):
                return os.path.getsize(file_path)
            return 0
        except Exception as e:
            logger.error(f"Error getting file size: {str(e)}")
            return 0
    
    def validate_file_size(self, file_size: int) -> bool:
        """
        Validate file size against maximum allowed
        
        Args:
            file_size: Size in bytes
            
        Returns:
            True if valid, False otherwise
        """
        return file_size <= settings.MAX_FILE_SIZE
    
    def validate_file_extension(self, filename: str) -> bool:
        """
        Validate file extension against allowed types
        
        Args:
            filename: Name of the file
            
        Returns:
            True if valid extension, False otherwise
        """
        extension = self._get_file_extension(filename).lower().lstrip('.')
        return extension in settings.allowed_extensions_list
    
    def _get_file_extension(self, filename: str) -> str:
        """
        Extract file extension from filename
        
        Args:
            filename: Name of the file
            
        Returns:
            File extension including dot (e.g., '.pdf')
        """
        return os.path.splitext(filename)[1].lower()
    
    def get_storage_stats(self) -> dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        try:
            upload_files = list(self.upload_dir.glob('*'))
            generated_files = list(self.generated_dir.glob('*'))
            
            upload_size = sum(f.stat().st_size for f in upload_files if f.is_file())
            generated_size = sum(f.stat().st_size for f in generated_files if f.is_file())
            
            return {
                'upload_files_count': len([f for f in upload_files if f.is_file()]),
                'generated_files_count': len([f for f in generated_files if f.is_file()]),
                'upload_size_mb': round(upload_size / (1024 * 1024), 2),
                'generated_size_mb': round(generated_size / (1024 * 1024), 2),
                'total_size_mb': round((upload_size + generated_size) / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {}
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move file from source to destination
        
        Args:
            source_path: Current file path
            destination_path: New file path
            
        Returns:
            True if moved successfully, False otherwise
        """
        try:
            if self.file_exists(source_path):
                shutil.move(source_path, destination_path)
                logger.info(f"File moved from {source_path} to {destination_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error moving file: {str(e)}")
            return False
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy file from source to destination
        
        Args:
            source_path: Current file path
            destination_path: Destination file path
            
        Returns:
            True if copied successfully, False otherwise
        """
        try:
            if self.file_exists(source_path):
                shutil.copy2(source_path, destination_path)
                logger.info(f"File copied from {source_path} to {destination_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error copying file: {str(e)}")
            return False
