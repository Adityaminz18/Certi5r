# 🎓 Zenith Club Certificate Portal - Certi5r

A modern, secure FastAPI-based web application for downloading academic certificates with OTP verification and S3/MinIO cloud storage integration.

**Repository**: [https://github.com/Adityaminz18/Certi5r](https://github.com/Adityaminz18/Certi5r)

![Certificate Portal](https://img.shields.io/badge/FastAPI-009639?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![AWS S3](https://img.shields.io/badge/AWS%20S3-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white)

## ✨ Features

- **🔐 Secure Authentication**: OTP-based email verification system
- **🎨 Modern UI**: Dark theme with particle effects and glass morphism design
- **☁️ Cloud Storage**: S3/MinIO integration for secure file storage
- **📧 Email Validation**: University domain verification (@sushantuniversity.edu.in)
- **📱 Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **⚡ Fast Downloads**: Direct file downloads with presigned URLs
- **�️ Security**: Rate limiting and secure certificate validation

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with automatic schema management
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Storage**: AWS S3/MinIO compatible object storage
- **Email**: SMTP integration for OTP delivery
- **Security**: OTP verification with time-based expiration

## 📋 Prerequisites

- Python 3.8+
- S3/MinIO storage access
- SMTP email server credentials
- University email domain access

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Adityaminz18/Certi5r.git
   cd Certi5r
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```env
   # Application Environment
   ENVIRONMENT=dev  # Use 'prod' for production, 'dev' for development
   
   # S3/MinIO Configuration
   MINIO_ENDPOINT=s3.zenithclub.in
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   BUCKET_NAME=certificates

   # SMTP Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

5. **Run the application**
   ```bash
   python3 main.py
   ```

6. **Access the portal**
   Open http://localhost:8000 in your browser

## 📁 Project Structure

```
Certi5r/
├── main.py                 # FastAPI application
├── add_to_db.py           # Database management script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── certificates.db        # SQLite database (auto-created)
├── templates/
│   └── index.html         # Main UI template
├── static/
│   ├── favicon-*.png      # Favicon files
│   ├── favicon.ico        # Favicon
│   └── script.js          # Frontend JavaScript
└── README.md             # This file
```

## 🔧 Configuration

### Environment Modes
The application supports two modes controlled by the `ENVIRONMENT` variable:

#### Development Mode (`ENVIRONMENT=dev`)
- ✅ API Documentation available at `/docs` and `/redoc`
- ✅ Debug endpoints enabled (`/debug/info`, `/debug/otp-store`)
- ✅ OTP values printed to console for testing
- ✅ Detailed startup information
- ✅ All debugging features enabled

#### Production Mode (`ENVIRONMENT=prod`)
- ❌ API Documentation disabled (security)
- ❌ Debug endpoints disabled
- ❌ No OTP printing to console
- ✅ Clean production startup
- ✅ Enhanced security posture

### Email Format Validation
The system validates that emails follow the university format:
- **Format**: `name.rollnumber@sushantuniversity.edu.in`
- **Example**: `aditya.220btccse004@sushantuniversity.edu.in`
- **Roll Number Pattern**: 3 digits + letters + 3 digits (e.g., 220btccse004)

### S3/MinIO Setup
Certificates should be uploaded to your S3/MinIO bucket with filenames matching roll numbers:
- **Naming Convention**: `{ROLL_NUMBER}.pdf` (e.g., `220BTCCSE004.pdf`)
- **File Format**: PDF files
- **Bucket**: Configured in environment variables

### SMTP Configuration
For Gmail, use App Passwords:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `SMTP_PASSWORD`

## 🎯 Usage

1. **Student Access**:
   - Visit the portal
   - Enter university email (name.rollnumber@sushantuniversity.edu.in)
   - Receive OTP via email
   - Enter OTP to verify
   - Download certificate

2. **Admin Setup**:
   - Upload certificates to S3/MinIO bucket
   - Ensure filenames match roll numbers
   - Update database records as needed

## 🛠️ API Endpoints

- `GET /` - Main portal interface
- `POST /send-otp` - Send OTP to email
- `POST /verify-otp` - Verify OTP and get access
- `GET /preview/{roll_number}` - Preview certificate (15-min expiry)
- `GET /download/{roll_number}` - Download certificate

## 🧪 Testing & Demo

### Dummy User for Testing

A special dummy user is available for testing the complete flow without needing real email verification:

- **Email**: `dummy.220btccse000@sushantuniversity.edu.in`
- **Hardcoded OTP**: `123456` (always works)
- **Roll Number**: `220btccse000`
- **Certificate**: Available in database
- **No Email Sent**: Emails are skipped for dummy user (console only)

### Testing Steps

1. **Start the portal** and navigate to `http://localhost:8000`
2. **Enter dummy email**: `dummy.220btccse000@sushantuniversity.edu.in`
3. **Click "Send OTP"** - will show success message (no actual email sent)
4. **Check console** - OTP `123456` will be displayed in server logs
5. **Enter OTP**: Use `123456` 
6. **Access certificate**: Preview and download will work

### Debug Features (Development Mode)

- ✅ All OTP values printed to console
- ✅ Debug endpoints enabled (`/debug/info`, `/debug/otp-store`)
- ✅ Special dummy user notifications
- ✅ Error details in responses

### Database Management

Use the included database management script:

```bash
# Add new certificate entries
python add_to_db.py add <roll_number>

# View all certificates
python add_to_db.py view

# Interactive menu
python add_to_db.py
```

## 📊 Database Management Guide

### Using the `add_to_db.py` Script

The `add_to_db.py` script is a comprehensive tool for managing certificate entries in the SQLite database. It provides both command-line and interactive interfaces.

#### Command Line Usage

```bash
# Initialize the database (creates tables if they don't exist)
python add_to_db.py

# Add a new certificate entry
python add_to_db.py add 220btccse004

# View all certificate entries
python add_to_db.py view

# Search for a specific certificate
python add_to_db.py search 220btccse004

# Delete a certificate entry
python add_to_db.py delete 220btccse004

# Add dummy test data
python add_to_db.py dummy
```

#### Interactive Menu

Run the script without arguments to access the interactive menu:

```bash
python add_to_db.py
```

The interactive menu provides:
1. **Add Certificate Entry** - Add new roll numbers to the database
2. **View All Certificates** - Display all entries with download statistics
3. **Search Certificate** - Find specific certificate details
4. **Delete Certificate** - Remove entries from database
5. **Add Dummy Data** - Add test entry (220btccse000) for testing
6. **Initialize Database** - Create/recreate database tables

#### Database Schema

The script manages two main tables:

**Certificates Table:**
```sql
CREATE TABLE certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT UNIQUE NOT NULL,           -- Student roll number (lowercase)
    has_certificate INTEGER DEFAULT 0,          -- 1 if certificate exists, 0 if not
    download_count INTEGER DEFAULT 0,           -- Number of times downloaded
    last_downloaded DATETIME,                   -- Last download timestamp
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Download Logs Table:**
```sql
CREATE TABLE download_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT NOT NULL,                  -- Student roll number
    email TEXT NOT NULL,                        -- Student email
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Adding Certificates in Bulk

For bulk operations, you can create a script or use the interactive menu repeatedly:

```bash
# Example: Add multiple certificates
python add_to_db.py add 220btccse001
python add_to_db.py add 220btccse002
python add_to_db.py add 220btccse003
```

#### Certificate File Naming Convention

Ensure your S3/MinIO bucket contains certificate files with names matching the roll numbers:
- **Format**: `{ROLL_NUMBER}.pdf`
- **Example**: `220btccse004.pdf`
- **Case**: Both uppercase and lowercase supported (script checks both)

#### Verification Steps

After adding certificates to the database:

1. **Check Database Entry:**
   ```bash
   python add_to_db.py search 220btccse004
   ```

2. **Verify S3/MinIO File:**
   - Ensure `220BTCCSE004.pdf` or `220btccse004.pdf` exists in your bucket

3. **Test Download:**
   - Use the dummy email format: `name.220btccse004@sushantuniversity.edu.in`
   - Test the complete OTP flow

#### Best Practices

- **Roll Number Format**: Use lowercase in database (script auto-converts)
- **File Naming**: Use uppercase for S3 files (`220BTCCSE004.pdf`)
- **Backup**: Regular database backups before bulk operations
- **Testing**: Use dummy data (220btccse000) for testing flows

## 🔒 Security Features

- **OTP Verification**: 6-digit codes with 10-minute expiry
- **Email Domain Validation**: Restricted to university domain
- **Presigned URLs**: Temporary access with controlled expiration
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive form and data validation

## 🎨 UI Features

- **Dark Theme**: Modern dark interface with #00ff9d accent color
- **Particle Effects**: Animated background particles
- **Glass Morphism**: Modern card designs with backdrop blur
- **Responsive**: Works on desktop, tablet, and mobile
- **Typography**: Fira Code monospace font for terminal aesthetics

## � Email Template

The system sends beautifully designed emails matching the portal's theme:
- Dark background with green accents
- Glass morphism effects
- Security notices and instructions
- Responsive design for all email clients

## 🐛 Troubleshooting

### Common Issues

1. **Email not received**
   - Check spam folder
   - Verify SMTP configuration
   - Ensure email format is correct

2. **Certificate not found**
   - Verify roll number in email
   - Check S3/MinIO bucket contents
   - Ensure filename matches roll number

3. **Download issues**
   - Check S3/MinIO connectivity
   - Verify bucket permissions
   - Ensure certificate file exists

### Database Reset
To reset the database:
```bash
rm certificates.db
# Restart the application to recreate
```

## 🤝 Contributing

1. Fork the repository at [https://github.com/Adityaminz18/Certi5r](https://github.com/Adityaminz18/Certi5r)
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support or questions:
- Create an issue in the [GitHub repository](https://github.com/Adityaminz18/Certi5r/issues)
- Contact: contact@zenithclub.in

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Tailwind CSS for the styling system
- MinIO for S3-compatible storage

---

**Made with ❤️ for Zenith Club & Sushant University**

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   git clone https://github.com/Adityaminz18/Certi5r.git
   cd Certi5r
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python add_to_db.py  # Initialize database
   ```

2. **Configure SMTP**
   ```bash
   cp .env.example .env
   # Edit .env with your SMTP credentials
   ```

3. **Run Server**
   ```bash
   source venv/bin/activate
   uvicorn main:app --reload
   ```

4. **Access Portal**
   - Open: http://localhost:8000

## 📂 Project Structure

```
📁 Certi5r/
├── 🚀 main.py                 # FastAPI application with OTP system
├── �️ add_to_db.py           # Database management script
├── 📋 requirements.txt        # Dependencies
├── 🔐 .env.example           # Environment template
├── 🚫 .gitignore             # Git ignore rules
├── 📊 certificates.db        # SQLite database
├── 📁 templates/
│   └── 🏠 index.html         # Multi-step interface
├── 📁 static/
│   ├── 🖼️ favicon-*.png      # Favicon files
│   ├── 🎨 favicon.ico        # Favicon
│   └── ⚡ script.js          # Interactive JavaScript
└── 📖 README.md              # This documentation
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# MinIO/S3 Configuration
MINIO_ENDPOINT=s3.zenithclub.in
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BUCKET_NAME=certificates

# SMTP Configuration
# For Gmail (testing):
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# For Zoho (production):
SMTP_SERVER=smtp.zoho.com
SMTP_PORT=587
SMTP_USERNAME=your_email@zenithclub.in
SMTP_PASSWORD=your_password
```

### S3 Bucket Structure

Upload certificates to your MinIO S3 bucket with this structure:
```
certificates/
└── tenure2024-25/
    ├── 220BTCCSE004.pdf    # Uppercase
    ├── 220btccse004.pdf    # Lowercase (fallback)
    ├── 230BTCCSE016.pdf
    └── ...
```

## 🎯 How It Works

### For Users:

1. **Enter Details**: Roll number and email address
2. **OTP Verification**: Receive and enter 6-digit OTP
3. **Download**: Preview and download certificate if available

### API Workflow:

1. `POST /send-otp` - Validates roll number and sends OTP
2. `POST /verify-otp` - Verifies OTP and enables download
3. `GET /download/{roll_number}` - Downloads certificate
4. `GET /preview/{roll_number}` - Previews certificate

## 📊 Database Schema

```sql
-- Certificates table
CREATE TABLE certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT UNIQUE NOT NULL,
    has_certificate INTEGER DEFAULT 0,  -- 1 if exists, 0 if not
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Download logs
CREATE TABLE download_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT NOT NULL,
    email TEXT NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 Security Features

- **OTP Verification**: 6-digit OTP with 10-minute expiry
- **Email Validation**: Basic email format validation
- **Roll Number Validation**: Format validation (e.g., 220BTCCSE004)
- **Session Management**: OTP cleanup after use/expiry
- **Download Logging**: All downloads tracked with timestamps

## 🎨 UI Features

- **🎯 Step-by-step Process**: Guided multi-step interface
- **📱 Responsive Design**: Works on all devices
- **🎭 Smooth Animations**: Modern CSS animations
- **🔄 Loading States**: Visual feedback during operations
- **❌ Error Handling**: Clear error messages
- **🎉 Success States**: Celebration for successful verification

## 📧 SMTP Setup

### Gmail (for testing):
1. Enable 2-factor authentication
2. Generate app password
3. Use app password in SMTP_PASSWORD

### Zoho (for production):
1. Use your Zoho Mail credentials
2. Ensure SMTP is enabled in Zoho settings

## 🚀 Deployment

### Development:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔧 Troubleshooting

### Common Issues:

1. **OTP not received**: Check SMTP configuration in .env
2. **Certificate not found**: Verify S3 bucket structure and file names
3. **Database errors**: Run `python add_to_db.py` to initialize database
4. **Import errors**: Ensure virtual environment is activated

### Debug Mode:
Set `DEBUG=True` in .env for detailed error messages.


## 🎉 Thank You Message

The portal includes a special thank you message:
> "Thank you for contributing to Zenith Club's events and making them memorable! Your participation and enthusiasm have been invaluable to our community."

## 📞 Support

For technical issues or questions about the certificate portal, contact the Zenith Club technical team.

---

**© 2024 Zenith Club. All rights reserved.**
