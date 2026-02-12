#!/usr/bin/env python3
"""
CareFlow AI - Full Deployment Script
Uploads source code and deploys the application
"""
import paramiko
import os
import tarfile
import io
from stat import S_IRWXU

HOST = '79.99.45.136'
USERNAME = 'root'
PASSWORD = 'j2nzgPFUido5D'
REMOTE_DIR = '/opt/careflow-ai-deploy'
LOCAL_DIR = r'C:\Users\evera\careflow-ai'

# Files/directories to exclude from upload
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.venv',
    'venv',
    'node_modules',
    '.next',
    '.git',
    '*.pyc',
    '.pytest_cache',
    'coverage',
    'dist',
    'build',
    '.DS_Store',
    '*.log',
    'DEPLOYMENT_PACKAGE',
    '.claude',
]

def should_exclude(path):
    """Check if path should be excluded from upload"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern.replace('*', '') in path:
            return True
        # Check for file extensions
        if pattern.startswith('*') and path.endswith(pattern[1:]):
            return True
    return False

def create_tar(directory, name):
    """Create a tar file excluding unnecessary files"""
    print(f'Creating tar for {name}...')
    tar_buffer = io.BytesIO()

    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)
                if not should_exclude(file_path):
                    # Get path relative to directory
                    arcname = os.path.relpath(file_path, directory)
                    try:
                        tar.add(file_path, arcname=arcname)
                    except Exception as e:
                        print(f'  Warning: Could not add {file_path}: {e}')

    tar_buffer.seek(0)
    return tar_buffer

def upload_tar(ssh, sftp, tar_buffer, remote_path, name):
    """Upload a tar file and extract it"""
    print(f'Uploading {name}...')

    # Upload tar file
    tar_file_path = f'/tmp/{name}.tar.gz'
    remote_file = sftp.file(tar_file_path, 'w')
    remote_file.set_pipelined(True)
    remote_file.write(tar_buffer.read())
    remote_file.close()

    print(f'Extracting {name}...')
    # Extract on remote server
    stdin, stdout, stderr = ssh.exec_command(f'tar -xzf {tar_file_path} -C {remote_path}')
    stdout.channel.recv_exit_status()

    # Clean up tar file
    ssh.exec_command(f'rm {tar_file_path}')
    print(f'Uploaded and extracted {name}')

def main():
    print('=' * 50)
    print('CareFlow AI - Full Deployment')
    print('=' * 50)

    # Connect to server
    print('\nConnecting to server...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USERNAME, PASSWORD, timeout=30)
    sftp = ssh.open_sftp()

    # Create backend tar and upload
    backend_path = os.path.join(LOCAL_DIR, 'backend')
    if os.path.exists(backend_path):
        backend_tar = create_tar(backend_path, 'backend')
        upload_tar(ssh, sftp, backend_tar, REMOTE_DIR, 'backend')

    # Create frontend tar and upload
    frontend_path = os.path.join(LOCAL_DIR, 'frontend')
    if os.path.exists(frontend_path):
        frontend_tar = create_tar(frontend_path, 'frontend')
        upload_tar(ssh, sftp, frontend_tar, REMOTE_DIR, 'frontend')

    # Create environment file
    print('\nCreating environment file...')
    env_content = """
# CareFlow AI Production Environment
DOMAIN=careflowai.veraldabs.co.uk
APP_URL=https://careflowai.veraldabs.co.uk
API_URL=https://api.careflowai.veraldabs.co.uk
NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk
NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk

# Database
DB_PASSWORD=SecurePass2024!

# Secrets (generate these for production)
SECRET_KEY=your-secret-key-here-change-in-production
SECRET_KEY_REFRESH=your-refresh-key-here-change-in-production
ENCRYPTION_KEY=your-encryption-key-here-change-in-production

# OpenAI API Key
OPENAI_API_KEY=sk-proj-qFbjTmM7cXQjW9nCWHhgVrZ3vHYp6FhPYGLCkEqtLYM3FcPyDCKPG6wm5aJYHVAUJSy5rLK8tTkEN9f1NEkYxApMFmLn4V9fD5lPxaLJ6mEaTg0U8LPbqzA2NjZwG0=

# SMTP (configure if needed)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO

# Sentry (optional)
SENTRY_DSN=
"""
    # Upload environment file
    with sftp.file(f'{REMOTE_DIR}/.env.production', 'w') as f:
        f.write(env_content)

    print('Environment file created')

    # List uploaded files
    print('\n=== Verifying uploaded files ===')
    stdin, stdout, stderr = ssh.exec_command(f'ls -la {REMOTE_DIR}/ && echo "---" && du -sh {REMOTE_DIR}/backend {REMOTE_DIR}/frontend 2>/dev/null || echo "Source code sizes not available"')
    print(stdout.read().decode())

    sftp.close()
    ssh.close()

    print('\n' + '=' * 50)
    print('Upload complete! Ready to deploy.')
    print('Run the following to deploy:')
    print(f'ssh root@{HOST} "cd {REMOTE_DIR} && ./deploy.sh --domain=careflowai.veraldabs.co.uk"')
    print('=' * 50)

if __name__ == '__main__':
    main()
