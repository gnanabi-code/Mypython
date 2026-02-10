# Oracle Object Storage File Transfer App

A Python application to transfer files from local storage to Oracle Cloud Infrastructure Object Storage, with Docker support for easy deployment.

## Features

- ✅ Upload individual files to Oracle Object Storage
- ✅ Upload entire directories recursively
- ✅ Download files from Oracle Object Storage
- ✅ List objects in buckets
- ✅ Docker containerization for easy deployment
- ✅ Comprehensive logging
- ✅ Error handling and retry logic
- ✅ Environment variable configuration

## Prerequisites

- Python 3.11+ (for local development)
- Docker & Docker Compose (for containerized deployment)
- Oracle Cloud Infrastructure account with Object Storage bucket
- OCI credentials configured locally (~/.oci/config)

## Setup

### 1. Get Oracle Cloud Credentials

1. Log in to [Oracle Cloud Console](https://www.oracle.com/cloud/sign-in/)
2. Navigate to **Users** in the top-right menu
3. Click your username and go to **User Settings**
4. Scroll down to **API Keys** and click **Add API Key**
5. A private key will be generated - download and save it to `~/.oci/`
6. Copy your **Namespace** from Object Storage service page
7. Create your Object Storage bucket in Oracle Cloud Console

### 2. Configure OCI Credentials Locally

```bash
# Create OCI config directory
mkdir -p ~/.oci

# Create config file and add your credentials
cat > ~/.oci/config << EOF
[DEFAULT]
user=ocid1.user.oc1...
fingerprint=your_fingerprint
key_file=~/.oci/your_private_key.pem
tenancy=ocid1.tenancy.oc1...
region=us-phoenix-1
EOF

# Set proper permissions
chmod 600 ~/.oci/config
chmod 600 ~/.oci/your_private_key.pem
```

### 3. Clone and Configure the App

```bash
# Clone/download the project
cd PhotoSync

# Create .env file from template
cp .env.example .env

# Edit .env with your Oracle credentials
# OCI_NAMESPACE=your_namespace
# OCI_BUCKET_NAME=your_bucket_name
```

## Usage

### Option 1: Using Docker Compose (Recommended)

#### Upload a Directory
```bash
docker-compose run --rm file-transfer upload-dir --local-path /app/uploads --object-prefix photos
```

#### Upload a Single File
```bash
docker-compose run --rm file-transfer upload-file --local-path /app/uploads/image.jpg --object-name photos/image.jpg
```

#### List Objects
```bash
docker-compose run --rm file-transfer list --object-prefix photos
```

#### Download a File
```bash
docker-compose run --rm file-transfer download --object-name photos/image.jpg --local-path /app/downloads/image.jpg
```

### Option 2: Using Docker Directly

#### Build the Image
```bash
docker build -t oci-file-transfer .
```

#### Run Container
```bash
docker run --rm \
  -e OCI_NAMESPACE="your_namespace" \
  -e OCI_BUCKET_NAME="your_bucket_name" \
  -v ~/.oci:/root/.oci:ro \
  -v $(pwd)/uploads:/app/uploads:ro \
  -v $(pwd)/downloads:/app/downloads:rw \
  -v $(pwd)/logs:/app/logs:rw \
  oci-file-transfer upload-dir --local-path /app/uploads
```

### Option 3: Local Python Execution

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run Application
```bash
# Set environment variables
export OCI_NAMESPACE="your_namespace"
export OCI_BUCKET_NAME="your_bucket_name"

# Upload directory
python app.py upload-dir --local-path ./uploads --object-prefix photos

# Upload single file
python app.py upload-file --local-path ./uploads/image.jpg --object-name photos/image.jpg

# List objects
python app.py list --object-prefix photos

# Download file
python app.py download --object-name photos/image.jpg --local-path ./downloads/image.jpg
```

## Command Reference

### Commands

- **upload-file**: Upload a single file
- **upload-dir**: Upload entire directory
- **list**: List all objects in bucket
- **download**: Download a file

### Arguments

- `--namespace`: Oracle Object Storage namespace (optional if env var set)
- `--bucket`: Oracle Object Storage bucket name (optional if env var set)
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
