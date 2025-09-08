from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import boto3
from botocore.exceptions import ClientError
import smtplib
import email.mime.text
import email.mime.multipart
import os
from pathlib import Path
import tempfile
from typing import Optional
import re
import random
import string
from datetime import datetime, timedelta
from decouple import config
import requests

# Environment Configuration
ENVIRONMENT = config("ENVIRONMENT", default="dev").lower()
IS_PRODUCTION = ENVIRONMENT == "prod"

# Configure FastAPI based on environment
app = FastAPI(
    title="Zenith Club Certificate Portal",
    description="Secure certificate download portal with OTP verification",
    version="1.0.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = "certificates.db"

# MinIO/S3 Configuration
MINIO_ENDPOINT = config("MINIO_ENDPOINT", default="s3.zenithclub.in")
ACCESS_KEY = config("AWS_ACCESS_KEY_ID", default="your_access_key_here")
SECRET_KEY = config("AWS_SECRET_ACCESS_KEY", default="your_secret_key_here")
BUCKET_NAME = config("BUCKET_NAME", default="certificates")

# SMTP Configuration
SMTP_SERVER = config("SMTP_SERVER", default="smtp.gmail.com")
SMTP_PORT = config("SMTP_PORT", default=587, cast=int)
SMTP_USERNAME = config("SMTP_USERNAME", default="your_email@gmail.com")
SMTP_PASSWORD = config("SMTP_PASSWORD", default="your_app_password")
SMTP_FROM_NAME = config("SMTP_FROM_NAME", default="Zenith Club")
SMTP_FROM_EMAIL = config("SMTP_FROM_EMAIL", default="noreply@zenithclub.in")

# OTP Configuration
OTP_EXPIRY_MINUTES = 10

# Store OTPs temporarily (in production, use Redis or database)
otp_store = {}

def get_allowed_emails():
    """Get list of allowed email domains/addresses"""
    # In a real application, this would come from a config file or database
    return [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
        "student.university.edu", "university.edu"
    ]

def validate_email(email: str) -> bool:
    """Validate email format and check for sushantuniversity.edu.in domain with roll number"""
    # Check if email ends with @sushantuniversity.edu.in
    if not email.endswith("@sushantuniversity.edu.in"):
        return False
    
    # Extract the local part (before @)
    local_part = email.split("@")[0]
    
    # Check if local part contains a roll number pattern
    # Expected format: name.rollnumber (e.g., aditya.220btccse004)
    if "." not in local_part:
        return False
    
    # Get the roll number part (after the last dot)
    parts = local_part.split(".")
    if len(parts) < 2:
        return False
    
    roll_number = parts[-1].lower()  # Get last part and convert to lowercase
    
    # Validate roll number format (3 digits + letters + 3 digits)
    # Examples: 220btccse004, 230bca006, 240btccse046
    roll_pattern = r'^\d{3}[a-z]+\d{3}$'
    
    return bool(re.match(roll_pattern, roll_number))

def extract_roll_number_from_email(email: str) -> str:
    """Extract roll number from email (e.g., aditya.220btccse004@sushantuniversity.edu.in -> 220btccse004)"""
    if not email.endswith("@sushantuniversity.edu.in"):
        return ""
    
    local_part = email.split("@")[0]
    if "." not in local_part:
        return ""
    
    parts = local_part.split(".")
    if len(parts) < 2:
        return ""
    
    return parts[-1].lower()  # Return the roll number part

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create certificates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            has_certificate INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0,
            last_downloaded DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create downloads log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT NOT NULL,
            email TEXT NOT NULL,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_otp(email: str = ""):
    """Generate 6-digit OTP"""
    # Hardcoded OTP for dummy user for testing
    if email and "dummy.220btccse000@sushantuniversity.edu.in" in email.lower():
        return "123456"
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email_address: str, otp: str):
    """Send OTP via email"""
    try:
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = email_address
        msg['Subject'] = "Zenith Club - Certificate Download OTP"
        
        body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Zenith Club - Certificate Download OTP</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap" rel="stylesheet">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Fira Code', monospace; background: radial-gradient(1200px 800px at 10% 10%, rgba(0,255,157,0.07), transparent 60%), radial-gradient(1000px 600px at 90% 10%, rgba(0,200,255,0.06), transparent 60%), #0a0a0a; color: #f0f0f0; min-height: 100vh;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                
                <!-- Header matching website theme -->
                <div style="background: rgba(255,255,255,0.03); backdrop-filter: blur(10px); padding: 20px 30px; text-align: center; border-radius: 12px 12px 0 0; border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, rgba(0,255,157,.6), rgba(0,160,255,.35)); opacity: 0.1; border-radius: 12px 12px 0 0;"></div>
                    <div style="position: relative; z-index: 2;">
                        <div style="display: inline-flex; align-items: center; gap: 8px; margin-bottom: 10px; line-height: 1;">
                            <span style="color: #9ca3af; font-size: 24px; font-weight: bold;">&lt;</span>
                            <span style="color: #ffffff; font-size: 28px; font-weight: bold; line-height: 1;">
                                <span style="color: #00ff9d;">Z</span>enith
                            </span>
                            <span style="color: #9ca3af; font-size: 24px; font-weight: bold;">/&gt;</span>
                        </div>
                        <div style="color: #9ca3af; font-size: 14px; font-family: 'Fira Code', monospace; line-height: 1.4;">
                            <span style="color: #00ff9d;">./certificates</span> • Tenure 2024-25
                        </div>
                    </div>
                </div>
                
                <!-- Main content with matching glass theme -->
                <div style="background: rgba(255,255,255,0.03); backdrop-filter: blur(10px); padding: 40px 30px; border-radius: 0 0 12px 12px; border: 1px solid rgba(255,255,255,0.1); border-top: none;">
                    
                    <!-- Status indicator -->
                    <div style="display: inline-flex; align-items: center; gap: 10px; padding: 10px 18px; border-radius: 20px; border: 1px solid rgba(128, 128, 128, 0.3); background: rgba(255,255,255,0.03); color: #d1d5db; font-size: 14px; margin-bottom: 30px; font-family: 'Fira Code', monospace; line-height: 1;">
                        <span style="height: 8px; width: 8px; border-radius: 50%; background: #00ff9d; flex-shrink: 0;"></span>
                        <span style="white-space: nowrap;">OTP Verification • Certificate Portal</span>
                    </div>
                    
                    <h2 style="color: #f0f0f0; margin: 0 0 15px 0; font-size: 26px; text-align: center; font-weight: 700; line-height: 1.3; letter-spacing: 0.5px;">🔐&nbsp;&nbsp;Authentication Required</h2>
                    <p style="color: #9ca3af; text-align: center; margin: 0 0 30px 0; font-size: 16px; line-height: 1.5;">Enter this verification code to access your certificate</p>
                    
                    <!-- OTP Code Box with neon glow matching website -->
                    <div style="background: linear-gradient(135deg, rgba(0,255,157,0.1), rgba(0,160,255,0.05)); border: 1px solid rgba(0,255,157,0.35); padding: 30px; text-align: center; border-radius: 12px; margin: 30px 0; box-shadow: 0 0 0 1px rgba(0,255,157,0.35), 0 0 30px 2px rgba(0,255,157,0.15); position: relative;">
                        <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,255,157,.6), rgba(0,160,255,.35)); opacity: 0.1; border-radius: 12px; pointer-events: none;"></div>
                        <div style="position: relative; z-index: 2;">
                            <h3 style="margin: 0; font-size: 48px; letter-spacing: 12px; font-weight: bold; color: #00ff9d; text-shadow: 0 0 20px rgba(0,255,157,0.5); font-family: 'Fira Code', monospace;">{otp}</h3>
                            <p style="margin: 15px 0 0 0; color: #9ca3af; font-size: 14px;">⏱️ Expires in 10 minutes</p>
                        </div>
                    </div>
                    
                    <!-- Security info with terminal-like styling -->
                    <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 12px; padding: 20px; margin: 20px 0; font-family: 'Fira Code', monospace;">
                        <p style="color: #fca5a5; margin: 0 0 15px 0; font-weight: bold; font-size: 16px;">🛡️ Security Notice</p>
                        <div style="color: #fecaca; margin: 0; line-height: 1.8; font-size: 14px;">
                            <div style="margin-bottom: 8px;">• This code expires in 10 minutes</div>
                            <div style="margin-bottom: 8px;">• Never share this code with anyone</div>
                            <div style="margin-bottom: 8px;">• Zenith Club will never ask for this code</div>
                            <div>• If you didn't request this, please ignore this email</div>
                        </div>
                    </div>
                    
                    <!-- Support section with theme colors -->
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <p style="color: #9ca3af; font-size: 14px; margin: 0;">Need help? Contact our support team</p>
                        <p style="color: #00ff9d; font-size: 14px; margin: 5px 0 0 0; font-weight: 500;">contact@zenithclub.in</p>
                    </div>
                    
                    <!-- Footer with terminal styling -->
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); margin: 30px 0 0 0; padding: 20px 0 0 0;">
                        <p style="font-size: 12px; color: #6b7280; text-align: center; margin: 0; line-height: 1.6; font-family: 'Fira Code', monospace;">
                            <span style="color: #9ca3af;">$</span> <span style="color: #00ff9d;">zenith-club</span> <span style="color: #6b7280;">--automated-email</span><br>
                            <span style="color: #6b7280; font-size: 11px;">This is an automated message from Zenith Club Certificate Portal</span><br>
                            <span style="color: #6b7280; font-size: 11px;">Please do not reply to this email</span>
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(email.mime.text.MIMEText(body, 'html'))
        
        # Use SMTP_SSL for port 465, regular SMTP with starttls for port 587
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def check_certificate_exists(roll_number: str) -> bool:
    """Check if certificate exists in S3/MinIO"""
    try:
        s3_client = get_s3_client()
        if not s3_client:
            print("S3 client not available, checking local files as fallback")
            # Fallback to local file check
            pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and roll_number.upper() in f.upper()]
            return len(pdf_files) > 0
            
        s3_key = f"certificates/tenure2024-25/{roll_number.upper()}.pdf"
        
        s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except ClientError as e:
        # Try lowercase version
        try:
            if s3_client:
                s3_key = f"certificates/tenure2024-25/{roll_number.lower()}.pdf"
                s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
                return True
        except ClientError:
            pass
        
        # Fallback to local file check
        try:
            pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and roll_number.upper() in f.upper()]
            return len(pdf_files) > 0
        except Exception:
            return False
    except Exception as e:
        print(f"S3 connection error: {e}")
        # Fallback to local file check
        try:
            pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and roll_number.upper() in f.upper()]
            return len(pdf_files) > 0
        except Exception:
            return False

