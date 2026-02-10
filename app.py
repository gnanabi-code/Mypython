#!/usr/bin/env python3
"""
Oracle Object Storage File Transfer Application
Transfers files from local directory to Oracle Cloud Infrastructure Object Storage
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import oci
from oci.object_storage import ObjectStorageClient
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


class OracleObjectStorageUploader:
    """Handles file uploads to Oracle Object Storage"""
    
    def __init__(self, config: dict, namespace: str, bucket_name: str):
        """
        Initialize Oracle Object Storage uploader
        
        Args:
            config: OCI configuration dictionary (from ~/.oci/config file)
            namespace: Oracle Cloud Object Storage namespace
            bucket_name: Name of the bucket
        """
        try:
            # Initialize OCI config
            oci_config = oci.config.from_file(
                file_location=config.get('config_file', os.path.expanduser('~/.oci/config')),
                profile_name=config.get('profile', 'DEFAULT')
            )
            
            self.object_storage_client = ObjectStorageClient(oci_config)
            self.namespace = namespace
            self.bucket_name = bucket_name
            
            # Verify connection by accessing bucket properties
            self.object_storage_client.get_bucket(
                namespace_name=namespace,
                bucket_name=bucket_name
            )
            logger.info(f"Connected to Oracle Object Storage bucket: {bucket_name} in namespace: {namespace}")
        except oci.exceptions.OciError as e:
            logger.error(f"Failed to connect to Oracle Object Storage: {e}")
            raise
    
    def upload_file(self, local_file_path: str, object_name: str = None):
        """
        Upload a single file to Oracle Object Storage
        
        Args:
            local_file_path: Path to local file
            object_name: Name for the object (optional, defaults to filename)
        
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
        
        object_name = object_name or local_path.name
        
        try:
            with open(local_path, 'rb') as file_content:
                self.object_storage_client.put_object(
                    namespace_name=self.namespace,
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    put_object_body=file_content
                )
            file_size = local_path.stat().st_size
            logger.info(f"Successfully uploaded: {local_file_path} -> {object_name} ({file_size} bytes)")
            return True
        except oci.exceptions.OciError as e:
            logger.error(f"Failed to upload {local_file_path}: {e}")
            return False
    
    def upload_directory(self, local_dir_path: str, object_prefix: str = ""):
        """
        Upload all files from a directory to Oracle Object Storage
        
        Args:
            local_dir_path: Path to local directory
            object_prefix: Prefix for objects (creates folder-like structure)
        
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
                # Create object name with directory structure
                relative_path = file_path.relative_to(local_dir)
                object_name = f"{object_prefix}/{relative_path}".lstrip('/').replace('\\', '/')
                
                if self.upload_file(str(file_path), object_name):
                    stats['success_count'] += 1
                    stats['total_size'] += file_path.stat().st_size
                    stats['files'].append({
                        'local_path': str(file_path),
                        'object_name': object_name,
                        'size': file_path.stat().st_size
                    })
                else:
                    stats['failed_count'] += 1
        
        return stats
    
    def list_objects(self, object_prefix: str = ""):
        """
        List all objects in the bucket
        
        Args:
            object_prefix: Optional prefix to filter objects
        """
        try:
            objects = self.object_storage_client.list_objects(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                prefix=object_prefix if object_prefix else None
            )
            logger.info(f"Objects in bucket '{self.bucket_name}':")
            for obj in objects.data.objects:
                logger.info(f"  - {obj.name} ({obj.size} bytes)")
        except oci.exceptions.OciError as e:
            logger.error(f"Failed to list objects: {e}")
    
    def download_file(self, object_name: str, local_file_path: str):
        """
        Download a file from Oracle Object Storage
        
        Args:
            object_name: Name of the object
            local_file_path: Path to save the file locally
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.object_storage_client.get_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            
            Path(local_file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_file_path, 'wb') as file:
                file.write(response.data.content)
            
            logger.info(f"Successfully downloaded: {object_name} -> {local_file_path}")
            return True
        except oci.exceptions.OciError as e:
            logger.error(f"Failed to download {object_name}: {e}")
            return False


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='Transfer files to/from Oracle Object Storage'
    )
    parser.add_argument(
        'action',
        choices=['upload-file', 'upload-dir', 'list', 'download'],
        help='Action to perform'
    )
    parser.add_argument(
        '--config-file',
        required=False,
        help='Path to OCI config file (default: ~/.oci/config)'
    )
    parser.add_argument(
        '--profile',
        required=False,
        default='DEFAULT',
        help='OCI config profile name (default: DEFAULT)'
    )
    parser.add_argument(
        '--namespace',
        required=False,
        help='Oracle Object Storage namespace'
    )
    parser.add_argument(
        '--bucket',
        required=False,
        help='Oracle Object Storage bucket name'
    )
    parser.add_argument(
        '--local-path',
        help='Local file or directory path'
    )
    parser.add_argument(
        '--object-name',
        help='Object name in storage'
    )
    parser.add_argument(
        '--object-prefix',
        default='',
        help='Prefix for objects (for directory uploads)'
    )
    
    args = parser.parse_args()
    
    # Get namespace from argument or environment variable
    namespace = args.namespace or os.getenv('OCI_NAMESPACE')
    if not namespace:
        logger.error("Oracle Object Storage namespace not provided")
        sys.exit(1)
    
    # Get bucket name from argument or environment variable
    bucket_name = args.bucket or os.getenv('OCI_BUCKET_NAME')
    if not bucket_name:
        logger.error("Oracle Object Storage bucket name not provided")
        sys.exit(1)
    
    try:
        config = {
            'config_file': args.config_file or os.path.expanduser('~/.oci/config'),
            'profile': args.profile
        }
        
        uploader = OracleObjectStorageUploader(config, namespace, bucket_name)
        
        if args.action == 'upload-file':
            if not args.local_path:
                logger.error("--local-path is required for upload-file action")
                sys.exit(1)
            success = uploader.upload_file(args.local_path, args.object_name)
            sys.exit(0 if success else 1)
        
        elif args.action == 'upload-dir':
            if not args.local_path:
                logger.error("--local-path is required for upload-dir action")
                sys.exit(1)
            stats = uploader.upload_directory(args.local_path, args.object_prefix)
            logger.info(f"Upload complete: {stats['success_count']} succeeded, {stats['failed_count']} failed, {stats['total_size']} bytes total")
            sys.exit(0 if stats['failed_count'] == 0 else 1)
        
        elif args.action == 'list':
            uploader.list_objects(args.object_prefix)
        
        elif args.action == 'download':
            if not args.object_name or not args.local_path:
                logger.error("--object-name and --local-path are required for download action")
                sys.exit(1)
            success = uploader.download_file(args.object_name, args.local_path)
            sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
