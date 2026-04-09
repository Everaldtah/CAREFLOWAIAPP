#!/usr/bin/env python3
import paramiko
import time

HOST = '79.99.45.136'
USERNAME = 'root'
PASSWORD = 'j2nzgPFUido5D'
REMOTE_DIR = '/opt/careflow-ai-deploy'

def run_cmd(ssh, command, print_output=True):
    """Run a command on the remote server"""
    if print_output:
        print(f"\nRunning: {command[:100]}...")
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    output = ""
    for line in iter(stdout.readline, ''):
        if line:
            output += line
            if print_output:
                try:
                    print(line.rstrip())
except Exception:
                    pass
    exit_status = stdout.channel.recv_exit_status()
    return exit_status, output

def main():
    print("=" * 50)
    print("CareFlow AI - Manual Deployment")
    print("=" * 50)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USERNAME, PASSWORD, timeout=30)
    sftp = ssh.open_sftp()

    # Upload environment file
    print("\nStep 1: Creating environment file...")
    env_content = """DOMAIN=careflowai.veraldabs.co.uk
APP_URL=https://careflowai.veraldabs.co.uk
API_URL=https://api.careflowai.veraldabs.co.uk
NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk
NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk
DB_PASSWORD=SecurePass2024!
SECRET_KEY=prod-secret-key-change-this-12345678
SECRET_KEY_REFRESH=prod-refresh-key-change-this-12345678
ENCRYPTION_KEY=prod-encryption-key-change-this-12345678
OPENAI_API_KEY=sk-proj-qFbjTmM7cXQjW9nCWHhgVrZ3vHYp6FhPYGLCkEqtLYM3FcPyDCKPG6wm5aJYHVAUJSy5rLK8tTkEN9f1NEkYxApMFmLn4V9fD5lPxaLJ6mEaTg0U8LPbqzA2NjZwG0=
LOG_LEVEL=INFO
"""
    with sftp.file(f'{REMOTE_DIR}/.env', 'w') as f:
        f.write(env_content)
    print("Environment file created")

    # Check directory structure
    print("\nStep 2: Checking directory structure...")
    run_cmd(ssh, f'ls -la {REMOTE_DIR}/')
    run_cmd(ssh, f'ls -la {REMOTE_DIR}/backend/ | head -10')
    run_cmd(ssh, f'ls -la {REMOTE_DIR}/frontend/ | head -10')

    # Stop existing containers
    print("\nStep 3: Stopping existing containers...")
    run_cmd(ssh, f'cd {REMOTE_DIR} && docker-compose -f docker-compose.prod.yml down 2>/dev/null || echo "No existing containers"')

    # Build and start containers
    print("\nStep 4: Building Docker images (this may take 10+ minutes)...")
    status, _ = run_cmd(ssh, f'cd {REMOTE_DIR} && docker-compose -f docker-compose.prod.yml build --no-cache', print_output=False)

    if status != 0:
        print("Build failed! Checking logs...")
        run_cmd(ssh, f'cd {REMOTE_DIR} && docker-compose -f docker-compose.prod.yml logs backend | tail -50')
        return

    print("\nStep 5: Starting containers...")
    run_cmd(ssh, f'cd {REMOTE_DIR} && docker-compose -f docker-compose.prod.yml up -d')

    # Wait for containers to start
    print("\nWaiting 30 seconds for containers to start...")
    time.sleep(30)

    # Check status
    print("\nStep 6: Checking container status...")
    run_cmd(ssh, f'cd {REMOTE_DIR} && docker-compose -f docker-compose.prod.yml ps')

    # Check health
    print("\nStep 7: Checking backend health...")
    run_cmd(ssh, 'curl -s http://localhost:8000/health || echo "Backend not ready yet"')

    sftp.close()
    ssh.close()

    print("\n" + "=" * 50)
    print("Deployment Complete!")
    print("=" * 50)
    print(f"\nYour app should be available at:")
    print(f"  Frontend: https://careflowai.veraldabs.co.uk")
    print(f"  Backend API: https://api.careflowai.veraldabs.co.uk")
    print(f"  Health Check: https://api.careflowai.veraldabs.co.uk/health")

if __name__ == '__main__':
    main()