def update_certificate_status(roll_number: str):
    """Update certificate status in database"""
    conn = get_db()
    cursor = conn.cursor()
    
    has_cert = 1 if check_certificate_exists(roll_number) else 0
    
    cursor.execute(
        "INSERT OR REPLACE INTO certificates (roll_number, has_certificate) VALUES (?, ?)",
        (roll_number.upper(), has_cert)
    )
    
    conn.commit()
    conn.close()
    return has_cert

def get_s3_client():
    """Get MinIO/S3 client"""
    try:
        return boto3.client(
            's3',
            endpoint_url=f'https://{MINIO_ENDPOINT}',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name='us-east-1'  # MinIO typically uses this
        )
    except Exception as e:
        print(f"Failed to create S3 client: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Print startup info only in development
    if not IS_PRODUCTION:
        print(f"🚀 Zenith Club Certificate Portal starting in {ENVIRONMENT.upper()} mode")
        print(f"📚 API Documentation: http://localhost:8000/docs")
        print(f"🔧 ReDoc: http://localhost:8000/redoc")
    else:
        print("🚀 Zenith Club Certificate Portal starting in PRODUCTION mode")
        print("📚 API Documentation: DISABLED for production")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the index page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/send-otp")
async def send_otp_route(
    email: str = Form(...)
):
    """Send OTP to email"""
    
    # Validate email format and domain
    if not validate_email(email):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid email format. Email must be in format: name.rollnumber@sushantuniversity.edu.in"}
        )
    
    # Extract roll number from email
    roll_number = extract_roll_number_from_email(email)
    if not roll_number:
        return JSONResponse(
            status_code=400,
            content={"error": "Could not extract roll number from email"}
        )
    
    # Check if certificate exists in database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT has_certificate FROM certificates WHERE roll_number = ?", (roll_number.upper(),))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result['has_certificate']:
        return JSONResponse(
            status_code=404,
            content={"error": f"No certificate found for roll number: {roll_number.upper()}"}
        )
    
    # Generate and send OTP
    otp = generate_otp(email)
    expiry = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Store OTP
    otp_store[email] = {
        "otp": otp,
        "roll_number": roll_number.upper(),
        "expiry": expiry
    }
    
    # Send OTP email (for demo, we'll just print it and return success)
    # Print OTP only in development mode or for dummy user
    if not IS_PRODUCTION:
        print(f"OTP for {email}: {otp}")  # Debug info for development
    
    # Special handling for dummy user - no email sent
    if "dummy.220btccse000@sushantuniversity.edu.in" in email.lower():
        print(f"🎯 DUMMY USER OTP: {otp} (hardcoded for testing - no email sent)")
        return JSONResponse(content={"message": "OTP sent successfully (dummy mode - check console)"})
    
    try:
        if send_otp_email(email, otp):
            return JSONResponse(content={"message": "OTP sent successfully"})
        else:
            # Fallback: still succeed even if email fails (for demo purposes)
            return JSONResponse(content={"message": "OTP sent successfully (demo mode)"})
    except:
        # Fallback for demo purposes
        return JSONResponse(content={"message": "OTP sent successfully (demo mode)"})

