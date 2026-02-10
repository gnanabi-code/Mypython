# Quick Setup & Installation Guide

## Prerequisites Installation

### Step 1: Install Python (if not already installed)

**Windows:**
- Download from: https://www.python.org/downloads/
- Or install via Chocolatey: `choco install python`
- Or Windows Package Manager: `winget install Python.Python.3.11`

**Verify installation:**
```powershell
python --version
pip --version
```

### Step 2: Install Docker Desktop (for containerized deployment)

**Windows:**
- Download Docker Desktop: https://www.docker.com/products/docker-desktop
- Install and enable WSL 2 backend
- Verify: `docker --version`

### Step 3: Set Up Oracle Cloud Credentials

1. Go to Oracle Cloud Console: https://www.oracle.com/cloud/sign-in/
2. Navigate to your user settings (top-right menu)
3. Go to **API Keys** and generate a new key
4. Download the private key file and save to `~/.oci/`
5. Create `~/.oci/config` file with your credentials:

```ini
[DEFAULT]
user=ocid1.user.oc1.xxxxxxxx
fingerprint=ab:cd:ef:12:34:56:78:90:ab:cd:ef:12:34:56:78:90
key_file=~/.oci/your_private_key.pem
tenancy=ocid1.tenancy.oc1.xxxxxxxx
region=us-phoenix-1
```

6. Get your **Namespace** from Oracle Cloud Console (Object Storage > Buckets > your namespace)
7. Edit `.env` file:
```
OCI_NAMESPACE=your_namespace_here
OCI_BUCKET_NAME=your_bucket_name_here
```

## Running the Application

### Option A: Local Python (Recommended for development)

```powershell
# Navigate to project directory
cd PhotoSync

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py --help

# Example: Upload directory
python app.py upload-dir --local-path ./uploads --object-prefix photos/2024

# Example: List files
python app.py list --object-prefix photos
```

### Option B: Docker (Recommended for production)

```powershell
# Build image
docker build -t oci-file-transfer .

# Run container
docker run --rm `
  -e OCI_NAMESPACE="your_namespace" `
  -e OCI_BUCKET_NAME="your_bucket" `
  -v "$env:USERPROFILE\.oci:/root/.oci:ro" `
  -v "$(pwd)/uploads:/app/uploads:ro" `
  -v "$(pwd)/logs:/app/logs:rw" `
  oci-file-transfer upload-dir --local-path /app/uploads
```

### Option C: Docker Compose (Easiest)

```powershell
# Load environment from .env
docker-compose run --rm file-transfer upload-dir --local-path /app/uploads

# Or use the Windows script
.\start.cmd upload
```

## Command Examples

```powershell
# Help
python app.py --help

# Upload single file
python app.py upload-file --local-path "./uploads/photo.jpg" --object-name "images/photo.jpg"

# Upload entire directory
python app.py upload-dir --local-path "./uploads" --object-prefix "photos/2024/february"

# List files
python app.py list --object-prefix "photos"


# Download file
python app.py download --blob-name "photos/image.jpg" --local-path "./downloads/image.jpg"
```

## Troubleshooting

### "Python not found"
- Reinstall Python and ensure "Add Python to PATH" is checked
- Restart your terminal after installation
- Use full path: `C:\Python311\python.exe app.py`

### "No module named 'azure'"
```powershell
pip install -r requirements.txt
```

### "Connection failed to Azure"
- Verify `.env` file has correct credentials
- Check connection string format
- Test connection: `python app.py list`

### "Permission denied"
- Check file/folder permissions
- Run as Administrator if needed
- Use Docker for isolation

## Project Structure Reference

```
PhotoSync/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .env                  # Configuration (create from .env.example)
├── .env.example          # Template
├── .gitignore            # Git ignore rules
├── README.md             # Documentation
├── start.sh              # Linux/Mac script
├── start.cmd             # Windows script
├── uploads/              # Files to upload (create this directory)
├── downloads/            # Download destination (auto-created)
└── logs/                 # Application logs (auto-created)
```

## Next Steps

1. **Install Python 3.11+** (if not already installed)
2. **Edit .env** with your Azure credentials
3. **Create uploads directory**: `mkdir uploads`
4. **Run**: `python app.py --help` to verify setup
5. **Test upload**: Add files to `uploads/` and run upload command

---

For detailed usage, see [README.md](README.md)
