#!/usr/bin/env python3
"""
Azure Blob Storage File Transfer Application
Transfers files from local directory to Azure Blob Storage
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_transfer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AzureBlobUploader:
    """Handles file uploads to Azure Blob Storage"""
    
    def __init__(self, connection_string: str, container_name: str):
        """
        Initialize Azure Blob Storage uploader
        
        Args:
            connection_string: Azure Storage connection string
            container_name: Name of the blob container
        """
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
            self.container_name = container_name
            self.container_client = self.blob_service_client.get_container_client(
                container_name
            )
            logger.info(f"Connected to Azure Storage container: {container_name}")
        except AzureError as e:
            logger.error(f"Failed to connect to Azure Storage: {e}")
            raise
    
    def create_container_if_not_exists(self):
        """Create container if it doesn't already exist"""
        try:
            self.container_client.get_container_properties()
            logger.info(f"Container '{self.container_name}' already exists")
        except AzureError:
            try:
                self.blob_service_client.create_container(self.container_name)
                logger.info(f"Created container: {self.container_name}")
            except AzureError as e:
                logger.error(f"Failed to create container: {e}")
                raise
    
    def upload_file(self, local_file_path: str, blob_name: str = None):
        """
        Upload a single file to Azure Blob Storage
        
        Args:
            local_file_path: Path to local file
            blob_name: Name for the blob (optional, defaults to filename)
        
        Returns:
            bool: True if successful, False otherwise
        """
        local_path = Path(local_file_path)
        
        if not local_path.exists():
            logger.error(f"File not found: {local_file_path}")
            return False
        
        if not local_path.is_file():
            logger.error(f"Path is not a file: {local_file_path}")
            return False
        
        blob_name = blob_name or local_path.name
        
        try:
            with open(local_path, 'rb') as data:
                self.container_client.upload_blob(
                    name=blob_name,
                    data=data,
                    overwrite=True
                )
            file_size = local_path.stat().st_size
            logger.info(f"Successfully uploaded: {local_file_path} -> {blob_name} ({file_size} bytes)")
            return True
        except AzureError as e:
            logger.error(f"Failed to upload {local_file_path}: {e}")
            return False
    
    def upload_directory(self, local_dir_path: str, blob_prefix: str = ""):
        """
        Upload all files from a directory to Azure Blob Storage
        
        Args:
            local_dir_path: Path to local directory
            blob_prefix: Prefix for blobs (creates folder-like structure)
        
        Returns:
            dict: Statistics about the upload (success_count, failed_count, total_size)
        """
        local_dir = Path(local_dir_path)
        
        if not local_dir.exists():
            logger.error(f"Directory not found: {local_dir_path}")
            return None
        
        if not local_dir.is_dir():
            logger.error(f"Path is not a directory: {local_dir_path}")
            return None
        
        stats = {
            'success_count': 0,
            'failed_count': 0,
            'total_size': 0,
            'files': []
        }
        
        files = list(local_dir.glob('**/*'))
        logger.info(f"Found {len([f for f in files if f.is_file()])} files to upload in {local_dir_path}")
        
        for file_path in files:
            if file_path.is_file():
                # Create blob name with directory structure
                relative_path = file_path.relative_to(local_dir)
                blob_name = f"{blob_prefix}/{relative_path}".lstrip('/')
                
                if self.upload_file(str(file_path), blob_name):
                    stats['success_count'] += 1
                    stats['total_size'] += file_path.stat().st_size
                    stats['files'].append({
                        'local_path': str(file_path),
                        'blob_name': blob_name,
                        'size': file_path.stat().st_size
                    })
                else:
                    stats['failed_count'] += 1
        
        return stats
    
    def list_blobs(self, blob_prefix: str = ""):
        """
        List all blobs in the container
        
        Args:
            blob_prefix: Optional prefix to filter blobs
        """
        try:
            blobs = self.container_client.list_blobs(name_starts_with=blob_prefix)
            logger.info(f"Blobs in container '{self.container_name}':")
            for blob in blobs:
                logger.info(f"  - {blob.name} ({blob.size} bytes)")
        except AzureError as e:
            logger.error(f"Failed to list blobs: {e}")
    
    def download_file(self, blob_name: str, local_file_path: str):
        """
        Download a file from Azure Blob Storage
        
        Args:
            blob_name: Name of the blob
            local_file_path: Path to save the file locally
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            download_stream = blob_client.download_blob()
            
            Path(local_file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_file_path, 'wb') as file:
                file.write(download_stream.readall())
            
            logger.info(f"Successfully downloaded: {blob_name} -> {local_file_path}")
            return True
        except AzureError as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            return False


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='Transfer files to/from Azure Blob Storage'
    )
    parser.add_argument(
        'action',
        choices=['upload-file', 'upload-dir', 'list', 'download'],
        help='Action to perform'
    )
    parser.add_argument(
        '--connection-string',
        required=False,
        help='Azure Storage connection string'
    )
    parser.add_argument(
        '--container',
        required=False,
        help='Azure Blob Storage container name'
    )
    parser.add_argument(
        '--local-path',
        help='Local file or directory path'
    )
    parser.add_argument(
        '--blob-name',
        help='Blob name in storage'
    )
    parser.add_argument(
        '--blob-prefix',
        default='',
        help='Prefix for blobs (for directory uploads)'
    )
    
    args = parser.parse_args()
    
    # Get connection string from argument or environment variable
    connection_string = args.connection_string or os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        logger.error("Azure Storage connection string not provided")
        sys.exit(1)
    
    # Get container name from argument or environment variable
    container_name = args.container or os.getenv('AZURE_CONTAINER_NAME')
    if not container_name:
        logger.error("Azure Container name not provided")
        sys.exit(1)
    
    try:
        uploader = AzureBlobUploader(connection_string, container_name)
        uploader.create_container_if_not_exists()
        
        if args.action == 'upload-file':
            if not args.local_path:
                logger.error("--local-path is required for upload-file action")
                sys.exit(1)
            success = uploader.upload_file(args.local_path, args.blob_name)
            sys.exit(0 if success else 1)
        
        elif args.action == 'upload-dir':
            if not args.local_path:
                logger.error("--local-path is required for upload-dir action")
                sys.exit(1)
            stats = uploader.upload_directory(args.local_path, args.blob_prefix)
            logger.info(f"Upload complete: {stats['success_count']} succeeded, {stats['failed_count']} failed, {stats['total_size']} bytes total")
            sys.exit(0 if stats['failed_count'] == 0 else 1)
        
        elif args.action == 'list':
            uploader.list_blobs(args.blob_prefix)
        
        elif args.action == 'download':
            if not args.blob_name or not args.local_path:
                logger.error("--blob-name and --local-path are required for download action")
                sys.exit(1)
            success = uploader.download_file(args.blob_name, args.local_path)
            sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