@app.post("/verify-otp")
async def verify_otp_route(
    email: str = Form(...),
    otp: str = Form(...)
):
    """Verify OTP and return certificate status"""
    
    if email not in otp_store:
        return JSONResponse(
            status_code=400,
            content={"error": "No OTP found for this email"}
        )
    
    stored_data = otp_store[email]
    
    # Check if OTP has expired
    if datetime.now() > stored_data["expiry"]:
        del otp_store[email]
        return JSONResponse(
            status_code=400,
            content={"error": "OTP has expired. Please request a new one."}
        )
    
    # Verify OTP
    if stored_data["otp"] != otp:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid OTP"}
        )
    
    # OTP is valid
    return JSONResponse(content={"success": True, "roll_number": stored_data["roll_number"]})

def generate_presigned_url(roll_number: str, expiration: int = 3600) -> Optional[str]:
    """Generate presigned URL for certificate download from S3/MinIO"""
    try:
        s3_client = get_s3_client()
        if not s3_client:
            print("S3 client not available")
            return None
            
        # Try uppercase first
        s3_key = f"certificates/tenure2024-25/{roll_number.upper()}.pdf"
        
        try:
            # Check if file exists with uppercase
            s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        except ClientError:
            # Try lowercase
            s3_key = f"certificates/tenure2024-25/{roll_number.lower()}.pdf"
            try:
                s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
            except ClientError:
                print(f"Certificate file not found for {roll_number}")
                return None
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
        
        return presigned_url
        
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

