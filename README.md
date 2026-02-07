# Azure Blob Storage File Transfer App

A Python application to transfer files from local storage to Azure Blob Storage, with Docker support for easy deployment.

## Features

- ✅ Upload individual files to Azure Blob Storage
- ✅ Upload entire directories recursively
- ✅ Download files from Azure Blob Storage
- ✅ List blobs in containers
- ✅ Docker containerization for easy deployment
- ✅ Comprehensive logging
- ✅ Error handling and retry logic
- ✅ Environment variable configuration

## Prerequisites

- Python 3.11+ (for local development)
- Docker & Docker Compose (for containerized deployment)
- Azure Storage Account with connection string
- Azure Blob Storage container

## Setup

### 1. Get Azure Storage Connection String

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Storage Account
3. Go to **Access keys** or **Connection string**
4. Copy your connection string

### 2. Clone and Configure

```bash
# Clone/download the project
cd PhotoSync

# Create .env file from template
cp .env.example .env

# Edit .env with your Azure credentials
# AZURE_STORAGE_CONNECTION_STRING=your_connection_string
# AZURE_CONTAINER_NAME=your_container_name
```

## Usage

### Option 1: Using Docker Compose (Recommended)

#### Upload a Directory
```bash
docker-compose run --rm file-transfer upload-dir --local-path /app/uploads --blob-prefix photos
```

#### Upload a Single File
```bash
docker-compose run --rm file-transfer upload-file --local-path /app/uploads/image.jpg --blob-name photos/image.jpg
```

#### List Blobs
```bash
docker-compose run --rm file-transfer list --blob-prefix photos
```

#### Download a File
```bash
docker-compose run --rm file-transfer download --blob-name photos/image.jpg --local-path /app/downloads/image.jpg
```

### Option 2: Using Docker Directly

#### Build the Image
```bash
docker build -t azure-file-transfer .
```

#### Run Container
```bash
docker run --rm \
  -e AZURE_STORAGE_CONNECTION_STRING="your_connection_string" \
  -e AZURE_CONTAINER_NAME="your_container" \
  -v $(pwd)/uploads:/app/uploads:ro \
  -v $(pwd)/downloads:/app/downloads:rw \
  -v $(pwd)/logs:/app/logs:rw \
  azure-file-transfer upload-dir --local-path /app/uploads
```

### Option 3: Local Python Execution

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run Application
```bash
# Set environment variables
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
export AZURE_CONTAINER_NAME="your_container"

# Upload directory
python app.py upload-dir --local-path ./uploads --blob-prefix photos

# Upload single file
python app.py upload-file --local-path ./uploads/image.jpg --blob-name photos/image.jpg

# List blobs
python app.py list --blob-prefix photos

# Download file
python app.py download --blob-name photos/image.jpg --local-path ./downloads/image.jpg
```

## Command Reference

### Commands

- **upload-file**: Upload a single file
- **upload-dir**: Upload entire directory
- **list**: List all blobs in container
- **download**: Download a file

### Arguments

- `--connection-string`: Azure Storage connection string (optional if env var set)
- `--container`: Azure container name (optional if env var set)
- `--local-path`: Path to local file or directory
- `--blob-name`: Name/path for blob in storage
- `--blob-prefix`: Prefix for organizing blobs (default: empty)

## Examples

### Example 1: Upload Photos to Azure

```bash
# Create uploads directory
mkdir -p uploads
cp /path/to/photos/* uploads/

# Set environment variables
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"
export AZURE_CONTAINER_NAME="photos"

# Upload all files
python app.py upload-dir --local-path uploads --blob-prefix 2024/february
```

### Example 2: Container Deployment
```bash
# Build image
docker build -t azure-uploader .

# Run with docker-compose
docker-compose up
```

## Directory Structure

```
PhotoSync/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Environment variables template
├── README.md            # This file
├── uploads/             # Local files to upload (create manually)
├── downloads/           # Downloaded files location
└── logs/                # Application logs
```

## Logging

All operations are logged to `logs/file_transfer.log` and console output.

Log levels:
- `INFO`: Normal operations
- `ERROR`: Failed operations
- `DEBUG`: Detailed debugging information

## Error Handling

The application handles:
- Missing files/directories
- Azure authentication failures
- Network errors
- File permission issues
- Container creation failures

## Security

- Never commit `.env` file with real credentials
- Use managed identities or key vault in production
- Restrict docker image access in registries
- Use read-only mounts for uploads directory

## Troubleshooting

### Connection String Error
```
Error: Failed to connect to Azure Storage
```
- Verify `AZURE_STORAGE_CONNECTION_STRING` is set correctly
- Check if connection string has expired

### Container Not Found
```
Error: ResourceNotFoundError
```
- Ensure `AZURE_CONTAINER_NAME` is correct
- Container will be created automatically if it doesn't exist

### Permission Denied
```
Error: File not found or permission denied
```
- Check file/directory permissions on local system
- Verify Docker volume mounts are correct

### Docker Issues
```bash
# View logs
docker-compose logs -f

# Rebuild image
docker-compose build --no-cache

# Clean up
docker-compose down -v
```

## Performance Tips

1. **Batch uploads**: Use `upload-dir` instead of multiple `upload-file` calls
2. **Blob naming**: Use hierarchical naming (e.g., `year/month/day/filename`)
3. **Container organization**: Group related files with naming prefixes
4. **Parallel uploads**: Consider using Azure SDK for parallel operations

## Advanced Configuration

### Using Managed Identity (Production)

Instead of connection string, use managed identity:
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

Modify `app.py` for your production needs.

## Support & License

For issues or questions, check Azure documentation:
- [Azure Storage Documentation](https://docs.microsoft.com/azure/storage/)
- [Azure SDK for Python](https://docs.microsoft.com/azure/developer/python/)
- [Docker Documentation](https://docs.docker.com/)

## Contributing

Feel free to modify and extend for your use case.

---

**Last Updated**: February 2026