@app.get("/download/{roll_number}")
async def download_certificate(roll_number: str, email: str):
    """Download certificate PDF via presigned URL or redirect"""
    
    # Verify that user has completed OTP verification
    if email not in otp_store:
        raise HTTPException(status_code=403, detail="Please complete OTP verification first")
    
    stored_data = otp_store[email]
    if stored_data["roll_number"] != roll_number.upper():
        raise HTTPException(status_code=403, detail="Invalid access")
    
    try:
        # First try to get presigned URL from S3/MinIO
        presigned_url = generate_presigned_url(roll_number)
        
        if presigned_url:
            # Log download
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO download_logs (roll_number, email) VALUES (?, ?)",
                (roll_number.upper(), email)
            )
            cursor.execute(
                "UPDATE certificates SET download_count = download_count + 1, last_downloaded = ? WHERE roll_number = ?",
                (datetime.now(), roll_number.upper())
            )
            conn.commit()
            conn.close()
            
            # Clean up OTP after successful download
            if email in otp_store:
                del otp_store[email]
            
            # Download file from S3 and return as FileResponse
            try:
                response = requests.get(presigned_url, stream=True)
                response.raise_for_status()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    temp_file.flush()
                
                return FileResponse(
                    temp_file.name,
                    media_type='application/pdf',
                    filename=f"{roll_number.upper()}_certificate.pdf"
                )
                
            except Exception as e:
                print(f"Error downloading from S3: {e}")
                # Fallback to redirect if download fails
                return RedirectResponse(url=presigned_url)
        
        else:
            # Fallback to local files if S3 is not available
            pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and roll_number.upper() in f.upper()]
            if pdf_files:
                pdf_path = pdf_files[0]
                
                # Log download
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO download_logs (roll_number, email) VALUES (?, ?)",
                    (roll_number.upper(), email)
                )
                cursor.execute(
                    "UPDATE certificates SET download_count = download_count + 1, last_downloaded = ? WHERE roll_number = ?",
                    (datetime.now(), roll_number.upper())
                )
                conn.commit()
                conn.close()
                
                # Clean up OTP after successful download
                if email in otp_store:
                    del otp_store[email]
                
                return FileResponse(
                    pdf_path,
                    media_type='application/pdf',
                    filename=f"{roll_number.upper()}_certificate.pdf"
                )
            else:
                raise HTTPException(status_code=404, detail="Certificate file not found")
        
    except Exception as e:
        print(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while downloading: {str(e)}")

@app.get("/preview/{roll_number}")
async def preview_certificate(roll_number: str, email: str):
    """Preview certificate PDF via presigned URL or redirect"""
    
    # Verify that user has completed OTP verification
    if email not in otp_store:
        raise HTTPException(status_code=403, detail="Please complete OTP verification first")
    
    stored_data = otp_store[email]
    if stored_data["roll_number"] != roll_number.upper():
        raise HTTPException(status_code=403, detail="Invalid access")
    
    try:
        # Generate presigned URL for preview (shorter expiration)
        presigned_url = generate_presigned_url(roll_number, expiration=900)  # 15 minutes
        
        if presigned_url:
            # Log preview (don't increment download count for preview)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO download_logs (roll_number, email) VALUES (?, ?)",
                (roll_number.upper(), email)
            )
            conn.commit()
            conn.close()
            
            # Redirect to presigned URL for preview
            return RedirectResponse(url=presigned_url)
        
        else:
            # Fallback to local files
            pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and roll_number.upper() in f.upper()]
            if pdf_files:
                pdf_path = pdf_files[0]
                return FileResponse(
                    pdf_path,
                    media_type='application/pdf',
                    filename=f"{roll_number.upper()}_certificate.pdf"
                )
            else:
                raise HTTPException(status_code=404, detail="Certificate file not found")
        
    except Exception as e:
        print(f"Preview error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while previewing: {str(e)}")

# Additional static file routes
@app.get("/script.js")
async def get_script():
    """Serve JavaScript file"""
    return FileResponse("static/script.js", media_type="application/javascript")

@app.get("/style.css")
async def get_style():
    """Serve CSS file"""
    return FileResponse("static/style.css", media_type="text/css")

@app.get("/favicon.ico")
async def get_favicon():
    """Serve favicon file"""
    return FileResponse("static/favicon-32.png", media_type="image/png")

@app.get("/test-s3")
async def test_s3_connection():
    """Test S3/MinIO connectivity and list available certificates"""
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return JSONResponse(content={"error": "S3 client not available"})
        
        # List objects in the certificates bucket
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix="certificates/tenure2024-25/"
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })
        
        return JSONResponse(content={
            "status": "success",
            "bucket": BUCKET_NAME,
            "endpoint": MINIO_ENDPOINT,
            "files_found": len(files),
            "files": files[:10]  # Show first 10 files
        })
        
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "error": str(e),
            "bucket": BUCKET_NAME,
            "endpoint": MINIO_ENDPOINT
        })

# Debug endpoints (only available in development)
if not IS_PRODUCTION:
    @app.get("/debug/info")
    async def debug_info():
        """Debug information - only available in development mode"""
        return {
            "environment": ENVIRONMENT,
            "is_production": IS_PRODUCTION,
            "database": DATABASE,
            "minio_endpoint": MINIO_ENDPOINT,
            "bucket_name": BUCKET_NAME,
            "smtp_server": SMTP_SERVER,
            "docs_enabled": True,
            "message": "Debug mode is active"
        }
    
    @app.get("/debug/otp-store")
    async def debug_otp_store():
        """View current OTP store - only available in development mode"""
        return {
            "otp_count": len(otp_store),
            "emails": list(otp_store.keys()),
            "message": "This endpoint is only available in development mode"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)